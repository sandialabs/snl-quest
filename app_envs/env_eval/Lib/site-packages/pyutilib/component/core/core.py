# This is a copy of the with_metaclass function from 'six' from the
# development branch.  This fixes a bug in six 1.6.1.
#
# Copyright (c) 2010-2014 Benjamin Peterson
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import re
import sys
import weakref
from six import itervalues, string_types
import logging
logger = logging.getLogger('pyutilib.component.core')

__all__ = ['Plugin', 'implements', 'Interface', 'CreatePluginFactory',
           'PluginMeta', 'alias', 'ExtensionPoint', 'SingletonPlugin',
           'PluginFactory', 'PluginError', 'PluginGlobals', 'with_metaclass',
           'IPluginLoader', 'IPluginLoadPath', 'IIgnorePluginWhenLoading',
           'IOptionDataProvider', 'PluginEnvironment']

# print "ZZZ - IMPORTING CORE"


def with_metaclass(meta, *bases):
    """Create a base class with a metaclass."""

    # This requires a bit of explanation: the basic idea is to make a
    # dummy metaclass for one level of class instantiation that replaces
    # itself with the actual metaclass.  Because of internal type checks
    # we also need to make sure that we downgrade the custom metaclass
    # for one level to something closer to type (that's why __call__ and
    # __init__ comes back from type etc.).
    class metaclass(meta):
        __call__ = type.__call__
        __init__ = type.__init__

        def __new__(cls, name, this_bases, d):
            if this_bases is None:
                return type.__new__(cls, name, (), d)
            return meta(name, bases, d)

    return metaclass('temporary_class', None, {})

#
# Plugins define within Pyomo
#


#
# Define the default logging behavior for a given namespace, which is to
# ignore the log messages.
#
def logger_factory(namespace):
    log = logging.getLogger('pyutilib.component.core.' + namespace)

    class NullHandler(logging.Handler):

        def emit(self, record):  # pragma:nocover
            """Do not generate logging record"""

    log.addHandler(NullHandler())
    return log


class PluginError(Exception):
    """Exception base class for plugin errors."""

    def __init__(self, value):
        """Constructor, whose argument is the error message"""
        self.value = value

    def __str__(self):
        """Return a string value for this message"""
        return str(self.value)


class PluginEnvironment(object):

    def __init__(self, name=None, bootstrap=False):
        if bootstrap:
            self.env_id = 1
        else:
            PluginGlobals.env_counter += 1
            self.env_id = PluginGlobals.env_counter
            if name is None:
                name = "env%d" % PluginGlobals.env_counter
            if name in PluginGlobals.env:
                raise PluginError("Environment %s is already defined" % name)
        #
        self.loaders = None
        self.loader_paths = None
        #
        self.name = name
        self.log = logger_factory(self.name)
        if __debug__ and self.log.isEnabledFor(logging.DEBUG):
            self.log.debug("Creating PluginEnvironment %r" % self.name)
        # A dictionary of plugin classes
        #   name -> plugin cls
        self.plugin_registry = {}
        # The interfaces that have been defined
        #   name -> interface cls
        self.interfaces = {}
        # A dictionary of singleton plugin class instance ids
        #   plugin cls -> id
        self.singleton_services = {}
        # A set of nonsingleton plugin instances
        self.nonsingleton_plugins = set()

    def cleanup(self, singleton=True):
        # ZZZ
        # return
        if PluginGlobals is None or PluginGlobals.plugin_instances is None:
            return
        if singleton:
            for id_ in itervalues(self.singleton_services):
                if (id_ in PluginGlobals.plugin_instances and
                        PluginGlobals.plugin_instances[id_] is not None):
                    del PluginGlobals.plugin_instances[id_]
            self.singleton_services = {}
        #
        for id_ in self.nonsingleton_plugins:
            del PluginGlobals.plugin_instances[id_]
        self.nonsingleton_plugins = set()

    def plugins(self):
        for id_ in itervalues(self.singleton_services):
            if (id_ in PluginGlobals.plugin_instances and
                    PluginGlobals.plugin_instances[id_] is not None):
                yield PluginGlobals.plugin_instances[id_]
        for id_ in sorted(self.nonsingleton_plugins):
            yield PluginGlobals.plugin_instances[id_]

    def load_services(self, path=None, auto_disable=False, name_re=True):
        """Load services from IPluginLoader extension points"""

        if self.loaders is None:
            self.loaders = ExtensionPoint(IPluginLoader)
            self.loader_paths = ExtensionPoint(IPluginLoadPath)
        #
        # Construct the search path
        #
        search_path = []
        if path is not None:
            if isinstance(path, string_types):
                search_path.append(path)
            elif type(path) is list:
                search_path += path
            else:
                raise PluginError("Unknown type of path argument: " + str(
                    type(path)))
        for item in self.loader_paths:
            search_path += item.get_load_path()
        self.log.info("Loading services to environment "
                      "%s from search path %s" % (self.name, search_path))
        #
        # Compile the enable expression
        #
        if type(auto_disable) is bool:
            if auto_disable:
                disable_p = re.compile("")
            else:
                disable_p = re.compile("^$")
        else:
            disable_p = re.compile(auto_disable)
        #
        # Compile the name expression
        #
        if type(name_re) is bool:
            if name_re:
                name_p = re.compile("")
            else:  # pragma:nocover
                raise PluginError(
                    "It doesn't make sense to specify name_re=False")
        else:
            name_p = re.compile(name_re)
        #
        for loader in self.loaders:
            loader.load(self, search_path, disable_p, name_p)
        # self.clear_cache()

    def Xclear_cache(self):
        """Clear the cache of active services"""
        self._cache = {}


