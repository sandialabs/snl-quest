#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________

__all__ = ['registered_executable', 'register_executable', 'TempfileManager']

from pyutilib.component.core import ExtensionPoint, PluginGlobals
from pyutilib.component.config import TempfileManager
from pyutilib.component.executables import IExternalExecutable, ExternalExecutable
"""
Test if an exectuable is registered, using the IExternalExecutable extension
point.

If 'name' is None, then return a list of the names of all registered
executables that are enabled.

If either this executable is not registered or it is disabled, then
None is returned.
"""


def registered_executable(name=None):
    ep = ExtensionPoint(IExternalExecutable)
    if name is None:
        return filter(lambda x: x.name, ep.extensions())
    return ep.service(name)


"""
Register an executable, using the IExternalExecutable extension
point.

If this executable has been registered, then do not reregister it
(even if it is disabled).
"""


def register_executable(name, validate=None):
    ep = ExtensionPoint(IExternalExecutable)
    if len(ep(name, all=True)) == 0:
        PluginGlobals.add_env("pca")
        PluginGlobals._executables.append(
            ExternalExecutable(
                name=name, validate=validate))
        PluginGlobals.pop_env()
    else:
        #
        # If the executable is being 'registered', then we search for it
        # again, since the user environment may have changed.
        #
        list(ep(name, all=True))[0].find_executable()
