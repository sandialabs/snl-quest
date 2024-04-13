#!/usr/bin/env python

import sys
import os
from os.path import abspath, basename, dirname, exists, join
import subprocess

usage = """usage: lbin [-f][-v] <command> [...]

This script recurses up the current path, looking for 'bin' and
python/bin directories.  If found, these directories are prepended to
the PATH environment path.
    -f : [find_only] show results from 'which <command>' after PATH
         expansion but do not run <command>
    -v : [verbose] show results from 'which <command>' after PATH expansion
"""


def lbin(args):
    verbose = False
    find_only = False
    if args and args[0] in ['-v', '-f']:
        if args[0] == '-v':
            verbose = True
        elif args[0] == '-f':
            find_only = True
        args.pop(0)

        if args and args[0] in ['-v', '-f']:
            if args[0] == '-v':
                verbose = True
            elif args[0] == '-f':
                find_only = True
            args.pop(0)

    if len(args) == 0:
        print(usage)
        return 1

    try:
        # On unix, the shell's reported PWD may be different from the '.'
        # inode's absolute path (e.g., when the cwd was reached through
        # symbolic links.)  This is a trivial way to defer to the shell's
        # notion of the cwd and quietly fall back on Python's getcwd() for
        # non-unix environments.
        curr = os.environ['PWD']
    except:
        curr = abspath(os.getcwd())
    dirs = []
    while os.sep in curr:
        if exists(join(curr, "python")):
            dirs.append(join(curr, "python", "bin"))
        if exists(join(curr, "bin")):
            dirs.append(join(curr, "bin"))
        if basename(curr) == "":
            break
        curr = dirname(curr)

    dirs.append(os.environ["PATH"])
    os.environ["PATH"] = os.pathsep.join(dirs)
    #print os.environ["PATH"]
    try:
        if find_only:
            if verbose:
                return subprocess.call(['which', '-a', args[0]])
            else:
                return subprocess.call(['which', args[0]])
        if verbose:
            print("Path search found the following instances of %s:" % args[0])
            x = subprocess.call(['which', args[0]])
            print("")
        os.execvp(args[0], args)
        #return subprocess.call(args)
    except OSError:
        err = sys.exc_info()[1]
        print("ERROR executing command '%s': %s" % (' '.join(args), str(err)))
        return err.errno


    # The [console_scripts] entry point requires a function that takes no
    # arguments
def main():
    sys.exit(lbin(sys.argv[1:]))


if __name__ == '__main__':
    main()
