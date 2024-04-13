#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________
"""
The Option class provides a mechanism for application classes to transparently
load configuration data.  For example, the consider the following class declaration:

  class FOO(Option):

    declare_option("x", local_name="bar")

    def __init__(self):
        self.x = FOO.bar

The FOO class contains a declaration 'bar', which is initialized by loading
a Configuration object.

"""

import weakref
import sys
import re
import os
import os.path
from pyutilib.component.core import PluginError, Interface, implements, Plugin, PluginGlobals, ExtensionPoint, IOptionDataProvider
try:
    unicode
except:
    basestring = str


class OptionError(PluginError):
    """Exception raised when there is an error processing an option."""


class IOption(Interface):
    """An interface that supports the initialization of Option objects
    from a Configuration object."""

    def matches_section(self, section):
        """Returns True if this option matches the section name."""

    def matches_name(self, section):
        """Returns True if this option matches the option name."""

    def load(self, option, value):
        """Loads this option, if it matches the option name.  Returns True
        if the option is loaded, and False otherwise."""

    def get_value(self):
        """Return the value of this option"""

    def default_str(self):
        """Return a string value that describes the default option value"""

    def reset(self):
        """Reset all options to their default values."""


class IUpdatedOptionsAction(Interface):
    """Define actions that are applied after options have been updated."""

    def reset_after_updates(self):
        """Perform actions that use updated option data."""


class IFileOption(Interface):
    """An interface that supports the initialization of the directory for
    options that specify files.  This is needed to correctly initialize
    relative paths for files."""

    def set_dir(self, path):
        """Sets the directory of the configuration data file."""


class OptionData(Plugin):
    """
    A class that is used to share option data between Option objects.
    This data in this class represents option data as

        section -> option -> data

    Note: this class does not currentl support the situation where an
    option is removed.  This would require a backwards map from option
    names to the Option classes that declare them.
    """

    implements(IOptionDataProvider, service=True)

    def __init__(self):
        """Constructor"""
        self.ignore_missing = False
        self.data = {}

    def get_data(self):
        """Get the class data"""
        return self.data

    def set(self, section, name, value):
        """Set the value of an option in a specified section"""
        if section not in self.data:
            self.data[section] = {}
        self.data[section][name] = value

    def get(self, section, name):
        """Get the value of an option in a specified section"""
        try:
            return self.data[section][name]
        except Exception:
            if self.ignore_missing:
                return None
            if section in self.data:
                raise OptionError(
                    "Problem retrieving the value of option %r from section %r. Valid keys are %s"
                    % (name, section, self.data[section].keys()))
            else:
                raise OptionError(
                    "Problem retrieving the value of option %r from section %r. Undefined section."
                    % (name, section))

    def clear(self, keys=None):
        """Clears the data"""
        if keys is None:
            self.data = {}
        else:
            for key in keys:
                if not key in self.data:
                    continue
                del self.data[key]


