#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________
"""
The outline of the PyUtilib Component Architecture (PCA) is adapted from Trac
(see the trac.core module).  This framework generalizes the Trac by supporting
multi-environment management of components, as well as non-singleton plugins.

This package provides a stand-alone module that defines all of the core
aspects of the PCA.  Related Python packages define extensions of this
framework that support current component-based applications.

NOTE: The PCA does not rely on any other part of PyUtilib.  Consequently,
this package can be independently used in other projects.
"""

from pyutilib.component.core.core import (
    Plugin, implements, Interface, CreatePluginFactory,
    PluginMeta, alias, ExtensionPoint, SingletonPlugin,
    PluginFactory, PluginError, PluginGlobals, with_metaclass,
    IPluginLoader, IPluginLoadPath, IIgnorePluginWhenLoading,
    IOptionDataProvider, PluginEnvironment
)

#
# This declaration is here because this is a convenient place where
# all symbols in this module have been defined.
#

class IgnorePluginPlugins(SingletonPlugin):
    """Ignore plugins from the pyutilib.component module"""

    implements(IIgnorePluginWhenLoading)

    def ignore(self, name):
        return name in globals()
