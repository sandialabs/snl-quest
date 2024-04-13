#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________

__all__ = ['subprocess', 'SubprocessMngr', 'run_command', 'timer',
           'signal_handler', 'run', 'PIPE', 'STDOUT']

from pyutilib.subprocess import GlobalData
import time
import signal
import os
import sys
import tempfile
import subprocess
from six import itervalues
from threading import Thread

_mswindows = sys.platform.startswith('win')

if _mswindows:
    import ctypes

# Note: on many python interpreters, WindowsError is only defined on
# Windows.  Since we want to trap it below, we will declare a local
# Exception type that is WindowsError if WindowsError is defined,
# otherwise it is a bogus Exception class.
try:
    WindowsError()
    _WindowsError = WindowsError
except NameError:

    class _WindowsError(Exception):
        pass


_peek_available = True
try:
    if _mswindows:
        from msvcrt import get_osfhandle
        from win32pipe import PeekNamedPipe
        from win32file import ReadFile
    else:
        from select import select
except:
    _peek_available = False

import pyutilib.services
from pyutilib.common import ApplicationError
from pyutilib.misc import quote_split

try:
    unicode
except:
    basestring = unicode = str

if sys.platform.startswith('java'):
    PIPE = None
    STDOUT = None
else:
    PIPE = subprocess.PIPE
    STDOUT = subprocess.STDOUT

if sys.version_info[0:2] >= (3, 0):

    def bytes_cast(x):
        if not x is None:
            if isinstance(x, basestring) is True:
                return x.encode()  # Encode string to bytes type
            else:
                # lets assume its of type bytes
                return x
        else:
            return x
else:
    bytes_cast = lambda x: x  # Do nothing

#
# Setup the timer
#
if sys.version_info >= (3,3):
    # perf_counter is guaranteed to be monotonic and the most accurate timer
    timer = time.perf_counter
else:
    # On old Pythons, clock() is more accurate than time() on Windows
    # (.35us vs 15ms), but time() is more accurate than clock() on Linux
    # (1ns vs 1us).  However, since we are only worring about process
    # timeouts here, we will stick with strictly monotonic timers
    timer = time.clock


def kill_process(process, sig=signal.SIGTERM, verbose=False):
    """
    Kill a process given a process ID
    """
    pid = process.pid
    if GlobalData.debug or verbose:
        print("Killing process %d with signal %d" % (pid, sig))
    if _mswindows:
        PROCESS_TERMINATE = 1
        handle = ctypes.windll.kernel32.OpenProcess(PROCESS_TERMINATE,
                                                    False, pid)
        ctypes.windll.kernel32.TerminateProcess(handle, -1)
        ctypes.windll.kernel32.CloseHandle(handle)
    else:
        #
        # Kill process and all its children
        #
        pgid = os.getpgid(pid)
        if pgid == -1:
            print("  ERROR: invalid pid %d" % pid)
            sys.exit(1)
        os.killpg(pgid, signal.SIGTERM)
        process.terminate()
        #
        # This is a hack.  The Popen.__del__ method references
        # the 'os' package, and when a process is interupted this
        # package is deleted before Popen.  I can't figure out why
        # _del_ is being called when Python closes down, though.  HOWEVER,
        # we can hard-ware Popen.__del__ to return immediately by telling it
        # that it did not create a child process!
        #
        if not GlobalData.current_process is None:
            GlobalData.current_process._child_created = False


GlobalData.current_process = None
GlobalData.pid = None
GlobalData.signal_handler_busy = False


#
# A signal handler that passes on the signal to the child process.
#
def verbose_signal_handler(signum, frame):
    c = frame.f_code
    print('  Signal handler called from ', c.co_filename, c.co_name,
          frame.f_lineno)
    print("  Waiting...",)
    signal_handler(signum, frame, True)


