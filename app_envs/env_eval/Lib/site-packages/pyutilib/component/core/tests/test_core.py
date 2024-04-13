#
# Unit Tests for component/core
#

import re
import sys
import os
from os.path import abspath, dirname
currdir = dirname(abspath(__file__)) + os.sep

from pyutilib.component.core import *
import pyutilib.th as unittest
import pyutilib.misc

try:
    import yaml
    yaml_available = True
except ImportError:
    yaml_available = False

testing_env = PluginEnvironment("testing")
PluginGlobals.add_env(testing_env)


def filter_noncore_interfaces(line):
    return "IConfiguration" in line or \
           "IEnvironmentConfig" in line or \
           "IExternalExecutable" in line or \
           "IFileOption" in line or  \
           "IOption" in line or  \
           "ITempfileManager" in line or  \
           "IWorkflowTask" in line or  \
           "testing" in line or  \
           "IDebug1" in line or  \
           "IDebug2" in line or  \
           "IDebug3" in line or  \
           "IDebug4" in line or  \
           "pyutilib.autotest" in line or  \
           "ITestDriver" in line or  \
           "IFunctorTask" in line or  \
           "ITestParser" in line or  \
           "pyutilib.workflow" in line or  \
           "IUpdatedOptionsAction" in line


class IDebug1(Interface):
    """An example interface"""


class IDebug2(Interface):
    """An example interface"""


class IDebug3(Interface):
    """An example interface"""


class IDebug4(Interface):
    """An example interface that provides default implementations of the api"""

    def __init__(self):
        self.x = 0

    def f1(self):
        self.x = 1

    def f2(self):
        self.x = 2


class Plugin1(Plugin):
    implements(IDebug1, service=True)


class Plugin1a(Plugin):
    implements(IDebug1)


class Plugin2(Plugin):
    implements(IDebug1, service=True)


class Plugin3(Plugin):
    implements(IDebug2, service=True)


class Plugin4(Plugin):
    implements(IDebug1, service=True)
    implements(IDebug2, service=True)


class Plugin5(Plugin):
    implements(IDebug3, service=True)


class Plugin6(Plugin, PluginEnvironment):
    implements(IDebug3, service=True)

    def __init__(self, **kwds):
        Plugin.__init__(self, **kwds)
        PluginEnvironment.__init__(self, "plugin6")


class Plugin7(Plugin):
    implements(IDebug1, service=True)

    def __init__(self, **kwds):
        Plugin.__init__(self, **kwds)
        self._enable = self._id % 2 == 0


class Plugin8(Plugin5):
    implements(IDebug2, service=True)


class Plugin9(Plugin5):
    implements(IDebug3, service=True)


class Service1(PluginEnvironment):

    def is_service_enabled(self, cls):
        return False


class Plugin10(Plugin):
    implements(IDebug1, "tmpenv", service=True)


class Plugin11a(Plugin):
    implements(IDebug4, service=True)

    def __init__(self):
        self.x = 4

    def f1(self):
        self.x = 5


class Plugin11b(Plugin):
    implements(IDebug4, inherit=True, service=True)

    def __init__(self):
        self.x = 0


PluginGlobals.pop_env()


