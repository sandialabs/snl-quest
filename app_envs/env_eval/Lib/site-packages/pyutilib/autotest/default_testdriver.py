#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________
#

import sys
from pyutilib.component.core import Plugin, implements, alias
from pyutilib.autotest import plugins


class DefaultTestDriver(Plugin):
    """
    This is the 'default' test driver, which simply prints the
    arguments being passed into a test.
    """

    implements(plugins.ITestDriver)
    alias('default')

    def setUpClass(self, cls, options):
        """Set-up the class that defines the suite of tests"""

    def tearDownClass(self, cls, options):
        """Tear-down the class that defines the suite of tests"""

    def setUp(self, testcase, options):
        """Set-up a single test in the suite"""

    def tearDown(self, testcase, options):
        """Tear-down a single test in the suite"""
        sys.stdout.flush()

    def run_test(self, testcase, name, options):
        """Execute a single test in the suite"""
        print('run_test ' + name)
        print(options)
