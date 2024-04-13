#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________

# This software is adapted from the Trac software (specifically, the trac.core
# module.  The Trac copyright statement is included below.

__all__ = ['ImportLoader']

from glob import glob
import imp
import re
import os
import sys
import logging

from pyutilib.component.config import ManagedSingletonPlugin
from pyutilib.component.core import implements, ExtensionPoint, IIgnorePluginWhenLoading, IPluginLoader, Plugin


class ImportLoader(ManagedSingletonPlugin):
    """Loader that looks for Python source files in the plugins directories,
    which simply get imported, thereby registering them with the component
    manager if they define any components.
    """

    ep_services = ExtensionPoint(IIgnorePluginWhenLoading)

    implements(IPluginLoader)

    def load(self, env, search_path, disable_re, name_re):
        generate_debug_messages = __debug__ and env.log.isEnabledFor(
            logging.DEBUG)
        env.log.info('Loading plugins with ImportLoader')
        for path in search_path:
            plugin_files = glob(os.path.join(path, '*.py'))
            #
            # Note: for reproducibility, this fixes the order that
            # files are loaded
            #
            for plugin_file in sorted(plugin_files):
                #print("ImportLoader:",plugin_file)
                #
                # Load the module
                #
                module = None
                plugin_name = os.path.basename(plugin_file[:-3])
                if plugin_name not in sys.modules and name_re.match(
                        plugin_name):
                    try:
                        module = imp.load_source(plugin_name, plugin_file)
                        if generate_debug_messages:
                            env.log.debug('Loading file plugin %s from %s' % \
                                  (plugin_name, plugin_file))
                    except Exception:
                        e = sys.exc_info()[1]
                        env.log.error(
                            'Failed to load plugin from %s',
                            plugin_file,
                            exc_info=True)
                        env.log.error('Load error: %r' % str(e))
                #
                # Disable singleton plugins that match
                #
                if not module is None:
                    if not disable_re.match(plugin_name) is None:
                        if generate_debug_messages:
                            env.log.debug('Disabling services in module %s' %
                                          plugin_name)
                        for item in dir(module):
                            #
                            # This seems like a hack, but
                            # without this we can disable pyutilib
                            # functionality!
                            #
                            flag = False
                            for service in ImportLoader.ep_services:
                                if service.ignore(item):
                                    flag = True
                                    break
                            if flag:
                                continue

                            cls = getattr(module, item)
                            try:
                                is_instance = isinstance(cls, Plugin)
                            except TypeError:  #pragma:nocover
                                is_instance = False
                            try:
                                is_plugin = issubclass(cls, Plugin)
                            except TypeError:
                                is_plugin = False
                            try:
                                is_singleton = not (cls.__instance__ is None)
                            except AttributeError:  #pragma:nocover
                                is_singleton = False
                            if is_singleton and is_plugin:
                                if generate_debug_messages:
                                    env.log.debug('Disabling service %s' % item)
                                cls.__instance__._enable = False
                            if is_instance:
                                if generate_debug_messages:
                                    env.log.debug('Disabling service %s' % item)
                                cls._enable = False
                    elif generate_debug_messages:
                        env.log.debug('All services in module %s are enabled' %
                                      plugin_name)

# Copyright (C) 2005-2008 Edgewall Software
# Copyright (C) 2005-2006 Christopher Lenz <cmlenz@gmx.de>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution. The terms
# are also available at http://trac.edgewall.org/wiki/TracLicense.
#
# This software consists of voluntary contributions made by many
# individuals. For the exact contribution history, see the revision
# history and logs, available at http://trac.edgewall.org/log/.
#
# Author: Christopher Lenz <cmlenz@gmx.de>