class TestExtensionPoint(unittest.TestCase):

    def setUp(self):
        PluginGlobals.add_env(testing_env)

    def tearDown(self):
        env_ = PluginGlobals.pop_env()
        env_.cleanup(singleton=False)

    def test_interface_decl(self):
        try:

            class IDebug1(Interface):
                pass

            self.fail("expected failure")
        except PluginError:
            pass

    def test_ep_init(self):
        """Test ExtensionPoint construction"""
        ep = ExtensionPoint(IDebug1)
        self.assertEqual(IDebug1, ep.interface)
        try:
            ExtensionPoint()
            self.fail("error expected")
        except PluginError:
            pass

    def test_ep_string(self):
        """Test ExtensionPoint registration"""
        ep = ExtensionPoint(IDebug1)
        self.assertEqual(str(ep), "<ExtensionPoint IDebug1 env=testing>")
        self.assertEqual(len(ep.extensions()), 0)
        s0 = Plugin1()
        self.assertEqual(len(ep.extensions()), 1)
        s1 = Plugin1()
        self.assertEqual(len(ep.extensions()), 2)

    def test_ep_registration(self):
        """Test ExtensionPoint registration"""
        ep = ExtensionPoint(IDebug1)
        self.assertEqual(ep.extensions(), list())
        s1 = Plugin1()
        s1a = Plugin1a()
        s2 = Plugin2()
        s3 = Plugin3()
        s4 = Plugin4()
        s5 = Plugin5()
        self.assertEqual(set(ep.extensions()), set([s1, s2, s4]))
        self.assertEqual(set(ep.extensions()), set([s1, s2, s4]))

    def test_ep_call(self):
        """Test ExtensionPoint __call__"""
        ep = ExtensionPoint(IDebug1)
        s1 = Plugin1(name="p1")
        s2 = Plugin2(name="p2")
        s3 = Plugin4(name="p3")
        s4 = Plugin4(name="p3")
        s5 = Plugin3(name="p4")
        self.assertEqual(
            ep(), sorted(
                set([s1, s2, s3, s4]), key=lambda x: x._id))
        try:
            ep(0)
            self.fail("expected failure")
        except PluginError:
            pass
        self.assertEqual(ep("p1"), [s1])
        self.assertEqual(ep('p3'), sorted(set([s3, s4]), key=lambda x: x._id))

    def test_ep_service(self):
        """Test ExtensionPoint service()"""
        ep = ExtensionPoint(IDebug1)
        s1 = Plugin1()
        s2 = Plugin2()
        s3 = Plugin3()
        s4 = Plugin4()
        try:
            ep.service()
            self.fail("expected failure")
        except PluginError:
            pass

    def test_ep_namespace1(self):
        """Test the semantics of the use of namespaces in interface decl"""
        env = PluginEnvironment("tmpenv")
        s1 = Plugin10()
        s2 = Plugin1()
        namespace_current1 = ExtensionPoint(IDebug1).extensions()
        namespace_current2 = ExtensionPoint(IDebug1, env).extensions()
        self.assertEqual(set(namespace_current1), set((s1, s2)))
        self.assertEqual(set(namespace_current2), set((s1, s2)))