class ExtensionPoint(object):
    """Marker class for extension points in services."""

    def __init__(self, *args):
        """Create the extension point.

        @param interface: the `Interface` subclass that defines the protocol
            for the extension point
        """
        #
        # Construct the interface, passing in this extension
        #
        nargs = len(args)
        if nargs == 0:
            raise PluginError(
                "Must specify interface class used in the ExtensionPoint")
        self.interface = args[0]
        self.__doc__ = 'List of services that implement `%s`' % \
            self.interface.__name__

    def __iter__(self):
        """Return an iterator to a set of services that match the interface of
        this extension point.
        """
        return self.extensions().__iter__()

    def __call__(self, key=None, all=False):
        """Return a set of services that match the interface of this
        extension point.
        """
        if type(key) in (int, int):
            raise PluginError("Access of the n-th extension point is "
                              "disallowed.  This is not well-defined, since "
                              "ExtensionPoints are stored as unordered sets.")
        return self.extensions(all=all, key=key)

    def service(self, key=None, all=False):
        """Return the unique service that matches the interface of this
        extension point.  An exception occurs if no service matches the
        specified key, or if multiple services match.
        """
        ans = ExtensionPoint.__call__(self, key=key, all=all)
        if len(ans) == 1:
            #
            # There is a single service, so return it.
            #
            return ans.pop()
        elif len(ans) == 0:
            return None
        else:
            raise PluginError("The ExtensionPoint does not have a unique "
                              "service!  %d services are defined for interface"
                              " %s.  (key=%s)" %
                              (len(ans), self.interface.__name__, str(key)))

    def __len__(self):
        """Return the number of services that match the interface of this
        extension point.
        """
        return len(self.extensions())

    def extensions(self, all=False, key=None):
        """Return a set of services that match the interface of this
        extension point.  This tacitly filters out disabled extension
        points.

        TODO - Can this support caching?
        How would that relate to the weakref test?
        """
        strkey = str(key)
        ans = set()
        remove = set()
        if self.interface in PluginGlobals.interface_services:
            for id_ in PluginGlobals.interface_services[self.interface]:
                if id_ not in PluginGlobals.plugin_instances:
                    remove.add(id_)
                    continue
                if id_ < 0:
                    plugin = PluginGlobals.plugin_instances[id_]
                else:
                    plugin = PluginGlobals.plugin_instances[id_]()
                if plugin is None:
                    remove.add(id_)
                elif ((all or plugin.enabled()) and
                      (key is None or strkey == plugin.name)):
                    ans.add(plugin)
            # Remove weakrefs that were empty
            # ZZ
            for id_ in remove:
                PluginGlobals.interface_services[self.interface].remove(id_)
        return sorted(ans, key=lambda x: x._id)

    def __repr__(self, simple=False):
        """Return a textual representation of the extension point.

        TODO: use the 'simple' argument
        """
        env_str = ""
        for env_ in itervalues(PluginGlobals.env):
            if self.interface in set(itervalues(env_.interfaces)):
                env_str += " env=%s" % env_.name
        return '<ExtensionPoint %s%s>' % (self.interface.__name__, env_str)


