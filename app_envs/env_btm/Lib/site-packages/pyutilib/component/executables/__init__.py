#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________

from pyutilib.component.core import PluginGlobals
PluginGlobals.add_env("pca")

from pyutilib.component.executables.executable import IExternalExecutable, ExternalExecutable

PluginGlobals.pop_env()