def signal_handler(signum, frame, verbose=False):
    if GlobalData.signal_handler_busy:
        print("")
        print("  Signal handler is busy.  Aborting.")
        sys.exit(-signum)
    if GlobalData.current_process is None:
        print("  Signal", signum, "recieved, but no process queued")
        print("  Exiting now")
        sys.exit(-signum)
    if GlobalData.current_process is not None and\
       GlobalData.current_process.pid is not None and\
       GlobalData.current_process.poll() is None:
        GlobalData.signal_handler_busy = True
        kill_process(GlobalData.current_process, signum)
        if verbose:
            print("  Signaled process", GlobalData.current_process.pid,
                  "with signal", signum)
        endtime = timer() + 1.0
        while timer() < endtime:
            status = GlobalData.current_process.poll()
            if status is None:
                break
            time.sleep(0.1)
        #GlobalData.current_process.wait()
        status = GlobalData.current_process.poll()
        if status is not None:
            GlobalData.signal_handler_busy = False
            if verbose:
                print("Done.")
            raise OSError("Interrupted by signal " + repr(signum))
        else:
            raise OSError("Problem terminating process" + repr(
                GlobalData.current_process.pid))
        GlobalData.current_process = None

    # Restore the original signal handlers (because the subprocess is
    # now defunct, and we shouldn't return here)
    for _sig in list(GlobalData.original_signal_handlers):
        signal.signal(_sig, GlobalData.original_signal_handlers.pop(_sig))
    # If there was originally a signal handler, then we should trigger
    # it, too
    orig_handler = signal.getsignal(signum)
    if hasattr(orig_handler, '__call__'):
        orig_handler(signum, frame)
    raise OSError("Interrupted by signal " + repr(signum))


#
# A function used to read in data from a shell command, and push it into a pipe.
#
def _stream_reader(args):
    unbuffer = args[0]
    stream = args[1]
    output = tuple(x for x in args[2:] if x is not None)

    def write(x):
        success = True
        for s in output:
            try:
                s.write(x)
            except ValueError:
                success = False
        return success

    def flush():
        for s in output:
            try:
                s.flush()
            except ValueError:
                pass

    raw_stderr = sys.__stderr__
    if raw_stderr is None:
        raw_stderr = sys.stderr
    try:
        encoding = stream.encoding
    except:
        encoding = None
    if encoding is None:
        try:
            encoding = raw_stderr.encoding
        except:
            pass
    if encoding is None:
        encoding = 'utf-8'

    buf = ""
    data = None

    while True:
        new_data = os.read(stream, 1)
        if not new_data:
            break
        if data:
            data += new_data
        else:
            data = new_data
        char = data.decode(encoding)
        if char.encode(encoding) != data:
            continue
        data = ""
        if unbuffer == 1:
            writeOK = write(char)
        buf += char
        if char[-1] != "\n":
            continue
        if unbuffer:
            if unbuffer != 1:
                writeOK = write(buf)
            flush()
        else:
            writeOK = write(buf)
        if writeOK:
            buf = ""
    writeOK = True
    if buf:
        writeOK &= write(buf)
    if data:
        writeOK &= write(data.decode(encoding))
    flush()
    if not writeOK and raw_stderr is not None:
        raw_stderr.write("""
ERROR: pyutilib.subprocess: output stream closed before all subprocess output
       was written to it.  The following was left in the subprocess buffer:
            '%s'
""" % (buf,))
        if data:
            raw_stderr.write(
                """The following undecoded unicode output was also present:
            '%s'
""" % (data,))


