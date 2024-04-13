#!/usr/bin/env python
#
# This script searches for a local python installation, which is
# applied, rather than the python executable on the user's path.
#
# Additionally, this script sets the PATH environmental variable to
# point to the acro/bin directory.
#

import os
from os.path import abspath, basename, dirname, exists, join
import sys
import signal


def lpython(args):
    sys.tracebacklimit = 0
    process = None

    def signal_handler(signum, frame):
        if not process is None:
            if sys.platform == "win32":
                # On Windows this calls the Win32 API function TerminateProcess()
                process.terminate()
            else:
                process.send_signal(signal.SIGTERM)
        sys.exit(-signum)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGHUP, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    #
    # Recurse up the current path, looking for a subdirectory that
    # contains 'python/bin/python'
    #
    pexec = None
    try:
        # On unix, the shell's reported PWD may be different from the '.'
        # inode's absolute path (e.g., when the cwd was reached through
        # symbolic links.)  This is a trivial way to defer to the shell's
        # notion of the cwd and quietly fall back on Python's getcwd() for
        # non-unix environments.
        curr = os.environ['PWD']
    except:
        curr = abspath(os.getcwd())
    while os.sep in curr:
        if exists(join(curr, "python", "bin", "python")):
            pexec = join(curr, "python", "bin", "python")
            os.environ["PATH"] = join(curr,
                                      "bin") + os.pathsep + os.environ["PATH"]
            break
        if exists(join(curr, "python", "bin", "python.exe")):
            pexec = join(curr, "python", "bin", "python.exe")
            os.environ["PATH"] = join(curr,
                                      "bin") + os.pathsep + os.environ["PATH"]
            break
        if exists(join(curr, "bin", "python")):
            pexec = join(curr, "bin", "python")
            break
        if exists(join(curr, "bin", "python.exe")):
            pexec = join(curr, "bin", "python.exe")
            break
        if basename(curr) == "":
            break
        curr = dirname(curr)

    if pexec is None:
        pexec = 'python'
    os.execvp(pexec, [pexec] + args)

    #try:
    #    import subprocess
    #    process = subprocess.Popen(args)
    #    process.wait()
    #    return process.returncode
    #
    #except ImportError:
    #    #
    #    # For Python 2.3
    #    #
    #    if pexec is None:
    #        returncode = os.system(" ".join(["python"]+args))
    #    else:
    #        returncode = os.system(" ".join([pexec]+args))
    #    return returncode


# The [console_scripts] entry point requires a function that takes no
# arguments
def main():
    sys.exit(lpython(sys.argv[1:]))

if __name__ == '__main__':
    main()
