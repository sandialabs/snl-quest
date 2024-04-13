#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________
"""A plugin that supports configuration of environment options."""

import os.path
import os
import re
import logging

from pyutilib.component.core import Interface, IPluginLoadPath, Plugin, implements
from pyutilib.component.config.options import DictOption, declare_option

logger = logging.getLogger('pyutilib.component.core.pca')


class IEnvironmentConfig(Interface):
    """Interface for environment configuration."""

    def get_option(self, option):
        """Return the value of the specified option."""

    def matches(self, namespace):
        """
        Returns a tuple (flag,count).  The flag is true if this
        environment is a parent of the specified namespace.  If the flag is
        true, then the count is the number of levels in the namespace.
        """


class EnvironmentConfig(Plugin):
    """A plugin that supports configuration of environment options."""

    implements(IEnvironmentConfig)
    implements(IPluginLoadPath)

    def __init__(self, namespace):
        self.namespace = namespace
        self.p = re.compile(namespace)
        declare_option("options", cls=DictOption, section=namespace)

    def get_option(self, option):
        try:
            return getattr(self.options, option)
        except AttributeError:
            return None

    def matches(self, namespace):
        if self.p.match(namespace) is None:
            return (False, 0)
        return (True, namespace.count('.') + 1)

    def get_load_path(self):
        ans = []
        #
        # Look for load_path in the environment
        #
        try:
            ans.append(
                os.path.normcase(os.path.realpath(self.options.load_path)))
        except OptionError:
            pass
        except AttributeError:
            pass
        #
        # Look for the $HOME/.$name/plugin directory
        #
        if "HOME" in os.environ:
            dir = os.path.normcase(
                os.path.realpath(
                    os.path.join(os.environ["HOME"], "." + self.namespace,
                                 "plugins")))
            if os.path.exists(dir):
                ans.append(dir)
        #
        # Look for the $PLUGINPATH environment
        #
        if "PLUGINPATH" in os.environ:
            tmp = os.environ["PLUGINPATH"]
            if ';' in tmp:
                ans += tmp.split(';')
            elif ':' in tmp:
                ans += tmp.split(':')
            else:
                ans += re.split('[ \t]+', tmp)
        if __debug__ and logger.isEnabledFor(logging.DEBUG):
            logger.debug("Created load path: %s" % ans)
        return ans