class TestPlugin(unittest.TestCase):

    def setUp(self):
        PluginGlobals.add_env("testing")

    def tearDown(self):
        env_ = PluginGlobals.pop_env()
        env_.cleanup(singleton=False)

    def test_init1(self):
        """Test the behavior of a plugin that is a service manager"""
        s1 = Plugin6()
        self.assertEqual(isinstance(s1, PluginEnvironment), True)
        self.assertEqual(isinstance(s1, Plugin), True)
        self.assertEqual(set(s1.__interfaces__.keys()), set([IDebug3]))

    #def test_init2(self):
    #"""Test that a plugin sets up the registry appropriately"""
    #s1 = Plugin4()
    #s2 = Plugin5()
    #self.assertEqual(s1 in PluginGlobals.interface_registry[IDebug1], True)
    #self.assertEqual(s1 in PluginGlobals.interface_registry[IDebug2], True)
    #self.assertEqual(not s1 in PluginGlobals.extension_points(IDebug3), True)

    def test_init4(self):
        """Verify that base classes are also captured"""
        s1 = Plugin8()
        self.assertEqual(set(s1.__interfaces__.keys()), set([IDebug3, IDebug2]))
        s1 = Plugin9()
        self.assertEqual(set(s1.__interfaces__.keys()), set([IDebug3]))

    def test_init5(self):
        #
        # We don't maintain a registry of environments
        #
        PluginEnvironment("test")
        PluginEnvironment("test")

    def test_repr(self):
        """Test the string representation generated"""
        tmp = PluginGlobals.plugin_counter
        PluginGlobals.plugin_counter = 0
        s1 = Plugin1()
        s2 = Plugin2()
        s3 = Plugin3()
        s4 = Plugin1()
        s5 = Plugin3()
        PluginGlobals.plugin_counter = tmp
        self.assertEqual(str(s1), "<Plugin Plugin1 'Plugin.1'>")
        self.assertEqual(str(s2), "<Plugin Plugin2 'Plugin.2'>")
        self.assertEqual(str(s3), "<Plugin Plugin3 'Plugin.3'>")
        self.assertEqual(str(s4), "<Plugin Plugin1 'Plugin.4'>")
        self.assertEqual(str(s5), "<Plugin Plugin3 'Plugin.5'>")

    def test_enabled(self):
        """Test control of enabled()"""
        ep = ExtensionPoint(IDebug1)
        self.assertEqual(ep.extensions(), list())
        s1 = Plugin1()
        s2 = Plugin2()
        s3 = Plugin3()
        s4 = Plugin4()
        s5 = Plugin5()
        s7a = Plugin7()
        s7b = Plugin7()
        s7c = Plugin7()
        s7d = Plugin7()
        s7e = Plugin7()
        s7f = Plugin7()
        #
        # Only s7b, and s7d will be returned from the exensions() calls
        #
        tmp = set(ep.extensions())
        if s7e in tmp:
            self.assertEqual(
                set(ep.extensions()), set([s1, s2, s4, s7a, s7c, s7e]))
        else:
            self.assertEqual(
                set(ep.extensions()), set([s1, s2, s4, s7b, s7d, s7f]))
        self.assertTrue(PluginGlobals.services() >= set(
            [s1, s2, s3, s4, s5, s7a, s7b, s7c, s7d, s7e, s7f]))

    def test_implements1(self):
        p1 = Plugin11a()
        self.assertEqual(p1.x, 4)
        p1.f1()
        self.assertEqual(p1.x, 5)
        try:
            p1.f2()
            self.fail("Expected AttributeError")
        except AttributeError:
            pass

    def test_implements2(self):
        p1 = Plugin11b()
        self.assertEqual(p1.x, 0)
        p1.f1()
        self.assertEqual(p1.x, 1)
        p1.f2()
        self.assertEqual(p1.x, 2)


class TestMisc(unittest.TestCase):

    def setUp(self):
        PluginGlobals.add_env("testing")

    def tearDown(self):
        env_ = PluginGlobals.remove_env("testing")
        env_.cleanup(singleton=False)

    def test_pprint(self):
        """Test the string representation generated"""

        class Plugin100(SingletonPlugin):
            implements(IDebug3, service=True)

        spx = Plugin100()
        PluginGlobals.add_env("foo")
        s1 = Plugin1()
        s2 = Plugin2()
        s3 = Plugin3()
        tmp_env = PluginGlobals.add_env("bar")
        s4 = Plugin1()
        s5 = Plugin3()
        s6 = Plugin11b()
        sp0 = Plugin100()
        try:
            self.assertFalse(re.match("<Plugin Plugin1", str(s1)) is None)
            self.assertFalse(re.match("<Plugin Plugin2", str(s2)) is None)
            self.assertFalse(re.match("<Plugin Plugin3", str(s3)) is None)
            self.assertFalse(re.match("<Plugin Plugin1", str(s4)) is None)
            self.assertFalse(re.match("<Plugin Plugin3", str(s5)) is None)
            pyutilib.misc.setup_redirect(currdir + "log1.out")
            PluginGlobals.pprint(plugins=False, json=True)
            pyutilib.misc.reset_redirect()
            self.assertMatchesJsonBaseline(currdir + "log1.out",
                                           currdir + "log1.jsn")
            if yaml_available:
                pyutilib.misc.setup_redirect(currdir + "log1.out")
                PluginGlobals.pprint(plugins=False, json=True)
                pyutilib.misc.reset_redirect()
                self.assertMatchesYamlBaseline(currdir + "log1.out",
                                               currdir + "log1.yml")
                #
                pyutilib.misc.setup_redirect(currdir + "log1.out")
                PluginGlobals.pprint(plugins=False)
                pyutilib.misc.reset_redirect()
                self.assertMatchesYamlBaseline(currdir + "log1.out",
                                               currdir + "log1.yml")
        finally:
            PluginGlobals.remove_env("foo", cleanup=True, singleton=False)
            PluginGlobals.remove_env("bar", cleanup=True, singleton=False)


