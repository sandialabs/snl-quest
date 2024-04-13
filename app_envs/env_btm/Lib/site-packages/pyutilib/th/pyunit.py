#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________

__all__ = ['TestCase', 'TestResult', 'TestSuite', 'TextTestRunner', 'main',
           'nottest', 'category']

from inspect import getfile
import stat
import os
import sys
import filecmp
import re

import unittest
using_unittest2 = True
main = unittest.main

from six import iteritems, itervalues, PY2

#
# Defer the pyutilib.misc import until it is actually needed.  If we
# import it here, then PyUtilib's test coverage will report all
# "module-level" lines as uncovered because they were executed before
# the nose coverage plugin was watching things.
#
#import pyutilib.misc

if using_unittest2:
    __all__.extend(
        ['skip', 'skipIf', 'skipUnless', 'expectedFailure', 'SkipTest'])
    skip = unittest.skip
    skipIf = unittest.skipIf
    skipUnless = unittest.skipUnless
    expectedFailure = unittest.expectedFailure
    SkipTest = unittest.SkipTest
import subprocess

TextTestRunner = unittest.TextTestRunner
TestResult = unittest.TestResult
TestSuite = unittest.TestSuite

try:
    from nose.tools import nottest
except ImportError:

    def nottest(func):
        """Decorator to mark a function or method as *not* a test"""
        func.__test__ = False
        return func

def _category_to_tuple(_cat):
    _cat = str(_cat).lower().strip()
    if _cat.endswith('=0') or _cat.endswith('=1'):
        _val = int(_cat[-1])
        _cat = _cat[:-2]
    else:
        _val = 1
    if _cat and _cat[0] in '!~-':
        _val = 1 - _val
        _cat = _cat[1:]
    return _cat, _val

def category(*args, **kwargs):
    # Get the set of categories for this test
    _categories = {}
    for cat in args:
        _cat, _val = _category_to_tuple(cat)
        if not _cat:
            continue
        _categories[_cat] = _val

    # Note: we used to try and short-circuit the nosetest test selection
    # and return test skips for tests that couldn't/wouldn't be run.
    # However, this code was unreliable, as categories could be set by
    # both decorating the TestCase (class) and the function.  As a
    # result, we will just rely on nosetest to do the right thing.

    def _id(func):
        if hasattr(func, '__mro__') and TestCase in func.__mro__:
            # @category() called on a TestCase class
            if len(_categories) > (1 if 'fragile' in _categories else 0):
                for c,v in iteritems(func.unspecified_categories):
                    setattr(func, c, v)
                    _categories.setdefault(c, v)
            default_updates = {}
            for c,v in iteritems(_categories):
                if c in func.unspecified_categories:
                    default_updates[c] = v
                setattr(func, c, v)
            if default_updates:
                for fcn in itervalues(func.__dict__):
                    if hasattr(fcn, '_categories'):
                        for c,v in iteritems(default_updates):
                            if c not in fcn._categories:
                                setattr(fcn, c, v)
        else:
            # This is a (currently unbound) method definition
            if len(_categories) > (1 if 'fragile' in _categories else 0):
                for c,v in iteritems(TestCase.unspecified_categories):
                    setattr(func, c, v)
            for c,v in iteritems(_categories):
                setattr(func, c, v)
            setattr(func, '_categories', _categories)
        return func
    return _id


#@nottest
def _run_import_baseline_test(self,
                              cwd=None,
                              module=None,
                              outfile=None,
                              baseline=None,
                              filter=None,
                              tolerance=None,
                              exact=False,
                              forceskip=False):
    if forceskip:
        if forceskip is True:
            self.skipTest("A forced test skip")
        else:
            self.skipTest(str(forceskip))
    if cwd is None:
        cwd = os.path.dirname(os.path.abspath(getfile(self.__class__)))
    oldpwd = os.getcwd()
    os.chdir(cwd)
    sys.path.insert(0, cwd)
    #
    try:
        import pyutilib.misc
        pyutilib.misc.setup_redirect(outfile)
        pyutilib.misc.import_file(module + ".py", clear_cache=True)
        pyutilib.misc.reset_redirect()
        #
        if baseline.endswith('.json'):
            self.assertMatchesJsonBaseline(
                outfile, baseline, tolerance=tolerance, exact=exact)
        elif baseline.endswith('.yml'):
            self.assertMatchesYamlBaseline(
                outfile, baseline, tolerance=tolerance, exact=exact)
        elif baseline.endswith('.xml'):
            self.assertMatchesXmlBaseline(
                outfile, baseline, tolerance=tolerance, exact=exact)
        else:
            self.assertFileEqualsBaseline(
                outfile, baseline, filter=filter, tolerance=tolerance)
    finally:
        os.chdir(oldpwd)
        sys.path.remove(cwd)