class PluginGlobals(object):
    """Global data for plugins. The main role of this class is to manage
    the stack of PluginEnvironment instances.

    Note: a single ID counter is used for tagging both environment and
    plugins registrations.  This enables the  user to track the relative
    order of construction of these objects.
    """

    def __init__(self):  # pragma:nocover
        """Disable construction."""
        raise PluginError("The PluginGlobals class should not be created.")

    # A dictionary of interface classes mapped to sets of plugin class
    # instance ids
    #   interface cls -> set(ids)
    interface_services = {}

    # A dictionary of plugin instances
    #   id -> weakref(instance)
    plugin_instances = {}

    # Environments
    env = {'pca': PluginEnvironment('pca', bootstrap=True)}
    env_map = {1: 'pca'}
    env_stack = ['pca']
    """A unique id used to name plugin objects"""
    plugin_counter = 0
    """A unique id used to name environment objects"""
    env_counter = 1
    """A list of executables"""
    _executables = []
    """TODO"""
    _default_OptionData = None

    @staticmethod
    def get_env(arg=None):
        """Return the current environment."""
        if arg is None:
            return PluginGlobals.env[PluginGlobals.env_stack[-1]]
        else:
            return PluginGlobals.env.get(arg, None)

    @staticmethod
    def add_env(name=None, validate=False):
        if name is not None and not isinstance(name, string_types):
            if validate and name.name in PluginGlobals.env:
                raise PluginError("Environment %s is already defined" % name)
            # We assume we have a PluginEnvironment object here
            PluginGlobals.env[name.name] = name
            PluginGlobals.env_map[name.env_id] = name.name
            PluginGlobals.env_stack.append(name.name)
            if __debug__ and name.log.isEnabledFor(logging.DEBUG):
                name.log.debug("Pushing environment %r on the "
                               "PluginGlobals stack" % name.name)
            return name
        else:
            env_ = PluginGlobals.env.get(name, None)
            if validate and env_ is not None:
                raise PluginError("Environment %s is already defined" % name)
            if env_ is None:
                env_ = PluginEnvironment(name)
                PluginGlobals.env[env_.name] = env_
            PluginGlobals.env_map[env_.env_id] = env_.name
            PluginGlobals.env_stack.append(env_.name)
            if __debug__ and env_.log.isEnabledFor(logging.DEBUG):
                env_.log.debug("Pushing environment %r on the "
                               "PluginGlobals stack" % env_.name)
            return env_

    @staticmethod
    def pop_env():
        if len(PluginGlobals.env_stack) > 1:
            name = PluginGlobals.env_stack.pop()
            env_ = PluginGlobals.env[name]
            if __debug__ and env_.log.isEnabledFor(logging.DEBUG):
                env_.log.debug("Popping environment %r from the "
                               "PluginGlobals stack" % env_.name)
            return env_
        else:
            return PluginGlobals.env[PluginGlobals.env_stack[0]]

    @staticmethod
    def remove_env(name, cleanup=False, singleton=True):
        tmp = PluginGlobals.env.get(name, None)
        if tmp is None:
            raise PluginError("No environment %s is defined" % name)
        # print "HERE - remove", name, tmp.env_id
        del PluginGlobals.env_map[tmp.env_id]
        del PluginGlobals.env[name]
        if cleanup:
            tmp.cleanup(singleton=singleton)
        PluginGlobals.env_stack = [name_ for name_ in PluginGlobals.env_stack
                                   if name_ in PluginGlobals.env]
        return tmp

    @staticmethod
    def clear():
        # ZZ
        # return
        for env_ in itervalues(PluginGlobals.env):
            env_.cleanup()
        PluginGlobals.interface_services = {}
        PluginGlobals.plugin_instances = {}
        PluginGlobals.env = {'pca': PluginEnvironment('pca', bootstrap=True)}
        PluginGlobals.env_map = {1: 'pca'}
        PluginGlobals.env_stack = ['pca']
        PluginGlobals.plugin_counter = 0
        PluginGlobals.env_counter = 1
        PluginGlobals._executables = []

    @staticmethod
    def clear_global_data(keys=None):
        # ZZ
        # return
        ep = ExtensionPoint(IOptionDataProvider)
        for ep_ in ep:
            ep_.clear(keys=keys)

    @staticmethod
    def services(name=None):
        """A convenience function that returns the services in the
        current environment.

        TODO:  env-specific services?
        """
        ans = set()
        for ids in itervalues(PluginGlobals.interface_services):
            for id_ in ids:
                if id_ not in PluginGlobals.plugin_instances:
                    # TODO: discard the id from the set?
                    continue
                if id_ < 0:
                    ans.add(PluginGlobals.plugin_instances[id_])
                else:
                    ans.add(PluginGlobals.plugin_instances[id_]())
        return ans

    @staticmethod
    def load_services(**kwds):
        """Load services from IPluginLoader extension points"""
        PluginGlobals.get_env().load_services(**kwds)

    @staticmethod
    def pprint(**kwds):
        """A pretty-print function"""

        ans = {}
        s = "#------------------------------"\
            "--------------------------------\n"
        i = 1
        ans['Environment Stack'] = {}
        s += "Environment Stack:\n"
        for env in PluginGlobals.env_stack:
            ans['Environment Stack'][i] = env
            s += "  '" + str(i) + "': " + env + "\n"
            i += 1
        s += "#------------------------------"\
             "--------------------------------\n"
        ans['Interfaces Declared'] = {}
        s += "Interfaces Declared:\n"
        keys = []
        for env_ in itervalues(PluginGlobals.env):
            keys.extend(interface_ for interface_ in env_.interfaces)
        keys.sort()
        for key in keys:
            ans['Interfaces Declared'][key] = None
            s += "  " + key + ":\n"
        s += "#------------------------------"\
             "--------------------------------\n"
        ans['Interfaces Declared by Environment'] = {}
        s += "Interfaces Declared by Environment:\n"
        for env_name in sorted(PluginGlobals.env.keys()):
            env_ = PluginGlobals.env[env_name]
            if len(env_.interfaces) == 0:
                continue
            ans['Interfaces Declared by Environment'][env_.name] = {}
            s += "  " + env_.name + ":\n"
            for interface_ in sorted(env_.interfaces.keys()):
                ans['Interfaces Declared by Environment'][env_.name][
                    interface_] = None
                s += "    " + interface_ + ":\n"
        #
        # Coverage is disabled here because different platforms give different
        # results.
        #
        if kwds.get('plugins', True):  # pragma:nocover
            s += "#---------------------------"\
                 "-----------------------------------\n"
            ans['Plugins by Environment'] = {}
            s += "Plugins by Environment:\n"
            for env_name in sorted(PluginGlobals.env.keys()):
                env_ = PluginGlobals.env[env_name]
                ans['Plugins by Environment'][env_.name] = {}
                s += "  " + env_.name + ":\n"
                flag = True
                for service_ in env_.plugins():
                    flag = False
                    try:
                        service_.name
                    except:
                        service_ = service_()
                    service_active = False
                    for interface in service_.__interfaces__:
                        if interface not in PluginGlobals.interface_services:
                            continue
                        service_active = service_._id in \
                            PluginGlobals.interface_services[interface]
                        break
                    service_s = service_.__repr__(
                        simple=not kwds.get('show_ids', True))
                    ans['Plugins by Environment'][env_.name][service_s] = {}
                    s += "    " + service_s + ":\n"
                    if kwds.get('show_ids', True):
                        ans['Plugins by Environment'][env_.name][service_s][
                            'name'] = service_.name
                        s += "       name:      " + service_.name + "\n"
                    ans['Plugins by Environment'][env_.name][service_s][
                        'id'] = str(service_._id)
                    s += "       id:        " + str(service_._id) + "\n"
                    ans['Plugins by Environment'][env_.name][service_s][
                        'singleton'] = str(service_.__singleton__)
                    s += "       singleton: " + \
                        str(service_.__singleton__) + "\n"
                    ans['Plugins by Environment'][env_.name][service_s][
                        'service'] = str(service_active)
                    s += "       service:   " + str(service_active) + "\n"
                    ans['Plugins by Environment'][env_.name][service_s][
                        'disabled'] = str(not service_.enabled())
                    s += "       disabled:  " + \
                        str(not service_.enabled()) + "\n"
                if flag:
                    s += "       None:\n"
        s += "#------------------------------"\
             "--------------------------------\n"
        ans['Plugins by Interface'] = {}
        s += "Plugins by Interface:\n"
        tmp = {}
        for env_ in itervalues(PluginGlobals.env):
            for interface_ in itervalues(env_.interfaces):
                tmp[interface_] = []
        for env_ in itervalues(PluginGlobals.env):
            for key in env_.plugin_registry:
                for item in env_.plugin_registry[key].__interfaces__:
                    if item in tmp:
                        tmp[item].append(key)
        keys = list(tmp.keys())
        for key in sorted(keys, key=lambda v: v.__name__.upper()):
            ans['Plugins by Interface'][str(key.__name__)] = {}
            if key.__name__ == "":  # pragma:nocover
                s += "  `" + str(key.__name__) + "`:\n"
            else:
                s += "  " + str(key.__name__) + ":\n"
            ttmp = tmp[key]
            ttmp.sort()
            if len(ttmp) == 0:
                s += "    None:\n"
            else:
                for item in ttmp:
                    ans['Plugins by Interface'][str(key.__name__)][item] = None
                    s += "    " + item + ":\n"
        s += "#-------------------------------"\
             "-------------------------------\n"
        ans['Plugins by Python Module'] = {}
        s += "Plugins by Python Module:\n"
        tmp = {}
        for env_ in itervalues(PluginGlobals.env):
            for name_ in env_.plugin_registry:
                tmp.setdefault(env_.plugin_registry[name_].__module__,
                               []).append(name_)
        if '__main__' in tmp:
            # This is a hack to ensure consistency in the tests
            tmp['pyutilib.component.core.tests.test_core'] = tmp['__main__']
            del tmp['__main__']
        keys = list(tmp.keys())
        keys.sort()
        for key in keys:
            ans['Plugins by Python Module'][str(key)] = {}
            if key == "":  # pragma:nocover
                s += "  `" + str(key) + "`:\n"
            else:
                s += "  " + str(key) + ":\n"
            ttmp = tmp[key]
            ttmp.sort()
            for item in ttmp:
                ans['Plugins by Python Module'][str(key)][item] = None
                s += "    " + item + ":\n"
        if kwds.get('json', False):
            import json
            print(
                json.dumps(
                    ans, sort_keys=True, indent=4, separators=(',', ': ')))
        else:
            print(s)

    @staticmethod
    def display(interface=None, verbose=False):
        print("Plugin Instances:", len(PluginGlobals.plugin_instances))
        if interface is not None:
            print("Interface:", interface.name)
            print("Count:",
                  len(PluginGlobals.interface_services.get(interface, [])))
            if verbose:
                for service in interface.services.get(interface, []):
                    print(service)
        else:
            print("Interfaces", len(PluginGlobals.interface_services))
            for interface in PluginGlobals.interface_services:
                print("  Interface:", interface)
                print("  Count:",
                      len(PluginGlobals.interface_services.get(interface, [])))
                if verbose:
                    for service in PluginGlobals.interface_services.get(
                            interface, []):
                        print("     ", PluginGlobals.plugin_instances[service])
        #
        print("")
        for env_ in itervalues(PluginGlobals.env):
            print("Plugin Declarations:", env_.name)
            for interface in sorted(
                    env_.interfaces.keys(), key=lambda v: v.upper()):
                print("Interface:", interface)
                # print "Aliases:"
                # for alias in sorted(interface._factory_cls.keys(),
                #                     key=lambda v: v.upper()):
                #     print "   ",alias,interface._factory_cls[alias]


