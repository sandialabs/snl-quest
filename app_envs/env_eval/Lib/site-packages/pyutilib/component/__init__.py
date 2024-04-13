#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________
#
from . import core

#
# Import the 'pyutilib.component' plugins
#
core.PluginGlobals.add_env("pca")

from . import config
from . import executables
from . import loader
from . import app

#
# Remove the "pca" environment as the default
#
core.PluginGlobals.pop_env()
