import sys
import os
from os.path import abspath, dirname
currdir = dirname(abspath(__file__)) + os.sep

import pyutilib.th as unittest
import pyutilib.services
from pyutilib.subprocess import subprocess, SubprocessMngr, timer
from pyutilib.subprocess.processmngr import _peek_available

import six

_mswindows = (sys.platform == 'win32')
try:
    import __pypy__
    is_pypy = True
except:
    is_pypy = False

pyutilib.services.register_executable("memmon")
global_memmon = pyutilib.services.registered_executable('memmon')
pyutilib.services.register_executable("valgrind")
global_valgrind = pyutilib.services.registered_executable('valgrind')


class Test(unittest.TestCase):

    def test_foo(self):
        if not _mswindows:
            foo = SubprocessMngr(
                "ls *py > /tmp/.pyutilib", stdout=subprocess.PIPE, shell=True)
            foo.wait()
            print("")
            if os.path.exists("/tmp/.pyutilib"):
                os.remove("/tmp/.pyutilib")
        else:
            foo = SubprocessMngr("cmd /C \"dir\" > C:/tmp", shell=True)
            foo.wait()
            print("")

    @unittest.skipIf(is_pypy, "Cannot launch python in this test with pypy")
    def test_timeout(self):
        targetTime = 2
        stime = timer()
        # On MS Windows, do not run this in a shell.  If so, MS Windows has difficulty
        # killing the process after the timelimit
        print("Subprocess python process")
        sys.stdout.flush()
        if ' ' in sys.executable:
            foo = SubprocessMngr(
                "'" + sys.executable + "' -q -c \"while True: pass\"",
                shell=False)
        else:
            foo = SubprocessMngr(
                sys.executable + " -q -c \"while True: pass\"",
                shell=False)
        foo.wait(targetTime)
        runTime = timer() - stime
        print("Ran for %f seconds" % (runTime,))
        #
        # timeout should be accurate to 1/10 second
        #
        self.assertTrue(runTime <= targetTime + 0.1)

    @unittest.skipIf(_mswindows,
                     "Cannot test the use of 'memmon' on MS Windows")
    @unittest.skipIf(sys.platform == 'darwin',
                     "Cannot test the use of 'memmon' on Darwin")
    @unittest.skipIf(not global_memmon,
                     "The 'memmon' executable is not available.")
    def test_memmon(self):
        pyutilib.services.register_executable('ls')
        pyutilib.subprocess.run(
            pyutilib.services.registered_executable('ls').get_path() + ' *.py',
            memmon=True,
            outfile=currdir + 'ls.out')
        INPUT = open(currdir + 'ls.out', 'r')
        flag = False
        for line in INPUT:
            flag = line.startswith('memmon:')
            if flag:
                break
        INPUT.close()
        if not flag:
            self.fail(
                "Failed to properly execute 'memmon' with the 'ls' command")
        os.remove(currdir + 'ls.out')

    @unittest.skipIf(_mswindows,
                     "Cannot test the use of 'valgrind' on MS Windows")
    @unittest.skipIf(not global_valgrind,
                     "The 'valgrind' executable is not available.")
    def test_valgrind(self):
        pyutilib.services.register_executable('ls')
        pyutilib.subprocess.run(
            pyutilib.services.registered_executable('ls').get_path() + ' *.py',
            valgrind=True,
            outfile=currdir + 'valgrind.out')
        INPUT = open(currdir + 'valgrind.out', 'r')
        flag = False
        for line in INPUT:
            flag = 'Memcheck' in line
            if flag:
                break
        INPUT.close()
        if not flag:
            self.fail(
                "Failed to properly execute 'valgrind' with the 'ls' command")
        os.remove(currdir + 'valgrind.out')

    def test_outputfile(self):
        pyutilib.subprocess.run([sys.executable, currdir + "tee_script.py"],
                                outfile=currdir + 'tee.out')
        INPUT = open(currdir + 'tee.out')
        output = INPUT.read()
        INPUT.close()
        os.remove(currdir + 'tee.out')
        if _peek_available:
            self.assertEqual(
                sorted(output.splitlines()),
                ["Tee Script: ERR", "Tee Script: OUT"])
        else:
            sys.stderr.write("BEGIN OUTPUT:\n" + output + "END OUTPUT\n")
            self.assertTrue(output.splitlines() in
                            (["Tee Script: ERR", "Tee Script: OUT"],
                             ["Tee Script: OUT", "Tee Script: ERR"]))

    def test_ostream_stringio(self):
        script_out = six.StringIO()
        output = pyutilib.subprocess.run(
            [sys.executable, currdir + "tee_script.py"], ostream=script_out)

        if _peek_available:
            self.assertEqual(
                sorted(script_out.getvalue().splitlines()),
                ["Tee Script: ERR", "Tee Script: OUT"])
        else:
            sys.stderr.write("BEGIN OUTPUT:\n" + script_out.getvalue() +
                             "END OUTPUT\n")
            self.assertTrue(script_out.getvalue().splitlines() in
                            (["Tee Script: ERR", "Tee Script: OUT"],
                             ["Tee Script: OUT", "Tee Script: ERR"]))

    @unittest.category("fragile")
    def test_tee(self):
        stream_out = six.StringIO()
        script_out = six.StringIO()
        pyutilib.misc.setup_redirect(stream_out)
        output = pyutilib.subprocess.run(
            [sys.executable, currdir + "tee_script.py"],
            ostream=script_out,
            tee=True)
        pyutilib.misc.reset_redirect()
        # The following is only deterministic if Peek/Select is available
        if _peek_available:
            self.assertEqual(
                sorted(stream_out.getvalue().splitlines()),
                ["Tee Script: ERR", "Tee Script: OUT"])
            self.assertEqual(
                sorted(script_out.getvalue().splitlines()),
                ["Tee Script: ERR", "Tee Script: OUT"])
        else:
            sys.stderr.write("BEGIN OUTPUT1:\n" + stream_out.getvalue() +
                             "END OUTPUT1\n")
            sys.stderr.write("BEGIN OUTPUT2:\n" + script_out.getvalue() +
                             "END OUTPUT2\n")
            self.assertTrue(stream_out.getvalue().splitlines() in
                            (["Tee Script: ERR", "Tee Script: OUT"],
                             ["Tee Script: OUT", "Tee Script: ERR"]))
            self.assertTrue(script_out.getvalue().splitlines() in
                            (["Tee Script: ERR", "Tee Script: OUT"],
                             ["Tee Script: OUT", "Tee Script: ERR"]))

    @unittest.category("fragile")
    def test_tee_stdout(self):
        stream_out = six.StringIO()
        script_out = six.StringIO()
        pyutilib.misc.setup_redirect(stream_out)
        output = pyutilib.subprocess.run(
            [sys.executable, currdir + "tee_script.py"],
            ostream=script_out,
            tee=(True, False))
        pyutilib.misc.reset_redirect()
        self.assertEqual(stream_out.getvalue().splitlines(),
                          ["Tee Script: OUT"])

        # The following is only deterministic if Peek/Select is available
        if _peek_available:
            self.assertEqual(
                sorted(script_out.getvalue().splitlines()),
                ["Tee Script: ERR", "Tee Script: OUT"])
        else:
            sys.stderr.write("BEGIN OUTPUT:\n" + script_out.getvalue() +
                             "END OUTPUT\n")
            self.assertTrue(script_out.getvalue().splitlines() in
                            (["Tee Script: ERR", "Tee Script: OUT"],
                             ["Tee Script: OUT", "Tee Script: ERR"]))

    @unittest.category("fragile")
    def test_tee_stderr(self):
        stream_out = six.StringIO()
        script_out = six.StringIO()
        pyutilib.misc.setup_redirect(stream_out)
        output = pyutilib.subprocess.run(
            [sys.executable, currdir + "tee_script.py"],
            ostream=script_out,
            tee=(False, True))
        pyutilib.misc.reset_redirect()
        self.assertEqual(stream_out.getvalue().splitlines(),
                          ["Tee Script: ERR"])

        # The following is only deterministic if Peek/Select is available
        if _peek_available:
            self.assertEqual(
                sorted(script_out.getvalue().splitlines()),
                ["Tee Script: ERR", "Tee Script: OUT"])
        else:
            sys.stderr.write("BEGIN OUTPUT:\n" + script_out.getvalue() +
                             "END OUTPUT\n")
            self.assertTrue(script_out.getvalue().splitlines() in
                            (["Tee Script: ERR", "Tee Script: OUT"],
                             ["Tee Script: OUT", "Tee Script: ERR"]))


if __name__ == "__main__":
    unittest.main()
