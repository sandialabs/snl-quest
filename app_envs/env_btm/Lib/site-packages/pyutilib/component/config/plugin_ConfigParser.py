#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________
"""A parser used by the Configuration class."""

__all__ = ['Configuration_ConfigParser']

import os.path
try:
    from ordereddict import OrderedDict
except:
    OrderedDict = dict
from pyutilib.component.core import implements
from pyutilib.component.config.configuration import ConfigurationError, IConfiguration
from pyutilib.component.config.managed_plugin import ManagedSingletonPlugin
from pyutilib.component.config.options import declare_option

def _configParser(**kwds):
    try:
        import ConfigParser
    except ImportError:
        import configparser as ConfigParser
    #
    # Force the config file option manager to be case sensitive
    #
    ConfigParser.RawConfigParser.optionxform = str
    return ConfigParser.ConfigParser(**kwds)

class Configuration_ConfigParser(ManagedSingletonPlugin):
    """A configuration parser that uses the ConfigParser package."""

    implements(IConfiguration)

    def __init__(self, **kwds):
        kwds['name'] = 'Configuration_ConfigParser'
        ManagedSingletonPlugin.__init__(self, **kwds)

    def load(self, filename):
        """Returns a list of tuples: [ (section,option,value) ]"""
        parser = _configParser()
        if not os.path.exists(filename):
            raise ConfigurationError("File " + filename + " does not exist!")
        parser.read(filename)
        #
        # Collect data
        #
        data = []
        for section in parser.sections():
            for (option, value) in parser.items(section):
                data.append((section, option, value))
        return data

    def save(self, filename, config, header=None):
        """Save configuration information to the specified file."""
        parser = _configParser()
        for (section, option, value) in config:
            if not parser.has_section(section):
                parser.add_section(section)
            parser.set(section, option, str(value))
        OUTPUT = open(filename, "w")
        if not header is None:
            for line in header.split("\n"):
                OUTPUT.write("; " + line + '\n')
        parser.write(OUTPUT)
        OUTPUT.close()