#@nottest
def _run_cmd_baseline_test(self,
                           cwd=None,
                           cmd=None,
                           outfile=None,
                           baseline=None,
                           filter=None,
                           cmdfile=None,
                           tolerance=None,
                           exact=False,
                           forceskip=False):
    if forceskip:
        if forceskip is True:
            self.skipTest("A forced test skip")
        else:
            self.skipTest(str(forceskip))
    if cwd is None:
        cwd = os.path.dirname(os.path.abspath(getfile(self.__class__)))
    oldpwd = os.getcwd()
    os.chdir(cwd)
    if type(cmd) in (list, tuple):
        useShell = False
    else:
        useShell = True
        cmd = cmd.strip()


    try:
        OUTPUT = open(outfile, "w")
        proc = subprocess.Popen(
            cmd, shell=useShell, stdout=OUTPUT, stderr=subprocess.STDOUT)
        proc.wait()
        OUTPUT.close()
        if cmdfile is not None:
            OUTPUT = open(cmdfile, 'w')
            OUTPUT.write("#!/bin/sh\n")
            OUTPUT.write("# Baseline test command\n")
            OUTPUT.write("#    cwd      %s\n" % cwd)
            OUTPUT.write("#    outfile  %s\n" % outfile)
            OUTPUT.write("#    baseline %s\n" % baseline)
            OUTPUT.write(cmd + '\n')
            OUTPUT.close()
            os.chmod(cmdfile, stat.S_IREAD | stat.S_IWRITE | stat.S_IEXEC)
        if baseline.endswith('.json'):
            self.assertMatchesJsonBaseline(
                outfile, baseline, tolerance=tolerance, exact=exact)
        elif baseline.endswith('.yml'):
            self.assertMatchesYamlBaseline(
                outfile, baseline, tolerance=tolerance, exact=exact)
        elif baseline.endswith('.xml'):
            self.assertMatchesXmlBaseline(
                outfile, baseline, tolerance=tolerance, exact=exact)
        else:
            self.assertFileEqualsBaseline(
                outfile, baseline, filter=filter, tolerance=tolerance)
        if not cmdfile is None:
            os.remove(cmdfile)
    finally:
        OUTPUT.close()
        os.chdir(oldpwd)


#@nottest
def _run_fn_baseline_test(self,
                          fn=None,
                          name=None,
                          baseline=None,
                          filter=None,
                          tolerance=None):
    files = fn(name)
    self.assertFileEqualsBaseline(
        files[0], baseline, filter=filter, tolerance=tolerance)
    for file in files[1:]:
        os.remove(file)


#@nottest
def _run_fn_test(self, fn, name, suite):
    if suite is None:
        explanation = fn(self, name)
    else:
        explanation = fn(self, name, suite)
    if not explanation is None and explanation != "":
        self.fail(explanation)


