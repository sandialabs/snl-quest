#
# Unit Tests for component/core
#

import os
from os.path import abspath, dirname
currdir = dirname(abspath(__file__)) + os.sep

import pyutilib.th as unittest
import pyutilib.component.core


#
# This class is declared to facilitate coverage
#
class DummyPlugin(pyutilib.component.core.Plugin):

    pyutilib.component.core.implements(pyutilib.component.core.IPluginLoadPath)
    pyutilib.component.core.implements(pyutilib.component.core.IPluginLoader)

    def get_load_path(self):
        return []

    def load(self, x, y, z, w):
        pass


class TestLoader(unittest.TestCase):

    def setUp(self):
        pyutilib.component.core.PluginGlobals.add_env("testing.loader")
        DummyPlugin()

    def tearDown(self):
        pyutilib.component.core.PluginGlobals.remove_env("testing.loader")

    def test_load1(self):
        pyutilib.component.core.PluginGlobals.get_env().load_services(
            path=currdir + "plugins1", auto_disable=True, name_re="^$")

    def test_load2(self):
        pyutilib.component.core.PluginGlobals.get_env().load_services(
            path=[currdir + "plugins1", currdir + "plugins2"],
            auto_disable="^$",
            name_re="^$")

    def test_load3(self):
        try:
            pyutilib.component.core.PluginGlobals.get_env().load_services(
                path={})
            self.fail("expect error")
        except pyutilib.component.core.PluginError:
            pass

    def test_load4(self):
        pyutilib.component.core.PluginGlobals.load_services(
            auto_disable="", name_re="^$")

    def test_load5(self):
        pyutilib.component.core.PluginGlobals.get_env().load_services(
            path=[currdir + "plugins1", currdir + "plugins2"],
            auto_disable=False,
            name_re="^$")

    def test_load6(self):
        pyutilib.component.core.PluginGlobals.get_env().load_services(
            path=[currdir + "plugins1", currdir + "plugins2"],
            auto_disable=False,
            name_re=True)


if __name__ == "__main__":
    unittest.main()
