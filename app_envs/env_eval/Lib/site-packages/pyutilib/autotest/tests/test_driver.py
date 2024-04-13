#
# Unit Tests for pyutilib.autotest
#
#

import os
import sys
from os.path import abspath, dirname, join
currdir = dirname(abspath(__file__)) + os.sep

import pyutilib.th as unittest
from pyutilib.misc import setup_redirect, reset_redirect
import pyutilib.autotest
import pyutilib.subprocess
from pyutilib.dev.entry_point import run_entry_point

try:
    import yaml
    yaml_available = True
except ImportError:
    yaml_available = False
try:
    import json
    json_available = True
except ImportError:
    json_available = False


def filter(str):
    return 'currdir' in str or \
           'Ran' in str or \
           'UserWarning' in str


def filter_t1(str):
    return 'options' in str or \
           'Options' in str or \
           'usage' in str or \
           'Usage' in str


class TestYaml(pyutilib.th.TestCase):

    def setUp(self):
        if sys.platform.startswith('java'):
            self.skipTest("Skipping tests because running in Jython")
        self.t1 = os.environ.get('PYUTILIB_AUTOTEST_CATEGORIES', None)
        self.t2 = os.environ.get('PYUTILIB_UNITTEST_CATEGORIES', None)
        if not self.t1 is None:
            del os.environ['PYUTILIB_AUTOTEST_CATEGORIES']
        if not self.t2 is None:
            del os.environ['PYUTILIB_UNITTEST_CATEGORIES']

    def driver(self, *args):
        tmp = ['autotest']
        tmp += list(args)
        pyutilib.autotest.run(tmp, {})

    def tearDown(self):
        if not self.t1 is None:
            os.environ['PYUTILIB_AUTOTEST_CATEGORIES'] = self.t1
        if not self.t2 is None:
            os.environ['PYUTILIB_UNITTEST_CATEGORIES'] = self.t2

    def test1(self):
        # run --help
        setup_redirect(currdir + 'test1.out')
        self.driver('--help')
        reset_redirect()
        self.assertFileEqualsBaseline(
            currdir + 'test1.out', currdir + 'test1.txt', filter=filter_t1)

    def test2(self):
        # run --help-suites example1.yml
        setup_redirect(currdir + 'test2.out')
        self.driver('--help-suites', currdir + 'example1.yml')
        reset_redirect()
        self.assertFileEqualsBaseline(currdir + 'test2.out',
                                      currdir + 'test2.txt')

    def test3(self):
        # run --help-categories example1.yml
        setup_redirect(currdir + 'test3.out')
        self.driver('--help-categories', currdir + 'example1.yml')
        reset_redirect()
        self.assertFileEqualsBaseline(currdir + 'test3.out',
                                      currdir + 'test3.txt')

    def test4(self):
        # run --help-tests suite1 example1.yml
        setup_redirect(currdir + 'test4.out')
        self.driver('--help-tests', 'suite1', currdir + 'example1.yml')
        reset_redirect()
        self.assertFileEqualsBaseline(currdir + 'test4.out',
                                      currdir + 'test4.txt')

    def test5(self):
        # run example1.yml
        run_entry_point('PyUtilib','pyutilib_test_driver',
                        [join(currdir,'example1.yml')],
                        outfile=join(currdir,'test5.out'))
        self.assertFileEqualsBaseline(
            currdir + 'test5.out', currdir + 'test5.txt', filter=filter)

    def test6(self):
        # run --cat x_suite2 --cat x_suite1 example1.yml
        run_entry_point('PyUtilib', 'pyutilib_test_driver',
                        [ '--cat', 'x_suite2', '--cat', 'x_suite1',
                          join(currdir,'example1.yml') ],
                        outfile=join(currdir,'test6.out'))
        self.assertFileEqualsBaseline(
            currdir + 'test6.out', currdir + 'test6.txt', filter=filter)


class TestJson(pyutilib.th.TestCase):

    def setUp(self):
        if sys.platform.startswith('java'):
            self.skipTest("Skipping tests because running in Jython")
        if not json_available:
            self.skipTest("Skipping tests because JSON is not available")
        self.t1 = os.environ.get('PYUTILIB_AUTOTEST_CATEGORIES', None)
        self.t2 = os.environ.get('PYUTILIB_UNITTEST_CATEGORIES', None)
        if not self.t1 is None:
            del os.environ['PYUTILIB_AUTOTEST_CATEGORIES']
        if not self.t2 is None:
            del os.environ['PYUTILIB_UNITTEST_CATEGORIES']

    def driver(self, *args):
        tmp = ['autotest']
        tmp += list(args)
        pyutilib.autotest.run(tmp, {})

    def tearDown(self):
        if not self.t1 is None:
            os.environ['PYUTILIB_AUTOTEST_CATEGORIES'] = self.t1
        if not self.t2 is None:
            os.environ['PYUTILIB_UNITTEST_CATEGORIES'] = self.t2

    def test1(self):
        # run --help
        setup_redirect(currdir + 'test1.out')
        self.driver('--help')
        reset_redirect()
        self.assertFileEqualsBaseline(
            currdir + 'test1.out', currdir + 'test1.txt', filter=filter_t1)

    def test2(self):
        # run --help-suites example1.json
        setup_redirect(currdir + 'test2.out')
        self.driver('--help-suites', currdir + 'example1.json')
        reset_redirect()
        self.assertFileEqualsBaseline(currdir + 'test2.out',
                                      currdir + 'test2.txt')

    def test3(self):
        # run --help-categories example1.json
        setup_redirect(currdir + 'test3.out')
        self.driver('--help-categories', currdir + 'example1.json')
        reset_redirect()
        self.assertFileEqualsBaseline(currdir + 'test3.out',
                                      currdir + 'test3.txt')

    def test4(self):
        # run --help-tests suite1 example1.json
        setup_redirect(currdir + 'test4.out')
        self.driver('--help-tests', 'suite1', currdir + 'example1.json')
        reset_redirect()
        self.assertFileEqualsBaseline(currdir + 'test4.out',
                                      currdir + 'test4.txt')

    def test5(self):
        # run example1.json
        run_entry_point('PyUtilib','pyutilib_test_driver',
                        [join(currdir,'example1.json')],
                        outfile=join(currdir,'test5.out'))
        self.assertFileEqualsBaseline(
            currdir + 'test5.out', currdir + 'test5.txt', filter=filter)

    def test6(self):
        # run --cat x_suite2 --cat x_suite1 example1.json
        run_entry_point('PyUtilib', 'pyutilib_test_driver',
                        [ '--cat', 'x_suite2', '--cat', 'x_suite1',
                          join(currdir,'example1.json') ],
                        outfile=join(currdir,'test6.out'))
        self.assertFileEqualsBaseline(
            currdir + 'test6.out', currdir + 'test6.txt', filter=filter)


if __name__ == "__main__":
    unittest.main()