class TestManager(unittest.TestCase):

    def setUp(self):
        PluginGlobals.add_env("testing")

    def tearDown(self):
        env_ = PluginGlobals.pop_env()
        if env_.name == 'testing':
            env_.cleanup(singleton=False)

    def test_init(self):
        """Test the behavior of a plugin that is a service manager"""
        s0 = Plugin1()
        self.assertTrue(PluginGlobals.services() >= set([s0]))
        env = PluginEnvironment("dummy")
        PluginGlobals.add_env(env)
        s1 = Plugin6()
        #self.assertTrue(s1 in PluginGlobals.get_env("testing"))
        #self.assertEqual(s1.services, set([]))
        self.assertTrue(PluginGlobals.services("testing") >= set([s0, s1]))
        PluginGlobals.remove_env("dummy")
        s2 = Plugin6()
        #self.assertTrue(s2 in PluginGlobals.get_env())
        #self.assertEqual(env.services, set([]))
        self.assertTrue(PluginGlobals.services("testing") >= set([s0, s1, s2]))

    def Xtest_get(self):
        env = PluginEnvironment("dummy")
        PluginGlobals.add_env(env)
        s0 = Plugin1()
        self.assertNotEqual(env.active_services(IDebug1), [s0])
        self.assertEqual(
            PluginGlobals.get_env("testing").active_services(IDebug1), [s0])
        try:
            env.active_services(s0)
            self.fail("Expected failure")
        except PluginError:
            pass
        PluginGlobals.pop_env()

    def test_pop1(self):
        """Test that popping the environment doesn't remove the last env"""
        PluginGlobals.pop_env()
        PluginGlobals.pop_env()
        PluginGlobals.pop_env()
        self.assertEqual(len(PluginGlobals.env_stack), 1)

    def test_pop2(self):
        try:
            PluginGlobals.add_env("pca", validate=True)
            self.fail("expected error")
        except PluginError:
            pass
        PluginGlobals.add_env("pca")
        self.assertEqual(PluginGlobals.get_env().name, "pca")
        PluginGlobals.pop_env()

    def test_factory(self):

        class Plugin5_factory(Plugin):
            implements(IDebug3, service=True)

        class Plugin6_factory(Plugin, PluginEnvironment):
            implements(IDebug3, service=True)

            def __init__(self, **kwds):
                Plugin.__init__(self, **kwds)
                PluginEnvironment.__init__(self, "plugin6_factory")

        PluginFactory("Plugin6_factory", name="p6")
        PluginFactory("Plugin5_factory", name="p5")
        PluginFactory("Plugin6_factory")
        try:
            PluginFactory("__foo__")
            self.fail("expected error")
        except PluginError:
            pass
        pyutilib.misc.setup_redirect(currdir + "factory.out")
        PluginGlobals.pprint(plugins=False, json=True)
        pyutilib.misc.reset_redirect()
        self.assertMatchesJsonBaseline(currdir + "factory.out",
                                       currdir + "factory.jsn")
        if yaml_available:
            pyutilib.misc.setup_redirect(currdir + "factory.out")
            PluginGlobals.pprint(plugins=False, json=True)
            pyutilib.misc.reset_redirect()
            self.assertMatchesYamlBaseline(currdir + "factory.out",
                                           currdir + "factory.yml")
            #
            pyutilib.misc.setup_redirect(currdir + "factory.out")
            PluginGlobals.pprint(plugins=False)
            pyutilib.misc.reset_redirect()
            self.assertMatchesYamlBaseline(currdir + "factory.out",
                                           currdir + "factory.yml")


if __name__ == "__main__":
    #import pyutilib.misc
    #print(pyutilib.misc.compare_file(currdir+"log1.out",currdir+"log1.txt", filter=filter_noncore_interfaces))
    unittest.main()