class OptionPlugin(Plugin):
    """Manages the initialization of an Option."""

    implements(IOption, service=True)

    def __init__(self):
        """
        Declare an extension point for a data provider, and
        construct one if one hasn't already been provided.
        """
        self.data = ExtensionPoint(IOptionDataProvider)
        if PluginGlobals._default_OptionData is None:
            PluginGlobals._default_OptionData = OptionData()
        #
        # This is a hack.  We shouldn't need to test if len(self.data) is zero.
        # Somewhere in our tests, the weakref to the OptionData object is being 
        # corrupted.  Perhaps this is caused by 'nose' or 'import' logic?
        #
        if True and len(self.data) == 0:
            PluginGlobals.interface_services[IOptionDataProvider].add(
                PluginGlobals._default_OptionData._id)
            PluginGlobals.plugin_instances[
                PluginGlobals._default_OptionData._id] = weakref.ref(
                    PluginGlobals._default_OptionData)
        #
        if len(self.data) == 0:
            #if False:
            #print "ZZZ", ep.Xextensions()
            #print "HERE", PluginGlobals._default_OptionData._id, PluginGlobals._default_OptionData.ctr
            #print "HERE", PluginGlobals._default_OptionData
            #print "HERE - id", id(PluginGlobals._default_OptionData)
            #print "HERE", getattr(PluginGlobals._default_OptionData, '_HERE_', None)
            #print "HERE", PluginGlobals._default_OptionData.__interfaces__
            #print ""
            #print "HERE", PluginGlobals.interface_services
            #print "HERE", PluginGlobals.plugin_instances.keys()
            #for exe_ in PluginGlobals._executables:
            #print exe_._id, exe_
            #print "LEN", len(PluginGlobals.env)
            #for name_ in PluginGlobals.env:
            #env_ = PluginGlobals.env[name_]
            #print env_.name
            #print env_.nonsingleton_plugins
            #print [env_.singleton_services[cls_] for cls_ in env_.singleton_services]
            raise PluginError(
                "Problem constructing a global OptionData object %s" %
                self.name)

    def matches_section(self, section):
        """
        This method returns true if the section name matches the option
        section, or if the option's section regular expression matches the
        section name.
        """
        return (section == self.section) or (self.section_re != None and (
            not self.section_p.match(section) is None))

    def matches_name(self, name):
        """
        This method returns true if the name matches the options' name.
        """
        return (self.name == "") or (name == self.name)

    def convert(self, value, default):
        """Convert a value into a specific type.  The default behavior is to
        take the list of values, and simply return the last one defined in the
        configuration."""
        return value[-1]

    def get_value(self):
        """
        Get the option value.
        """
        return self.data.service().get(self.section, self.name)

    def set_value(self, _value_, raw=False):
        """
        Set the option value.  By default, the option is converted using
        the option-specific `convert` method, but the `raw` option can be
        specified to force the raw value to be inserted.
        """
        if raw:
            self.data.service().set(self.section, self.name, _value_)
        else:
            if not type(_value_) is list or len(_value_) == 0:
                _value_ = [_value_]
            self.data.service().set(self.section, self.name, self.convert(
                _value_, self.default))

    def load(self, _option_, _value_):
        """
        Load an option value.  This method assumes that the option value is
        provided in a list, which is the format used when interfacing with
        the Configure class.
        """
        if type(_value_) is list and len(_value_) == 0:
            raise OptionError("Attempting to load option %r with empty data" %
                              (self.name))
        try:
            self.set_value(_value_)
        except OptionError:
            err = sys.exc_info()[1]
            raise OptionError("Error loading option %r: %s" %
                              (str(_option_), str(err)))
        return True

    def reset(self):
        """Set option to its default value"""
        self.set_value(self.default, raw=True)

    def default_str(self):
        """Return a string value that describes the default option value"""
        return str(self.default)


class Option(OptionPlugin):
    """Descriptor for configuration options.

    This class uses an OptionPlugin instance to support initialization of
    the option.  However, the OptionPlugin instance is given a handle on
    the Option instance to perform this initialization.  This allows for the
    explicit referencing of this object's data, as well as referencing the
    conversion routines that are specified in subclasses of Option.
    """

    def __init__(self, name=None, **kwds):
        """Create the extension point.

        @param name: the name of the option
        @param section: the name of the configuration section this option
            belongs to
        @param default: the default value for the option
        @param doc: documentation of the option
        """
        self.section = "globals"
        super(Option, self).__init__()
        self.section_re = None
        self.name = name
        self.default = None
        self.__doc__ = ""
        for (k, v) in kwds.items():
            self._parse_option(k, v)
        if name is None:
            raise OptionError("The Option class requires a name")
        self.reset()

    def _parse_option(self, k, v):
        """Parse option"""
        if k == "section":
            self.section = v
        elif k == "section_re":
            self.section_re = v
            self.section_p = re.compile(v)
        elif k == "default":
            self.default = v
        elif k == "doc":
            self.__doc__ = v
        elif not k in ("local_name"):
            #
            # It's convenient to ignore several keywords, which are really used by
            # declare_option().
            #
            raise OptionError("Unknown keyword: " + k)

    def __get__(self, instance, owner):
        raise PluginError(
            "The Option class cannot be used as a class decorator")

    def __set__(self, instance, value):
        raise PluginError(
            "The Option class cannot be used as a class decorator")

    def __repr__(self, simple=False):
        """Returns a string representation of the option name"""
        sec = " [" + self.section + "]"
        return '<%s%s %r>' % (self.__class__.__name__, sec, self.name)


