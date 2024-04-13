#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________
"""
This is a convenience class that configures the PyUtilib Component Architecture
for a named application.  This class registers and activates a variety of
plugins that are commonly used in simple applications.
"""

import pyutilib.component.core
import pyutilib.component.config
import os


class SimpleApplication(object):

    def __init__(self, name, filename=None):
        self.name = name
        if filename is None:
            self.filename = 'config.ini'
        else:
            self.filename = filename
        self.env = pyutilib.component.core.PluginGlobals.add_env(self.name)
        self.config = pyutilib.component.config.Configuration(filename)
        self._env_config = pyutilib.component.config.EnvironmentConfig(name)
        self._env_config.options.path = os.getcwd()
        self.logger = pyutilib.component.config.LoggingConfig(name)
        self._egg_plugin = pyutilib.component.core.PluginFactory(
            "EggLoader", namespace=name, env='pca')

    def configure(self, filename):
        """Load a configuration file, and update options"""
        self.config.load(filename)

    def save_configuration(self, filename):
        """Save a configuration file"""
        self.config.save(filename)

    def exit(self):
        """Perform cleanup operations"""
        self.logger.shutdown()

    def log(self, message):
        """Generate logging output"""
        self.logger.log(message)

    def flush(self):
        """Flush the log output"""
        self.logger.flush()