#
# A function used to read in data from two independent streams and push
# each to 1+ output pipes.  Managing this in a single thread allows our
# code output to be more predictible (and better formatted) when the
# output streams happen to point to the same place (e.g., file or
# terminal).  This function requires the ability to "peek" or "select"
# the next stream that is ready to be read from.
#
# For platforms that do not support select / peek, see the
# _pseudo_merged_reader.
#
def _merged_reader(*args):

    class StreamData(object):
        __slots__ = ('read', 'output', 'unbuffer', 'buf', 'data')

        def __init__(self, *args):
            if _mswindows:
                self.read = get_osfhandle(args[1])
            else:
                self.read = args[1]
            self.unbuffer = args[0]
            self.output = tuple(x for x in args[2:] if x is not None)
            self.buf = ""
            self.data = None

        def write(self, x):
            success = True
            for s in self.output:
                try:
                    s.write(x)
                except ValueError:
                    success = False
            return success

        def flush(self):
            for s in self.output:
                try:
                    s.flush()
                except ValueError:
                    pass

    raw_stderr = sys.__stderr__
    if raw_stderr is None:
        # There are cases, e.g., in Anaconda, where there is no stdout
        # for the original process because, for example, it was started
        # in a windowing environment.
        raw_stderr = sys.stderr
    try:
        encoding = stream.encoding
    except:
        encoding = None
    if encoding is None:
        try:
            encoding = raw_stderr.encoding
        except:
            pass
    if encoding is None:
        encoding = 'utf-8'

    streams = {}
    for s in args:
        tmp = StreamData(*s)
        streams[tmp.read] = tmp

    handles = sorted(streams.keys(), key=lambda x: -1 * streams[x].unbuffer)
    noop = []

    while handles:
        if _mswindows:
            new_data = None
            for h in handles:
                try:
                    numAvail = PeekNamedPipe(h, 0)[1]
                    if numAvail == 0:
                        continue
                    result, new_data = ReadFile(h, 1, None)
                except:
                    handles.remove(h)
                    new_data = None
            if new_data is None:
                continue
        else:
            h = select(handles, noop, noop)[0]
            if not h:
                break
            h = h[0]
            new_data = os.read(h, 1)
            if not new_data:
                handles.remove(h)
                continue
        s = streams[h]
        if s.data is None:
            s.data = new_data
        else:
            s.data += new_data
        char = s.data.decode(encoding)
        if char.encode(encoding) != s.data:
            continue
        s.data = None
        if s.unbuffer:
            writeOK = s.write(char)
        s.buf += char
        if char[-1] != "\n":
            continue
        if s.unbuffer:
            s.flush()
        else:
            writeOK = s.write(s.buf)
        if writeOK:
            s.buf = ""
    writeOK = True
    for s in itervalues(streams):
        if s.buf:
            writeOK &= s.write(s.buf)
        if s.data:
            writeOK &= s.write(s.data.decode(encoding))
        s.flush()
    if not writeOK and raw_stderr is not None:
        raw_stderr.write("""
ERROR: pyutilib.subprocess: output stream closed before all subprocess output
       was written to it.  The following was left in the subprocess buffer:
            '%s'
""" % (buf,))
        if data:
            raw_stderr.write(
                """The following undecoded unicode output was also present:
            '%s'
""" % (data,))


#
# A mock-up of the _merged_reader for platforms (or installations) that
# lack working select/peek implementations.  Note that this function
# does not guarantee determinism (and on many platforms is exceedingly
# nondeterministic).  However, it does change the flushing rules to
# better maintain output line integrity (at the cost of performance).
#
def _pseudo_merged_reader(*args):
    _threads = []
    for arg in args:
        _threads.append(Thread(target=_stream_reader, args=((2,) + arg[1:],)))
        _threads[-1].daemon = True
        _threads[-1].start()
    for th in _threads:
        th.join()


