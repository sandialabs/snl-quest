#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________

import sys
try:
    import nose
    import nose.plugins
except ImportError:
    print("This testing utility requires the 'nose' Python testing tool")
    sys.exit(1)
try:
    import nosexunit
    import nosexunit.plugin
    nose_xunit_installed = True
except ImportError:
    nose_xunit_installed = False
try:
    import coverage
    import nose.plugins.cover
    coverage_installed = True
except ImportError:
    coverage_installed = False

import re
import logging
import os
import os.path
import glob
import copy
from optparse import OptionParser

# Ignore exceptions that occur during a logging statement
logging.raiseExceptions = 0


class UnwantedPackagePlugin(nose.plugins.Plugin):
    enabled = True
    name = "unwanted-package"

    def __init__(self, unwanted):
        self.unwanted = unwanted

    def configure(self, options, conf):
        pass

    def wantDirectory(self, dirname):
        want = None
        if os.path.basename(dirname) in self.unwanted:
            want = False
        return want


def generate_options(package, packages, subpackages, filter, options, testdir,
                     xunitdir, dirname):
    if not type(packages) is list:
        tmp = [packages]
    else:
        tmp = packages
    newargs = []
    if options.xunit:
        newargs = ['--with-xunit', '--xunit-file', xunitdir + os.sep + 'TEST-' +
                   package + '.xml']
        #if coverage_installed:
    #newargs = newargs + ['--source-folder', '.']
    if coverage_installed:
        newargs = newargs + ['--with-coverage', '--cover-erase',
                             '--cover-inclusive', '--cover-package', package]
        if options.filtering or options.filtering_all:
            for item in filter:
                newargs.append('--cover-filter=' + item)
            if len(tmp) > 0:
                for item in subpackages:
                    if not item in tmp:
                        newargs.append('--cover-filter=' + package + '.' + item)
    if options.verbose:
        newargs = newargs + ['--verbosity=3']
    newargs = newargs + ['--where', dirname]
    return newargs


def main(argv, package, subpackages, filter, testdir, dirname="test"):

    parser = OptionParser()
    parser.add_option(
        "--no-xunit",
        help="Disable generation of XUnit XML summary",
        action="store_false",
        dest="xunit",
        default=True)
    parser.add_option(
        "-v",
        "--verbose",
        help="Provide verbose output",
        action="store_true",
        dest="verbose",
        default=False)
    parser.add_option(
        "-f",
        "--filter",
        help="Enable filtering of coverage tests with a customized nose installation",
        action="store_true",
        dest="filtering",
        default=False)
    parser.add_option(
        "-F",
        "--filter-all",
        help="Apply nose to all packages, filtering each coverage test",
        action="store_true",
        dest="filtering_all",
        default=False)
    parser.usage = "runtests [options] <package> [...]"
    parser.description = "A utility to run Pyomo tests.  A particular feature of this tool is the ability to filter coverage information, using a customized installation of the nose utility."
    parser.epilog = """The customized nose utility that supports filtering can be obtained from Bill Hart (wehart@sandia.gov)."""
    #
    # Process argv list
    #
    (options, args) = parser.parse_args(args=argv)
    #
    # Preprocess arguments, to eliminate trailing '/' or '\\' characters, which a user
    # might add using tab completion.
    #
    for i in range(0, len(args)):
        if args[i][-1] == os.sep:
            args[i] = args[i][:-1]
    #
    # Verify that the arguments are valid subpackages
    #
    unwanted = copy.copy(subpackages)
    for arg in args[1:]:
        if not arg in subpackages:
            print("ERROR: no subpackage '" + arg)
            sys.exit(1)
        unwanted.remove(arg)
    if unwanted == subpackages:
        unwanted = []
    #
    # Remove coverage files from previous 'runtests' executions
    #
    coverage_file = testdir + os.sep + dirname + os.sep + ".coverage"
    if os.path.exists(coverage_file):
        os.remove(coverage_file)
    os.environ["COVERAGE_FILE"] = coverage_file
    #for file in glob.glob("*/.coverage"):
    #os.remove(file)
    #for file in glob.glob("*/*/.coverage"):
    #os.remove(file)
    #
    # Remove XML files from previous 'runtests' executions
    #
    xunitdir = testdir + os.sep + dirname + os.sep + "xunit"
    if os.path.exists(xunitdir):
        for file in glob.glob(xunitdir + os.sep + "TEST*.xml"):
            os.remove(file)
    else:
        os.mkdir(xunitdir)

    plugins = [UnwantedPackagePlugin(unwanted)]
    #if nose_xunit_installed and options.xunit:
    #plugins.append(nosexunit.plugin.NoseXUnit())
    #if coverage_installed:
    #plugins.append(nose.plugins.cover.Coverage())
    #plugins.append(nose.plugins.xunit.Xunit())
    if not options.filtering_all:
        newargs = ['runtests'] + generate_options(
            package, args[1:], subpackages, filter, options, testdir, xunitdir,
            dirname) + args[1:]
        os.chdir(testdir)
        if options.verbose:
            print("Nose Arguments:", newargs)
            print("Test Dir:", testdir)
            if len(args) > 1:
                print("Test Packages:",)
                for arg in args[1:]:
                    print(arg,)
                print("")
            if len(unwanted) > 1:
                print("Ignored Packages:", unwanted)
        sys.argv = newargs
        nose.run(argv=newargs, addplugins=plugins)
    else:
        if len(args[1:]) == 0:
            arglist = subpackages
        else:
            arglist = args[1:]
        for arg in arglist:
            newargs = ['runtests'] + generate_options(arg, options) + [arg]
            print("Package Coverage Tests: " + arg)
            tmp = sys.stdout
            os.chdir(testdir)
            if options.verbose:
                print("Nose Arguments:", newargs)
                print("Test Dir:", testdir)
                if len(args) > 1:
                    print("Test Packages:",)
                    for arg in args[1:]:
                        print(arg,)
                    print("")
                if len(unwanted) > 1:
                    print("Ignored Packages:", unwanted)
            nose.run(argv=newargs, addplugins=plugins)
            sys.stdout = tmp
    #
    # Rename xUnit files and insert the package information
    #
    if os.path.exists(xunitdir):
        p = re.compile('^.*TEST-(.+)\.xml')
        for file in glob.glob(xunitdir + os.sep + "TEST-*.xml"):
            oldname = p.match(file).group(1)
            if oldname == "test":
                suffix = ""
            else:
                suffix = "." + oldname

            FILE = open(file, "r")
            text0 = "".join(FILE.readlines())
            FILE.close()
            ptmp = re.compile("testsuite name=\"nosetests\"")
            text1 = ptmp.sub("testsuite name=\"" + package + "\"", text0)
            #ptmp = re.compile("classname=\""+oldname)
            #text2 = ptmp.sub("classname=\""+package+suffix, text1)
            #FILE = open(xunitdir+os.sep+"TEST-"+package+suffix+".xml","w")
            FILE = open(file, "w")
            FILE.write(text1)
            FILE.close()
            #os.remove(file)
