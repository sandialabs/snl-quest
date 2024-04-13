#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________
"""Plugins that contain options that support configuration of their services."""

__all__ = ['ManagedPlugin', 'ManagedSingletonPlugin']

from pyutilib.component.core import Plugin, SingletonPlugin
from pyutilib.component.config.options import declare_option, BoolOption


class ManagedPlugin(Plugin):
    """A plugin that has an option supports configuration of this service."""

    def __init__(self, **kwds):
        Plugin.__init__(self, **kwds)
        #super(ManagedPlugin,self).__init__(**kwds)
        declare_option(
            name=self.name,
            section="Services",
            local_name="enable",
            default=self._enable,
            cls=BoolOption,
            doc="Option that controls behavior of service %s." % self.name)

    def __del__(self):
        # JPW: There has to be a better way to determine/cache the name of the option created in the 
        #      constructor call. For example, declare_option might return the name of the created attribute.
        #      In the mean time, I have hard-coded the (known) name.

        # clean up the attached BoolOption, which is a plugin - otherwise, a memory leak will result.
        self._enable.deactivate()


class ManagedSingletonPlugin(SingletonPlugin):
    """A singleton plugin that has an option supports configuration of this service."""

    def __init__(self, **kwds):
        Plugin.__init__(self, **kwds)
        #super(ManagedSingletonPlugin,self).__init__(**kwds)
        declare_option(
            name=self.name,
            section="Services",
            local_name="enable",
            default=self._enable,
            cls=BoolOption,
            doc="Option that controls behavior of service %s." % self.name)
