#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________
"""
This package defines the Configuration class, which provides a generic interface for reading/writing configuration files.  This class uses a simple
model for configuration data:

  section -> option -> value

A key role of this class is to support initialization of Option objects.
"""

import os.path
from pyutilib.component.core import PluginError, Interface, Plugin, ExtensionPoint, implements, IOptionDataProvider
from pyutilib.component.config.options import IOption, IFileOption, IUpdatedOptionsAction


class ConfigurationError(PluginError):
    """Exception raised when a value in the configuration file is not valid."""


class IConfiguration(Interface):
    """Define an interface for classes that are used by Configuration to
    read/write configuration data."""

    def load(self, filename):
        """Returns a list of tuples: [ (section,option,value) ]"""

    def save(self, filename, config):
        """Save configuration information to the specified file."""


class Configuration(Plugin):
    """This class manages configuration data.  Further, this configuration
    I/O is coordinated with Option objects.  When configuration data is read
    in, associated Option plugins are populated.  Similarly, when
    configuration data is writen, the configuration data is taken from
    Option data."""

    def __init__(self, filename=None, parser="ConfigParser"):
        """Constructor.
            @param filename - The associated configuration file.
            @param parser   - Specify the name of the parser used to
                read/write configuration files.
        """
        self.parser_type = "Configuration_ConfigParser"
        self.filename = filename
        #
        # Define extension points
        #
        self.parsers = ExtensionPoint(IConfiguration)
        self.option_plugins = ExtensionPoint(IOption)
        self.option_data_plugin = ExtensionPoint(IOptionDataProvider)
        self.pathoption_plugins = ExtensionPoint(IFileOption)
        self.postconfig_actions = ExtensionPoint(IUpdatedOptionsAction)
        self.clear()

    def clear(self):
        """Clear local data."""
        self.config = []
        self.data = {}
        self.section = []

    def __contains__(self, name):
        """Return whether the configuration contains a section of the given
        name.
        """
        return name in self.data

    def __getitem__(self, name):
        """Return the configuration section with the specified name."""
        if name not in self.data:
            raise ConfigurationError("No section " + name + " in data")
        return self.data[name]

    def sections(self):
        """Returns the names of all sections in the configuration data."""
        return list(self.data.keys())

    def load(self, filename=None):
        """Load configuration from a file."""
        if len(self.parsers) == 0:  #pragma:nocover
            raise ConfigurationError("No IConfiguration parsers are registered")
        if not filename is None:
            self.filename = filename
        if self.filename is None:
            raise ConfigurationError("Cannot load without a filename")
        for option in self.pathoption_plugins:
            option.set_dir(os.path.dirname(self.filename))
        #
        # By default, we simply take the first parser
        #
        self.config = self.parsers.service(self.parser_type).load(self.filename)
        self.data = {}
        self.section = []
        for (s, o, v) in self.config:
            if not s in self.data:
                self.section.append(s)
                self.data[s] = {}
            if not o in self.data[s]:
                self.data[s][o] = []
            self.data[s][o].append(v)
        #
        # Iterate through all sections, in the order they were
        # loaded.  Load data for extensions that match each section name.
        #
        for sec in self.section:
            #
            # Find the option_plugins that match this section
            #
            plugins = []
            for plugin in self.option_plugins:
                if plugin.matches_section(sec):
                    plugins.append(plugin)
            for option in self.data[sec]:
                flag = False
                for plugin in plugins:
                    if plugin.matches_name(option):
                        flag = plugin.load(option,
                                           self.data[sec][option]) or flag
                if not flag:
                    raise ConfigurationError(
                        "Problem loading file %r. Option %r in section %r is not recognized!"
                        % (self.filename, option, sec))
        #
        # Finalize the configuration process
        #
        for plugin in self.postconfig_actions:
            plugin.reset_after_updates()

    def save(self, filename=None):
        """Save configuration to a file."""
        if not filename is None:
            self.filename = filename
        if self.filename is None:
            raise ConfigurationError("Cannot save without a filename")
        #
        # Setup the list of tuples
        #
        self.clear()
        self.data = self.option_data_plugin.service().get_data()
        self.section = list(self.data.keys())
        self.section.sort()
        flag = False
        header = "\nNote: the following configuration options have been omitted because their\nvalue is 'None':\n"
        for sec in self.section:
            plugins = []
            for plugin in self.option_plugins:
                if plugin.matches_section(sec):
                    plugins.append(plugin)
            #
            options = list(self.data[sec].keys())
            options.sort()
            for option in options:
                for plugin in plugins:
                    if plugin.matches_name(option):
                        if not self.data[sec][option] is None:
                            val = self.data[sec][option]
                            self.config.append((sec, option, val))
                        else:
                            flag = True
                            header = header + "  section=%r option=%r\n" % (
                                sec, option)
                        break
        if flag:
            header = header + "\n"
        else:
            header = None
        #
        # Write config file
        #
        self.parsers.service(self.parser_type).save(self.filename, self.config,
                                                    header)

    def pprint(self):
        """Print a simple summary of the configuration data."""
        text = ""
        for (s, o, v) in self.config:
            text += "[%s] %s = %s\n" % (s, o, v)
        print(text)

    def summarize(self):
        """Summarize options"""
        tmp = {}
        for option in self.option_plugins:
            tmp.setdefault(option.section, {})[option.name] = option
        keys = list(tmp.keys())
        keys.sort()
        for key in keys:
            print("[" + key + "]")
            print("")
            okeys = list(tmp[key].keys())
            okeys.sort()
            for okey in okeys:
                print("  Option:    " + tmp[key][okey].name)
                print("  Type:      " + tmp[key][okey].__class__.__name__)
                print("  Default:   " + tmp[key][okey].default_str())
                print("  Doc:       " + tmp[key][okey].__doc__)
                print("")
            print("")