#
# Execute the command as a subprocess that we can send signals to.
# After this is finished, we can get the output from this command from
# the process.stdout file descriptor.
#
def run_command(cmd,
                outfile=None,
                cwd=None,
                ostream=None,
                stdin=None,
                stdout=None,
                stderr=None,
                valgrind=False,
                valgrind_log=None,
                valgrind_options=None,
                memmon=False,
                env=None,
                define_signal_handlers=None,
                debug=False,
                verbose=True,
                timelimit=None,
                tee=None,
                ignore_output=False,
                shell=False,
                thread_reader=None):
    #
    # Set the define_signal_handlers based on the global default flag.
    #
    if define_signal_handlers is None:
        define_signal_handlers = GlobalData.DEFINE_SIGNAL_HANDLERS_DEFAULT
    #
    # Move to the specified working directory
    #
    if cwd is not None:
        oldpwd = os.getcwd()
        os.chdir(cwd)

    cmd_type = type(cmd)
    if cmd_type is list:
        # make a private copy of the list
        _cmd = cmd[:]
    elif cmd_type is tuple:
        _cmd = list(cmd)
    else:
        _cmd = quote_split(cmd.strip())

    #
    # Setup memmoon
    #
    if memmon:
        memmon = pyutilib.services.registered_executable("memmon")
        if memmon is None:
            raise IOError("Unable to find the 'memmon' executable")
        _cmd.insert(0, memmon.get_path())
    #
    # Setup valgrind
    #
    if valgrind:
        #
        # The valgrind_log option specifies a logfile that is used to store
        # valgrind output.
        #
        valgrind_cmd = pyutilib.services.registered_executable("valgrind")
        if valgrind_cmd is None:
            raise IOError("Unable to find the 'valgrind' executable")
        valgrind_cmd = [valgrind_cmd.get_path()]
        if valgrind_options is None:
            valgrind_cmd.extend(
                ("-v", "--tool=memcheck", "--trace-children=yes"))
        elif type(valgrind_options) in (list, tuple):
            valgrind_cmd.extend(valgrind_options)
        else:
            valgrind_cmd.extend(quote_split(valgrind_options.strip()))
        if valgrind_log is not None:
            valgrind_cmd.append("--log-file-exactly=" + valgrind_log.strip())
        _cmd = valgrind_cmd + _cmd
    #
    # Redirect stdout and stderr
    #
    tmpfile = None
    if ostream is not None:
        stdout_arg = stderr_arg = ostream
        if outfile is not None or stdout is not None or stderr is not None:
            raise ValueError("subprocess.run_command(): ostream, outfile, and "
                             "{stdout, stderr} options are mutually exclusive")
        output = "Output printed to specified ostream"
    elif outfile is not None:
        stdout_arg = stderr_arg = open(outfile, "w")
        if stdout is not None or stderr is not None:
            raise ValueError("subprocess.run_command(): outfile and "
                             "{stdout, stderr} options are mutually exclusive")
        output = "Output printed to file '%s'" % outfile
    elif not (stdout is None and stderr is None):
        stdout_arg = stdout
        stderr_arg = stderr
        output = "Output printed to specified stdout and stderr streams"
    else:
        # Create a temporary file.  The mode is w+, which means that we
        #   can read and write.
        # NOTE: the default mode is w+b, but writing to the binary mode
        #   seems to cause problems in the _stream_reader function on Python
        #   3.x.
        stdout_arg = stderr_arg = tmpfile = tempfile.TemporaryFile(mode='w+')
        output = ""

    if stdout_arg is stderr_arg:
        try:
            if not tee or (not tee[0] and not tee[1]):
                stderr_arg = STDOUT
        except:
            pass

    #
    # Setup the default environment
    #
    if env is None:
        env = os.environ.copy()
    #
    # Setup signal handler
    #
    if define_signal_handlers:
        handler = verbose_signal_handler if verbose else signal_handler
        if sys.platform[0:3] != "win" and sys.platform[0:4] != 'java':
            GlobalData.original_signal_handlers[signal.SIGHUP] \
                = signal.signal(signal.SIGHUP, handler)
        GlobalData.original_signal_handlers[signal.SIGINT] \
            = signal.signal(signal.SIGINT, handler)
        GlobalData.original_signal_handlers[signal.SIGTERM] \
            = signal.signal(signal.SIGTERM, handler)
    rc = -1
    if debug:
        print("Executing command %s" % (_cmd,))
    try:
        try:
            simpleCase = not tee
            if stdout_arg is not None:
                stdout_arg.fileno()
            if stderr_arg is not None:
                stderr_arg.fileno()
        except:
            simpleCase = False

        out_th = []
        th = None
        GlobalData.signal_handler_busy = False
        if simpleCase:
            #
            # Redirect IO to the stdout_arg/stderr_arg files
            #
            process = SubprocessMngr(
                _cmd,
                stdin=stdin,
                stdout=stdout_arg,
                stderr=stderr_arg,
                env=env,
                shell=shell)
            GlobalData.current_process = process.process
            rc = process.wait(timelimit)
            GlobalData.current_process = None
        else:
            #
            # Aggressively wait for output from the process, and
            # send this to both the stdout/stdarg value, as well
            # as doing a normal 'print'
            #
            out_fd = []
            for fid in (0, 1):
                if fid == 0:
                    s, raw = stdout_arg, sys.stdout
                else:
                    s, raw = stderr_arg, sys.stderr
                try:
                    tee_fid = tee[fid]
                except:
                    tee_fid = tee
                if s is None or s is STDOUT:
                    out_fd.append(s)
                elif not tee_fid:
                    # This catches using StringIO as an output buffer:
                    # Python's subprocess requires the stream objects to
                    # have a "fileno()" attribute, which StringIO does
                    # not have.  We will mock things up by putting a
                    # pipe in between the subprocess and the StringIO
                    # buffer.  <sigh>
                    #
                    #if hasattr(s, 'fileno'):
                    #
                    # Update: in Python 3, StringIO declares a fileno()
                    # method, but that method throws an exception.  So,
                    # we can't just check for the attribute: we *must*
                    # call the method and see if we get an exception.
                    try:
                        s.fileno()
                        out_fd.append(s)
                    except:
                        r, w = os.pipe()
                        out_fd.append(w)
                        out_th.append(((fid, r, s), r, w))
                        #th = Thread(target=thread_reader, args=(r,None,s,fid))
                        #out_th.append((th, r, w))
                else:
                    r, w = os.pipe()
                    out_fd.append(w)
                    out_th.append(((fid, r, raw, s), r, w))
                    #th = Thread( target=thread_reader, args=(r,raw,s,fid) )
                    #out_th.append((th, r, w))
                #
            process = SubprocessMngr(
                _cmd,
                stdin=stdin,
                stdout=out_fd[0],
                stderr=out_fd[1],
                env=env,
                shell=shell)
            GlobalData.current_process = process.process
            GlobalData.signal_handler_busy = False
            #
            # Create a thread to read in stdout and stderr data
            #
            if out_th:
                if thread_reader is not None:
                    reader = thread_reader
                elif len(out_th) == 1:
                    reader = _stream_reader
                elif _peek_available:
                    reader = _merged_reader
                else:
                    reader = _pseudo_merged_reader
                th = Thread(target=reader, args=[x[0] for x in out_th])
                th.daemon = True
                th.start()
            #
            # Wait for process to finish
            #
            rc = process.wait(timelimit)
            GlobalData.current_process = None
            out_fd = None

    except _WindowsError:
        err = sys.exc_info()[1]
        raise ApplicationError(
            "Could not execute the command: '%s'\n\tError message: %s" %
            (' '.join(_cmd), err))
    except OSError:
        #
        # Ignore IOErrors, which are caused by interupts
        #
        pass
    finally:
        # restore the previous signal handlers, if necessary
        for _sig in list(GlobalData.original_signal_handlers):
            signal.signal(_sig, GlobalData.original_signal_handlers.pop(_sig))

    #
    # Flush stdout/stderr. Some platforms (notably Matlab, which
    # replaces stdout with a MexPrinter) have stdout/stderr that do not
    # implement flush()  See https://github.com/Pyomo/pyomo/issues/156
    #
    try:
        sys.stdout.flush()
    except AttributeError:
        pass
    try:
        sys.stderr.flush()
    except AttributeError:
        pass

    if out_th:
        #
        # 'Closing' the PIPE to send EOF to the reader.
        #
        for p in out_th:
            os.close(p[2])
        if th is not None:
            # Note, there is a condition where the subprocess can die
            # very quickly (raising an OSError) before the reader
            # threads have a chance to be set up.  Testing for None
            # avoids joining a thread that doesn't exist.
            th.join()
        for p in out_th:
            os.close(p[1])
        if th is not None:
            del th
    if outfile is not None:
        stdout_arg.close()
    elif tmpfile is not None and not ignore_output:
        tmpfile.seek(0)
        output = "".join(tmpfile.readlines())
        tmpfile.close()
    #
    # Move back from the specified working directory
    #
    if cwd is not None:
        os.chdir(oldpwd)
    #
    # Return the output
    #
    return [rc, output]

