#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________
#

__test__ = False

import pyutilib.component.core
pyutilib.component.core.PluginGlobals.add_env('pyutilib.autotest')

from pyutilib.autotest.plugins import ITestDriver, TestDriverFactory, ITestParser, TestDriverBase
from pyutilib.autotest.driver import run, main, create_test_suites
import pyutilib.autotest.yaml_plugin
import pyutilib.autotest.json_plugin
import pyutilib.autotest.default_testdriver

pyutilib.component.core.PluginGlobals.pop_env()