class VirtualOption(object):
    """
    This class is the decorator that is used to declare an option.  To use
    an option, each instance must declare an Option object.
    """

    def __init__(self, name, option=None):
        self.name = name
        self.option = option

    def _get_option(self, instance):
        if not self.option is None:
            return self.option
        try:
            return getattr(instance, self.name)
        except AttributeError:
            raise PluginError(
                "Expected attribute %r in instance %r.  The declare_option() method was not called in the constructor!"
                % (self.name, instance))

    def __get__(self, instance, owner):
        """Returns the value of the option, accessed through the local instance."""
        if owner is None:  #pragma:nocover
            return self
        return self._get_option(instance).get_value()

    def __set__(self, instance, value):
        """Sets the value of the option"""
        self._get_option(instance).set_value(value)

    def __repr__(self, simple=False):
        """Returns a string representation of the option name"""
        return "<VirtualOption %s>" % self.name


def declare_option(name, cls=Option, **kwds):
    if not issubclass(cls, Option):
        raise PluginError(
            "The 'cls' argument must specify an Option class type: %s" % cls)
    local_name = kwds.get("local_name", name)

    frame = sys._getframe(1)
    locals_ = frame.f_locals
    #print "HERE", locals_ is not frame.f_globals, '__module__' in locals_
    if locals_ is not frame.f_globals:
        kwds["name"] = name
        option_ = cls(**kwds)
        if '__module__' in locals_:
            #
            # Class decorator.  Initialize the VirtualOption, and then
            # create a locally-available Option instance.
            #
            locals_[local_name] = VirtualOption("_" + local_name, option_)
        else:
            #
            # Class constructor.  If a VirtualOption does not exist in this
            # class, create it.  Create an Option instance in this instance.
            #
            if not local_name in locals_["self"].__class__.__dict__:
                setattr(locals_["self"].__class__, local_name,
                        VirtualOption("_" + local_name))
            setattr(locals_["self"], "_" + local_name, option_)
    else:
        raise PluginError(
            "declare_option() can only be used in a class definition")


class DictOption(Option):
    """
    An option that supports an interface to _all_ options in a section.
    For example, consider the following class:

        class FOO(object):

            options = DictOption(section="bar")

    The `options` object will be populated by all data in the `bar` section.
    For example, if the values `a` and `b` are in this section, then they can
    be referenced as `foo.a` and `foo.b`.  Similarly, data can be inserted
    into the `bar` section by specifying the value of attributes of options:

        options.c = 1

    """

    class SectionWrapper(object):
        """
        A class that is used to manage attribute access to a DictOption
        instance.  This class uses IOptionDataProvider extension points
        to directly access shared Option data.
        """

        def __init__(self, section, ignore_missing=False):
            self._section_ = section
            ep = ExtensionPoint(IOptionDataProvider)
            ep.service().ignore_missing = ignore_missing
            self.__dict__["data"] = ep

        def __iter__(self):
            if not self._section_ in self.data.service().data:
                return {}.__iter__()
            return self.data.service().data[self._section_].__iter__()

        def __getitem__(self, name):
            return self.data.service().get(self._section_, name)

        def keys(self):
            if not self._section_ in self.data.service().data:
                return []
            return self.data.service().data[self._section_].keys()

        def __getattr__(self, name):
            try:
                return self.__dict__[name]
            except:
                return self.data.service().get(self._section_, name)

        def __setattr__(self, name, value):
            if name[0] == "_":
                self.__dict__[name] = value
            else:
                self.data.service().set(self._section_, name, value)

    def __init__(self, **kwds):
        """Constructor."""
        kwds["name"] = ""
        if 'ignore_missing' in kwds:
            ignore_missing = kwds['ignore_missing']
            del kwds['ignore_missing']
        else:
            ignore_missing = False
        super(DictOption, self).__init__(**kwds)
        self.default = DictOption.SectionWrapper(
            self.section, ignore_missing=ignore_missing)

    def get_value(self):
        """Returns the default value."""
        return self.default

    def set_value(self, _value_, raw=False):
        """
        If the value is a dictionary, then it is evaluated to populate
        corresponding data in the options data.

        NOTE: the raw option is ignored, but maintained for compatibility with the
        parent class.
        """
        if not type(_value_) is dict:
            return
        for key in _value_:
            self.default.__setattr__(key, _value_[key])

    def load(self, _option_, _value_):
        """
        Data is loaded one option/value pair at a time, so this
        method circumvents the core logic of this class.
        """
        self.data.service().set(self.section, _option_, _value_[-1])
        return True

    def default_str(self):
        """Return a string value that describes the default option value"""
        return "None (this dictionary consists of all values in this section)"


