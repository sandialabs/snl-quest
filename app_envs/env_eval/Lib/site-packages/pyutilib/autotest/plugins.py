#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________
#

__all__ = ['ITestDriver', 'TestDriverFactory', 'ITestParser', 'TestDriverBase']

from pyutilib.component.core import Interface, implements, Plugin, CreatePluginFactory


class ITestParser(Interface):

    def load_test_config(self, filename):
        pass  #pragma:nocover

    def print_test_config(self, repn):
        pass  #pragma:nocover


class ITestDriver(Interface):

    def setUpClass(self, cls, options):
        """Set-up the class that defines the suite of tests"""

    def tearDownClass(self, cls, options):
        """Tear-down the class that defines the suite of tests"""

    def setUp(self, testcase, options):
        """Set-up a single test in the suite"""

    def tearDown(self, testcase, options):
        """Tear-down a single test in the suite"""

    def run_test(self, testcase, name, options):
        """Execute a single test in the suite"""


class TestDriverBase(Plugin):

    implements(ITestDriver)

    def setUpClass(self, cls, options):
        """Set-up the class that defines the suite of tests"""

    def tearDownClass(self, cls, options):
        """Tear-down the class that defines the suite of tests"""

    def setUp(self, testcase, options):
        """Set-up a single test in the suite"""

    def tearDown(self, testcase, options):
        """Tear-down a single test in the suite"""

    def run_test(self, testcase, name, options):
        """Execute a single test in the suite"""


TestDriverFactory = CreatePluginFactory(ITestDriver)