class InterfaceMeta(type):
    """Meta class that registered the declaration of an interface"""

    def __new__(cls, name, bases, d):
        """Register this interface"""
        new_class = type.__new__(cls, name, bases, d)
        if name != "Interface":
            if name in PluginGlobals.get_env().interfaces:
                raise PluginError("Interface %s has already been defined" %
                                  name)
            PluginGlobals.get_env().interfaces[name] = new_class
        return new_class


class Interface(with_metaclass(InterfaceMeta, object)):
    """Marker base class for extension point interfaces.  This class
    is not intended to be instantiated.  Instead, the declaration
    of subclasses of Interface are recorded, and these
    classes are used to define extension points.
    """
    pass


class IPluginLoader(Interface):
    """An interface for loading plugins."""

    def load(self, env, path, disable_re, name_re):
        """Load plugins found on the specified path.  If disable_re is
        not none, then it is interpreted as a regular expression.  If
        this expression matches the path of a plugin, then that plugin
        is disabled. Otherwise, the plugin is enabled by default.
        """


class IPluginLoadPath(Interface):

    def get_load_path(self):
        """Returns a list of paths that are searched for plugins"""


class IIgnorePluginWhenLoading(Interface):
    """Interface used by Plugin loaders to identify Plugins that should
    be ignored"""

    def ignore(self, name):
        """Returns true if a loader should ignore a plugin during loading"""