class TestCase(unittest.TestCase):
    # Dictionary of options that may be used by function tests.
    _options = {}
    # A "bogus" category that we can use to check if TestCase came from
    # pyutilib or from unittest
    pyutilib_th = 1
    # The default test categories are 'smoke' and 'nightly' and 'expensive'
    smoke = 1
    nightly = 1
    expensive = 0
    fragile = 0
    _default_categories = True
    # If someone specifies a category, these are the default values of
    # the default categories if the category() decorator omits them.
    unspecified_categories = {
        'smoke':0, 'nightly':0, 'expensive':0, 'fragile':0 }

    if PY2:
        # Compatibility shim: assertRaisesRegexp was renamed to
        # assertRaisesRegex in Python 3.2
        assertRaisesRegex = unittest.TestCase.assertRaisesRegexp
        assertRegex = unittest.TestCase.assertRegexpMatches

    def __init__(self, methodName='runTest'):
        unittest.TestCase.__init__(self, methodName)

    @staticmethod
    def parse_categories(category_string):
        return tuple(
            tuple(_category_to_tuple(_cat) for _cat in _set.split(','))
            for _set in category_string.split()
        )

    @staticmethod
    def categories_to_string(categories):
        return ' '.join(','.join("%s=%s" % y for y in x) for x in categories)


    def get_options(self, name, suite=None):
        return self._options[suite, name]

    @nottest
    def recordTestData(self, name, value):
        """A method for recording data associated with a test.  This method is only
           meaningful when running this TestCase with 'nose', using the TestData plugin.
        """
        tmp = getattr(self, 'testdata', None)
        if not tmp is None:
            tmp[name] = value

    def shortDescription(self):
        # Disable nose's use of test docstrings for the test description.
        return None

    def assertMatchesXmlBaseline(self,
                                 testfile,
                                 baseline,
                                 delete=True,
                                 tolerance=0.0,
                                 exact=False):
        try:
            import pyutilib.misc
            pyutilib.misc.compare_xml_files(
                baseline, testfile, tolerance=tolerance, exact=exact)
            if delete:
                os.remove(testfile)
        except Exception:
            err = sys.exc_info()[1]
            self.fail("XML testfile does not match the baseline:\n   testfile="
                      + testfile + "\n   baseline=" + baseline + "\n" + str(
                          err))

    def assertMatchesYamlBaseline(self,
                                  testfile,
                                  baseline,
                                  delete=True,
                                  tolerance=0.0,
                                  exact=False):
        try:
            import pyutilib.misc
            pyutilib.misc.compare_yaml_files(
                baseline, testfile, tolerance=tolerance, exact=exact)
            if delete:
                os.remove(testfile)
        except Exception:
            err = sys.exc_info()[1]
            self.fail("YAML testfile does not match the baseline:\n   testfile="
                      + testfile + "\n   baseline=" + baseline + "\n" + str(
                          err))

    def assertMatchesJsonBaseline(self,
                                  testfile,
                                  baseline,
                                  delete=True,
                                  tolerance=0.0,
                                  exact=False):
        try:
            import pyutilib.misc
            pyutilib.misc.compare_json_files(
                baseline, testfile, tolerance=tolerance, exact=exact)
            if delete:
                os.remove(testfile)
        except Exception:
            err = sys.exc_info()[1]
            self.fail("JSON testfile does not match the baseline:\n   testfile="
                      + testfile + "\n   baseline=" + baseline + "\n" + str(
                          err))

    def assertFileEqualsBaseline(self,
                                 testfile,
                                 baseline,
                                 filter=None,
                                 delete=True,
                                 tolerance=None):
        import pyutilib.misc
        [flag, lineno, diffs] = pyutilib.misc.compare_file(
            testfile, baseline, filter=filter, tolerance=tolerance)
        if not flag:
            if delete:
                os.remove(testfile)
        else:  #pragma:nocover
            self.fail("Unexpected output difference at line " + str(
                lineno) + ":\n   testfile=" + testfile + "\n   baseline=" +
                      baseline + "\nDiffs:\n" + diffs)
        return [flag, lineno]

    def assertFileEqualsLargeBaseline(self, testfile, baseline, delete=True):
        import pyutilib.misc
        flag = pyutilib.misc.compare_large_file(testfile, baseline)
        if not flag:
            if delete:
                os.remove(testfile)
        else:  #pragma:nocover
            self.fail("Unexpected output difference:\n   testfile=" + testfile +
                      "\n   baseline=" + baseline)
        return flag

    def assertFileEqualsBinaryFile(self, testfile, baseline, delete=True):
        theSame = filecmp.cmp(testfile, baseline)
        if theSame:
            if delete:
                os.remove(testfile)
        else:  #pragma:nocover
            self.fail("Unexpected output difference:\n   testfile=" + testfile +
                      "\n   baseline=" + baseline)
        return theSame

    @nottest
    def add_fn_test(cls, name=None, suite=None, fn=None, options=None):
        if fn is None:
            print("ERROR: must specify the 'fn' option to define the test")
            return
        if name is None:
            print("ERROR: must specify the 'name' option to define the test")
            return
        tmp = name.replace("/", "_")
        tmp = tmp.replace("\\", "_")
        tmp = tmp.replace(".", "_")
        func = lambda self, c1=fn, c2=name, c3=suite: _run_fn_test(self, c1, c2, c3)
        func.__name__ = "test_" + str(tmp)
        func.__doc__ = "function test: "+func.__name__+ \
                       " ("+str(cls.__module__)+'.'+str(cls.__name__)+")"
        setattr(cls, "test_" + tmp, func)
        cls._options[suite, name] = options

    add_fn_test = classmethod(add_fn_test)

    @nottest
    def add_baseline_test(cls,
                          name=None,
                          cmd=None,
                          fn=None,
                          baseline=None,
                          filter=None,
                          cwd=None,
                          cmdfile=None,
                          tolerance=None,
                          outfile=None,
                          exact=False,
                          forceskip=False):
        if cmd is None and fn is None:
            print(
                "ERROR: must specify either the 'cmd' or 'fn' option to define how the output file is generated")
            return
        if name is None:
            print("ERROR: must specify the test name")
            return
        if baseline is None:
            baseline = os.path.abspath(name + ".txt")
        tmp = name.replace("/", "_")
        tmp = tmp.replace("\\", "_")
        tmp = tmp.replace(".", "_")
        if outfile is None:
            (dirname, basename) = os.path.split(baseline)
            if '.' in basename:
                outfile = os.path.join(dirname,
                                       basename.rpartition('.')[0] + '.out')
            else:
                outfile = baseline + '.out'
        #
        # Create an explicit function so we can assign it a __name__ attribute.
        # This is needed by the 'nose' package
        #
        if fn is None:
            func = lambda self,c1=cwd,c2=cmd,c3=os.path.abspath(outfile),c4=baseline,c5=filter,c6=cmdfile,c7=tolerance,c8=exact,c9=forceskip: _run_cmd_baseline_test(self,cwd=c1,cmd=c2,outfile=c3,baseline=c4,filter=c5,cmdfile=c6,tolerance=c7,exact=c8,forceskip=c9)
        else:
            func = lambda self,c1=fn,c2=name,c3=baseline,c4=filter,c5=tolerance,c6=forceskip: _run_fn_baseline_test(self,fn=c1,name=c2,baseline=c3,filter=c4,tolerance=c5,forceskip=c6)
        func.__name__ = "test_" + tmp
        func.__doc__ = "baseline test: "+func.__name__+ \
                       " ("+str(cls.__module__)+'.'+str(cls.__name__)+")"
        if fn is None and not cmdfile is None:
            func.__doc__ += "  Command archived in " + os.path.abspath(cmdfile)
        setattr(cls, "test_" + tmp, func)

    add_baseline_test = classmethod(add_baseline_test)

    @nottest
    def add_import_test(cls,
                        module=None,
                        name=None,
                        cwd=None,
                        baseline=None,
                        filter=None,
                        tolerance=None,
                        outfile=None):
        if module is None and name is None:
            print("ERROR: must specify the module that is imported")
            return
        if module is None:
            module = name
        if name is None:
            print("ERROR: must specify test name")
            return
        if baseline is None:
            baseline = name + ".txt"
        tmp = name.replace("/", "_")
        tmp = tmp.replace("\\", "_")
        tmp = tmp.replace(".", "_")
        if outfile is None:
            (dirname, basename) = os.path.split(baseline)
            if '.' in basename:
                outfile = os.path.join(dirname,
                                       basename.rpartition('.')[0] + '.out')
            else:
                outfile = baseline + '.out'
        #
        # Create an explicit function so we can assign it a __name__ attribute.
        # This is needed by the 'nose' package
        #
        func = lambda self,c1=cwd,c2=module,c3=outfile,c4=baseline,c5=filter,c6=tolerance: _run_import_baseline_test(self,cwd=c1,module=c2,outfile=c3,baseline=c4,filter=c5,tolerance=c6)
        func.__name__ = "test_" + tmp
        func.__doc__ = "import test: " + func.__name__
        setattr(cls, "test_" + tmp, func)

    add_import_test = classmethod(add_import_test)