class BoolOption(Option):
    """A class that converts option data into boolean values."""

    _TRUE_VALUES = ('yes', 'true', 'enabled', 'on', 'aye', '1', 1, True)

    def convert(self, value, default):
        """Conversion routine."""
        val = value[-1]
        if isinstance(val, basestring):
            val = val.lower() in BoolOption._TRUE_VALUES
        return bool(val)


class IntOption(Option):
    """A class that converts option data into integer values."""

    def convert(self, value, default):
        """Conversion routine."""
        val = value[-1]
        if not val:
            return 0
        try:
            return int(val)
        except ValueError:
            raise OptionError('Expected integer, got %s' % repr(value))
        except TypeError:
            raise OptionError('Expected string or integer type, got %s' %
                              repr(value))


class FloatOption(Option):
    """A class that converts option data into float values."""

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


class FileOption(Option):
    """A class that converts option data into a path.  Relative paths are
    converted using the path for the configuration file."""

    implements(IFileOption, service=True)
    implements(IUpdatedOptionsAction, service=True)

    def __init__(self, name, **kwds):
        """
        Constructor.  By default, the current working directory is the
        path used in this data.
        """
        self.dir = None
        Option.__init__(self, name, **kwds)

    def _parse_option(self, k, v):
        """Parse options that are specific to the FileOption class"""
        if k == "directory":
            self.dir = v
        else:
            Option._parse_option(self, k, v)

    def convert(self, value, default):
        """Conversion routine."""
        val = value[-1]
        if not val:
            if default is None:
                return None
            return os.path.normcase(os.path.realpath(default))
        if not os.path.isabs(val):
            val = os.path.join(self.dir, val)
            return os.path.normcase(os.path.realpath(val))
        else:
            return os.path.normcase(os.path.realpath(val))

    def set_dir(self, path):
        """Sets the path of the configuration data file."""
        self.dir = path

    def reset_after_updates(self):
        if self.dir is None:  #pragma:nocover
            raise OptionError("FileOption must have a directory specified.")


class ExecutableOption(FileOption):

    def convert(self, value, default):
        """Conversion routine."""
        val = FileOption.convert(self, value, default)
        if val is None or not os.access(val, os.X_OK):
            raise OptionError(
                "ExecutableOption value %r is not a file that can be executed" %
                val)
        return val

    def convert(self, value, default):
        """Conversion routine."""
        val = value[-1]
        if not val:
            if default is None:
                return None
            val = os.path.normcase(os.path.realpath(default))
        elif os.path.isabs(val):
            val = os.path.normcase(os.path.realpath(val))
        elif not self.dir is None:
            val = os.path.normcase(
                os.path.realpath(os.path.join(self.dir, val)))
        else:
            flag = False
            for path in os.environ.get("PATH", []).split(os.pathsep):
                if os.path.exists(os.path.join(path, val)):
                    val = os.path.normcase(
                        os.path.realpath(os.path.join(path, val)))
                    flag = True
                    break
            if not flag:
                return None
        #
        # Confirm that the executable can be solved
        #
        if val is None or not os.access(val, os.X_OK):
            raise OptionError(
                "ExecutableOption value %r is not a file that can be executed" %
                val)

    def reset_after_updates(self):
        pass