# Create an alias for run_command
run = run_command


class SubprocessMngr(object):

    def __init__(self,
                 cmd,
                 stdin=None,
                 stdout=None,
                 stderr=None,
                 env=None,
                 bufsize=0,
                 shell=False):
        """
        Setup and launch a subprocess
        """
        self.process = None
        #
        # By default, stderr is mapped to stdout
        #
        #if stderr is None:
        #    stderr=subprocess.STDOUT

        self.stdin = stdin
        if stdin is None:
            stdin_arg = None
        else:
            stdin_arg = subprocess.PIPE
        #
        # We would *really* like to deal with commands in execve form
        #
        if type(cmd) not in (list, tuple):
            cmd = quote_split(cmd.strip())
        #
        # Launch subprocess using a subprocess.Popen object
        #
        if _mswindows:
            #
            # Launch without console on MSWindows
            #
            startupinfo = subprocess.STARTUPINFO()
            #startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            self.process = subprocess.Popen(
                cmd,
                stdin=stdin_arg,
                stdout=stdout,
                stderr=stderr,
                startupinfo=startupinfo,
                env=env,
                bufsize=bufsize,
                shell=shell)
        elif getattr(subprocess, 'jython', False):
            #
            # Launch from Jython
            #
            self.process = subprocess.Popen(
                cmd,
                stdin=stdin_arg,
                stdout=stdout,
                stderr=stderr,
                env=env,
                bufsize=bufsize,
                shell=shell)
        else:
            #
            # Launch on *nix
            #
            self.process = subprocess.Popen(
                cmd,
                stdin=stdin_arg,
                stdout=stdout,
                stderr=stderr,
                preexec_fn=os.setsid,
                env=env,
                bufsize=bufsize,
                shell=shell)

    def X__del__(self):
        """
        Cleanup temporary file descriptor and delete that file.
        """

        if False and self.process is not None:
            try:
                if self.process.poll() is None:
                    self.kill()
            except OSError:
                #
                # It should be OK to ignore this exception.  Although poll() returns
                # None when the process is still active, there is a race condition
                # here.  Between running poll() and running kill() the process
                # may have terminated.
                #
                pass
        if self.process is not None:
            try:
                del self.process
            except:
                pass
        self.process = None

    def wait(self, timelimit=None):
        """
        Wait for the subprocess to terminate.  Terminate if a specified
        timelimit has passed.
        """
        if timelimit is None:
            # *Py3k: bytes_cast does no conversion for python 2.*, casts to bytes for 3.*
            self.process.communicate(input=bytes_cast(self.stdin))
            return self.process.returncode
        else:
            #
            # Wait timelimit seconds and then force a termination
            #
            # Sleep every 1/10th of a second to avoid wasting CPU time
            #
            if timelimit <= 0:
                raise ValueError("'timeout' must be a positive number")
            endtime = timer() + timelimit

            # This might be dangerous: we *could* deadlock if the input
            # is large...
            if self.stdin is not None:
                # *Py3k: bytes_cast does no conversion for python 2.*, casts to bytes for 3.*
                self.process.stdin.write(bytes_cast(self.stdin))

            while timer() < endtime:
                status = self.process.poll()
                if status is not None:
                    return status
                time.sleep(0.1)
            #
            # Check one last time before killing the process
            #
            status = self.process.poll()
            if status is not None:
                return status
            #
            # If we're here, then kill the process and return an error
            # returncode.
            #
            try:
                self.kill()
                return -1
            except OSError:
                #
                # The process may have stopped before we called 'kill()'
                # so check the status one last time.
                #
                status = self.process.poll()
                if status is not None:
                    return status
                else:
                    raise OSError("Could not kill process " + repr(
                        self.process.pid))

    def stdout(self):
        return self.process.stdout

    def send_signal(self, sig):
        """
        Send a signal to a subprocess
        """
        os.signal(self.process, sig)

    def kill(self, sig=signal.SIGTERM):
        """
        Kill the subprocess and its children
        """
        kill_process(self.process, sig)
        self.process.terminate()
        self.process.wait()
        del self.process
        self.process = None