class IOptionDataProvider(Interface):
    """An interface that supports the management of common data between
    Options.  This interface is also used to share this data with
    the Configuration class.
    """

    def get_data(self):
        """Returns a dictionary of dictionaries that represents the
        options data."""

    def set(self, section, name, value):
        """Sets the value of a given (section,name) pair"""

    def get(self, section, name):
        """Returns the value of a given (section,name) pair"""

    def clear(self):
        """Clears the data"""


class PluginMeta(type):
    """Meta class for the Plugin class.  This meta class
    takes care of service and extension point registration.  This class
    also instantiates singleton plugins.
    """

    def __new__(cls, name, bases, d):
        """Find all interfaces that need to be registered."""
        #
        # Avoid cycling in the Python logic by hard-coding the behavior
        # for the Plugin and SingletonPlugin classes.
        #
        if name == "Plugin":
            d['__singleton__'] = False
            return type.__new__(cls, name, bases, d)
        if name == "SingletonPlugin":
            d['__singleton__'] = True
            return type.__new__(cls, name, bases, d)
        if name == "ManagedSingletonPlugin":
            #
            # This is a derived class of SingletonPlugin for which
            # we do not need to build an instance
            #
            d['__singleton__'] = True
            return type.__new__(cls, name, bases, d)
        #
        # Check if plugin has already been registered
        #
        if len(d.get('_implements', [])) == 0 and (
                name in PluginGlobals.get_env().plugin_registry):
            return PluginGlobals.get_env().plugin_registry[name]
        #
        # Find all interfaces that this plugin will support
        #
        __interfaces__ = {}
        for interface in d.get('_implements', {}):
            __interfaces__.setdefault(interface,
                                      []).extend(d['_implements'][interface])
        for base in [base for base in bases if hasattr(base, '__interfaces__')]:
            for interface in base.__interfaces__:
                __interfaces__.setdefault(
                    interface, []).extend(base.__interfaces__[interface])
        d['__interfaces__'] = __interfaces__
        #
        # Create a boolean, which indicates whether this is
        # a singleton class.
        #
        if True in [issubclass(x, SingletonPlugin) for x in bases]:
            d['__singleton__'] = True
        else:
            d['__singleton__'] = False
        #
        # Add interfaces to the list of base classes if they are
        # declared inherited.
        #
        flag = False
        bases = list(bases)
        for interface in d.get('_inherited_interfaces', set()):
            if interface not in bases:
                bases.append(interface)
                flag = True
        if flag:
            cls = MergedPluginMeta
        #
        # Create new class
        #
        try:
            new_class = type.__new__(cls, name, tuple(bases), d)
        except:
            raise
        setattr(new_class, '__name__', name)
        #
        for _interface in __interfaces__:
            if getattr(_interface, '_factory_active', None) is None:
                continue
            for _name, _doc, _subclass in getattr(new_class, "_factory_aliases",
                                                  []):
                if _name in _interface._factory_active:
                    if _subclass:
                        continue
                    else:
                        raise PluginError("Alias '%s' has already been "
                                          "defined for interface '%s'" %
                                          (_name, str(_interface)))
                _interface._factory_active[_name] = name
                _interface._factory_doc[_name] = _doc
                _interface._factory_cls[_name] = new_class
        #
        if d['__singleton__']:
            #
            # Here, we create an instance of a singleton class, which
            # registers itself in singleton_services
            #
            PluginGlobals.get_env().singleton_services[new_class] = True
            __instance__ = new_class()
            PluginGlobals.plugin_instances[__instance__._id] = __instance__
            PluginGlobals.get_env().singleton_services[new_class] = \
                __instance__._id
        else:
            __instance__ = None
        #
        # Register this plugin
        #
        PluginGlobals.get_env().plugin_registry[name] = new_class
        return new_class


