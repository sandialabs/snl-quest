import os
import re
import sys
from os.path import abspath, dirname
currdir = dirname(abspath(__file__)) + os.sep

import unittest
from pyutilib.component.core import Interface, PluginGlobals, ExtensionPoint, implements, Plugin
from pyutilib.component.config.options import Option, OptionError, IOption, declare_option, FileOption, IntOption, FloatOption, DictOption, BoolOption

PluginGlobals.add_env("testing.options")


class IDummyOption(Interface):
    """An interface that supports the initialization of the directory for
    options that specify files.  This is needed to correctly initialize
    relative paths for files."""


class DummyOption1(Option):
    """A test class that converts option data into float values."""

    implements(IDummyOption)

    def convert(self, value, default):
        """Conversion routine."""
        val = value[-1]
        if not val:
            return 0
        try:
            return float(val)
        except ValueError:
            raise OptionError('Expected float, got %s' % repr(value))
        except TypeError:
            raise OptionError('Expected string or float type, got %s' %
                              repr(value))


PluginGlobals.pop_env()


class TestOption(unittest.TestCase):

    def setUp(self):
        PluginGlobals.add_env("testing.options")
        PluginGlobals.clear_global_data(keys=['globals', 'a.b'])

    def tearDown(self):
        PluginGlobals.remove_env(
            "testing.options", cleanup=True, singleton=False)

    def test_init1(self):
        """Test Option construction"""
        try:
            Option()
            self.fail("expected failure")
        except OptionError:
            pass

        try:
            Option(None)
            self.fail("expected failure")
        except OptionError:
            pass

        try:
            Option("name", x=None)
            self.fail("expected failure")
        except OptionError:
            pass

    def test_init2(self):
        """Test Option construction"""
        FOO = Option("foo")
        self.assertEqual(FOO.name, "foo")
        self.assertTrue(FOO.default is None)
        self.assertTrue(FOO.section == "globals")
        self.assertTrue(FOO.section_re == None)
        self.assertTrue(FOO.__doc__ == "")

    def test_init3(self):
        """Test Option construction"""
        FOO = Option(
            name="foo", default=1, section="a", doc="b", section_re="re")
        self.assertEqual(FOO.name, "foo")
        self.assertEqual(FOO.default, 1)
        self.assertTrue(FOO.get_value() == 1)
        self.assertEqual(FOO.section, "a")
        self.assertEqual(FOO.section_re, "re")
        self.assertEqual(FOO.__doc__, "b")

    def test_set_get1(self):
        """Test set/get values"""

        class TMP_set_get1(Plugin):
            ep = ExtensionPoint(IDummyOption)
            declare_option("foo", local_name="opt", default=4, cls=DummyOption1)

        obj = TMP_set_get1()
        self.assertTrue(obj.opt == 4)
        self.assertTrue(obj.opt / 2 == 2)
        obj.opt = 6
        self.assertTrue(obj.opt / 2 == 3)
        #
        # Verify that the TMP instance has value 6
        #
        for pt in obj.ep:
            self.assertEqual(pt.get_value(), 6)

    def test_set_get2(self):
        """Test validate global nature of set/get"""

        class TMP_set_get2(Plugin):
            ep = ExtensionPoint(IOption)
            declare_option("foo", local_name="o1", default=4)
            declare_option("foo", local_name="o2", default=4)

        obj = TMP_set_get2()
        self.assertEqual(type(obj.o1), int)
        self.assertTrue(obj.o1 / 2 == 2)
        obj.o1 = 6
        self.assertTrue(obj.o1 / 2 == 3)
        self.assertTrue(obj.o2 / 2 == 3)

    def test_set_get3(self):
        """Test validate nature of set/get for instance-specific options"""

        class TMP_set_get3(Plugin):
            ep = ExtensionPoint(IOption)

            def __init__(self, section):
                declare_option("o1", section=section, default=4)

        obj1 = TMP_set_get3("sec1")
        obj2 = TMP_set_get3("sec1")
        obj3 = TMP_set_get3("sec2")
        self.assertEqual(type(obj1.o1), int)
        self.assertTrue(obj1.o1 / 2 == 2)
        self.assertTrue(obj2.o1 / 2 == 2)
        self.assertTrue(obj3.o1 / 2 == 2)
        obj1.o1 = 6
        self.assertTrue(obj1.o1 / 2 == 3)
        self.assertTrue(obj2.o1 / 2 == 3)
        self.assertTrue(obj3.o1 / 2 == 2)

    def test_repr(self):
        """Test string repn"""
        ep = ExtensionPoint(IOption)

        class TMP_repr(Plugin):
            declare_option("o1", default=4)
            declare_option("o2", section="foo", default=4)

        obj = TMP_repr()
        if re.match("\<Option \[globals\] 'o1'\>",
                    str(ep.service("o1"))) is None:
            self.fail("Expected globals:o1, but this option is %s" %
                      str(ep.service("o1")))
        self.assertFalse(
            re.match("\<Option \[globals\] 'o1'\>", str(ep.service("o1"))) is
            None)
        self.assertFalse(
            re.match("\<Option \[foo\] 'o2'\>", str(ep.service("o2"))) is None)
        self.assertEqual(ep.service("o1").get_value(), 4)
        ep.service("o1").load("o1", ["new"])
        self.assertEqual(ep.service("o1").get_value(), "new")
        ep.service("o1").load("o1", "old")
        self.assertEqual(ep.service("o1").get_value(), "old")

    def test_bool(self):
        """Test boolean"""
        ep = ExtensionPoint(IOption)

        class TMP_bool(Plugin):
            declare_option("o1", cls=BoolOption)

        obj = TMP_bool()
        pt = ep.service("o1")

        pt.load("o1", [True])
        self.assertEqual(pt.get_value(), True)

        pt.load("o1", [False])
        self.assertEqual(pt.get_value(), False)

        pt.load("o1", [1])
        self.assertEqual(pt.get_value(), True)

        pt.load("o1", [0])
        self.assertEqual(pt.get_value(), False)

        pt.load("o1", ['YES'])
        self.assertEqual(pt.get_value(), True)

        pt.load("o1", ['no'])
        self.assertEqual(pt.get_value(), False)

    def test_int(self):
        """Test int"""
        ep = ExtensionPoint(IOption)

        class TMP_int(Plugin):
            declare_option("o1", cls=IntOption)

        obj = TMP_int()
        pt = ep.service("o1")

        pt.load("o1", [-1])
        self.assertEqual(pt.get_value(), -1)

        pt.load("o1", ["-1"])
        self.assertEqual(pt.get_value(), -1)

        pt.load("o1", [[]])
        self.assertEqual(pt.get_value(), 0)

        try:
            pt.load("o1", [['a']])
            self.fail("expected error")
        except OptionError:
            pass

        try:
            pt.load("o1", ["-1.5"])
            self.fail("expected error")
        except OptionError:
            pass

    def test_float(self):
        """Test float"""
        ep = ExtensionPoint(IOption)

        class TMP_float(Plugin):
            declare_option("o1", cls=FloatOption)

        obj = TMP_float()
        pt = ep.service("o1")

        pt.load("o1", [-1.5])
        self.assertEqual(pt.get_value(), -1.5)

        pt.load("o1", ["-1.5"])
        self.assertEqual(pt.get_value(), -1.5)

        pt.load("o1", [[]])
        self.assertEqual(pt.get_value(), 0)

        try:
            pt.load("o1", [['a']])
            self.fail("expected error")
        except OptionError:
            pass

        try:
            pt.load("o1", ['a'])
            self.fail("expected error")
        except OptionError:
            pass

    def test_dict1(self):
        """Test DictOption"""
        ep = ExtensionPoint(IOption)

        class TMP_dict1(Plugin):
            declare_option("options", DictOption)
            declare_option("b")
            declare_option("c", default=3)

        obj = TMP_dict1()

        self.assertEqual(obj.options.b, None)
        self.assertEqual(obj.options.c, 3)

    def test_dict2(self):
        """Test DictOption"""
        ep = ExtensionPoint(IOption)

        class TMP_dict2(Plugin):
            declare_option("options", DictOption)
            declare_option("b", local_name="o1")
            declare_option("c", local_name="o2", default=3)

        obj = TMP_dict2()
        #
        # testing attribute set/get
        #
        obj.options.x = 3
        self.assertEqual(obj.options.x, 3)
        try:
            obj.options.xx
            self.fail("expected error")
        except OptionError:
            pass
        #
        # Testing the DictOption set/get
        #
        obj.options = {'yy': 3, 'zz': 2}
        self.assertEqual(obj.options.yy, 3)
        self.assertEqual(obj.options.zz, 2)
        #
        # Testing load
        #
        #obj.options.load('vv',1)
        #obj.options.load('uu',[1])
        #self.assertEqual(obj.options.uu,3)
        #self.assertEqual(obj.options.vv,3)

    def test_path(self):
        """Test path"""
        ep = ExtensionPoint(IOption)
        if sys.platform == "win32":
            o1_default = "C:/default"
        else:
            o1_default = "/dev//default"

        class TMP_path(Plugin):
            declare_option(
                "o1", cls=FileOption, default=o1_default, directory="/dev/null")

        obj = TMP_path()
        pt = ep.service("o1")

        pt.load("o1", [None])
        if sys.platform == "win32":
            self.assertEqual(pt.get_value(), "c:\\default")
        else:
            self.assertEqual(pt.get_value(), "/dev/default")

        if sys.platform == "win32":
            pt.load("o1", ["C:/load1"])
        else:
            pt.load("o1", ["/dev/load1"])
        if sys.platform == "win32":
            self.assertEqual(pt.get_value(), "c:\\load1")
        else:
            self.assertEqual(pt.get_value(), "/dev/load1")

        if sys.platform == "win32":
            pt.set_dir("D:/foo")
        else:
            pt.set_dir("/dev/foo")
        pt.load("o1", ["bar"])
        if sys.platform == "win32":
            self.assertEqual(pt.get_value(), "d:\\foo\\bar")
        else:
            self.assertEqual(pt.get_value(), "/dev/foo/bar")

    def test_OptionPlugin(self):
        """Test OptionPlugin"""
        ep = ExtensionPoint(IOption)

        class TMP_OptionPlugin(Plugin):
            declare_option("o1")

        obj = TMP_OptionPlugin()
        pt = ep.service("o1")

        try:
            pt.load("o1", [])
            self.fail("expected error")
        except OptionError:
            pass


if __name__ == "__main__":
    unittest.main()