if __name__ == "__main__":  #pragma:nocover
    #GlobalData.debug=True
    print("Z")
    stime = timer()
    foo = run_command("./dummy", tee=True, timelimit=10)
    print("A")
    print("Ran for " + repr(timer() - stime) + " seconds")
    print(foo)
    sys.exit(0)

    if not _mswindows:
        foo = SubprocessMngr("ls *py")
        foo.wait()
        print("")

        foo = SubprocessMngr("ls *py", stdout=subprocess.PIPE)
        foo.wait()
        for line in foo.process.stdout:
            print(line,)
        print("")
        foo = None

        [rc, output] = run_command("ls *py")
        print(output)
        print("")

        [rc, output] = run_command("ls *py", outfile="tmp")
        INPUT = open("tmp", 'r')
        for line in INPUT:
            print(line,)
        INPUT.close()
        print("")

        print("X")
        [rc, output] = run_command(
            "python -c \"while True: print '.'\"", timelimit=2)
        print("Y")
        #[rc,output] = run_command("python -c \"while True: print '.'\"")
        [rc, output] = run_command(
            "python -c \"while True: print '.'\"", verbose=False)
        print("Y-end")
    else:
        foo = SubprocessMngr("cmd /C \"dir\"")
        foo.wait()
        print("")

    print("Z")
    stime = timer()
    foo = run_command("python -c \"while True: pass\"", timelimit=10)
    print("A")
    print("Ran for " + repr(timer() - stime) + " seconds")

pyutilib.services.register_executable("valgrind")
pyutilib.services.register_executable("memmon")