class MergedPluginMeta(PluginMeta, InterfaceMeta):

    def __new__(cls, name, bases, d):
        return PluginMeta.__new__(cls, name, bases, d)


class Plugin(with_metaclass(PluginMeta, object)):
    """Base class for plugins.  A 'service' is an instance of a Plugin.

    Every Plugin class can declare what extension points it provides, as
    well as what extension points of other Plugins it extends.
    """

    def __del__(self):
        # print "HERE - plugin __del__", self._id, self.name,
        #       self.__class__.__name__
        # ZZZ
        # return
        self.deactivate()
        if (PluginGlobals is not None and
                PluginGlobals.plugin_instances is not None and
                self._id in PluginGlobals.plugin_instances and
                PluginGlobals.plugin_instances[self._id] is not None):
            # print "HERE - plugin __del__", self._id
            # print "interface_services", PluginGlobals.interface_services
            # print "HERE", self.name, self.__class__.__name__
            del PluginGlobals.plugin_instances[self._id]
        if (PluginGlobals is not None and PluginGlobals.env_map is not None and
                self._id_env in PluginGlobals.env_map):
            PluginGlobals.env[PluginGlobals.env_map[
                self._id_env]].nonsingleton_plugins.discard(self._id)

    def __init__(self, **kwargs):
        if "name" in kwargs:
            self.name = kwargs["name"]

    def __new__(cls, *args, **kwargs):
        """Plugin constructor"""
        #
        # If this service is a singleton, then allocate and configure
        # it differently.
        #
        if cls in PluginGlobals.get_env().singleton_services:  # pragma:nocover
            id = PluginGlobals.get_env().singleton_services[cls]
            if id is True:
                self = super(Plugin, cls).__new__(cls)
                PluginGlobals.plugin_counter += 1
                self._id = -PluginGlobals.plugin_counter
                self._id_env = PluginGlobals.get_env().env_id
                self.name = self.__class__.__name__
                self._enable = True
                self.activate()
            else:
                self = PluginGlobals.plugin_instances[id]
            # print "HERE - Plugin singleton:",
            #       self._id, self.name, self._id_env
            return self
        #
        # Else we generate a normal plugin
        #
        self = super(Plugin, cls).__new__(cls)
        PluginGlobals.plugin_counter += 1
        self._id = PluginGlobals.plugin_counter
        self._id_env = PluginGlobals.get_env().env_id
        self.name = "Plugin." + str(self._id)
        PluginGlobals.get_env().nonsingleton_plugins.add(self._id)
        # print "HERE - Normal Plugin:", self._id, self.name,
        #   self.__class__.__name__, self._id_env
        self._enable = True
        PluginGlobals.plugin_instances[self._id] = weakref.ref(self)
        if getattr(cls, '_service', True):
            # self._HERE_ = self._id
            self.activate()
        return self

    def activate(self):
        """Register this plugin with all interfaces that it implements."""
        for interface in self.__interfaces__:
            PluginGlobals.interface_services.setdefault(interface,
                                                        set()).add(self._id)

    def deactivate(self):
        """Unregister this plugin with all interfaces that it implements."""
        # ZZ
        # return
        if PluginGlobals is None or PluginGlobals.interface_services is None:
            # This could happen when python quits
            return
        # for interface in self.__interfaces__:
        # if interface in PluginGlobals.interface_services:
        for interface in PluginGlobals.interface_services:
            # Remove an element if it exists
            PluginGlobals.interface_services[interface].discard(self._id)

    #
    # Support "with" statements. Forgetting to call deactivate
    # on Plugins is a common source of memory leaks
    #
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.deactivate()

    @staticmethod
    def alias(name, doc=None, subclass=False):
        """This function is used to declare aliases that can be used by a
        factory for constructing plugin instances.

        When the subclass option is True, then subsequent calls to
        alias() with this class name are ignored, because they are
        assumed to be due to subclasses of the original class declaration.
        """
        frame = sys._getframe(1)
        locals_ = frame.f_locals
        assert locals_ is not frame.f_globals and '__module__' in locals_, \
            'alias() can only be used in a class definition'
        locals_.setdefault('_factory_aliases', set()).add((name, doc, subclass))

    @staticmethod
    def implements(interface, inherit=None, namespace=None, service=False):
        """Can be used in the class definition of `Plugin` subclasses to
        declare the extension points that are implemented by this
        interface class.
        """
        frame = sys._getframe(1)
        locals_ = frame.f_locals
        #
        # Some sanity checks
        #
        assert namespace is None or isinstance(namespace, str), \
            'second implements() argument must be a string'
        assert locals_ is not frame.f_globals and '__module__' in locals_, \
            'implements() can only be used in a class definition'
        #
        locals_.setdefault('_implements', {}).setdefault(interface,
                                                         []).append(namespace)
        if inherit:
            locals_.setdefault('_inherited_interfaces', set()).add(interface)
        locals_['_service'] = service

    def disable(self):
        """Disable this plugin"""
        self._enable = False

    def enable(self):
        """Enable this plugin"""
        self._enable = True

    def enabled(self):
        """Return value indicating if this plugin is enabled"""
        enable = self._enable
        if hasattr(enable, 'get_value'):
            try:
                enable = enable.get_value()
            except:
                enable = None
        return enable

    def __repr__(self, simple=False):
        """Return a textual representation of the plugin."""
        if simple or self.__class__.__name__ == self.name:
            return '<Plugin %s>' % (self.__class__.__name__)
        else:
            return '<Plugin %s %r>' % (self.__class__.__name__, self.name)


alias = Plugin.alias
implements = Plugin.implements


class SingletonPlugin(Plugin):
    """The base class for singleton plugins.  The PluginMeta class
    instantiates a SingletonPlugin class when it is declared.  Note that
    only one instance of a SingletonPlugin class is created in
    any environment.
    """
    pass


def CreatePluginFactory(_interface):
    if getattr(_interface, '_factory_active', None) is None:
        setattr(_interface, '_factory_active', {})
        setattr(_interface, '_factory_doc', {})
        setattr(_interface, '_factory_cls', {})
        setattr(_interface, '_factory_deactivated', {})

    class PluginFactoryFunctor(object):

        def __call__(self, _name=None, args=[], **kwds):
            if _name is None:
                return self
            _name = str(_name)
            if _name not in _interface._factory_active:
                return None
            return PluginFactory(_interface._factory_cls[_name], args, **kwds)

        def services(self):
            return list(_interface._factory_active.keys())

        def get_class(self, name):
            return _interface._factory_cls[name]

        def doc(self, name):
            tmp = _interface._factory_doc[name]
            if tmp is None:
                return ""
            return tmp

        def deactivate(self, name):
            if name in _interface._factory_active:
                _interface._factory_deactivated[
                    name] = _interface._factory_active[name]
                del _interface._factory_active[name]

        def activate(self, name):
            if name in _interface._factory_deactivated:
                _interface._factory_active[
                    name] = _interface._factory_deactivated[name]
                del _interface._factory_deactivated[name]

    return PluginFactoryFunctor()


def PluginFactory(classname, args=[], **kwds):
    """Construct a Plugin instance, and optionally assign it a name"""

    if isinstance(classname, str):
        try:
            cls = PluginGlobals.get_env(kwds.get('env', None)).plugin_registry[
                classname]
        except KeyError:
            raise PluginError("Unknown class %r" % str(classname))
    else:
        cls = classname
    obj = cls(*args, **kwds)
    if 'name' in kwds:
        obj.name = kwds['name']
    if __debug__ and logger.isEnabledFor(logging.DEBUG):
        if obj is None:
            logger.debug("Failed to create plugin %s" % (classname))
        else:
            logger.debug("Creating plugin %s with name %s" % (classname,
                                                              obj.name))
    return obj
