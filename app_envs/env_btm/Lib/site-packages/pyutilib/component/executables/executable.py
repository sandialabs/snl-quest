#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________

import pyutilib.misc
from pyutilib.component.core import Interface, Plugin, implements
from pyutilib.component.config import ExecutableOption, declare_option


class IExternalExecutable(Interface):
    """Interface for plugins that define an external executable"""

    def get_path(self):
        """Returns a string that is the path of the executable"""


class ExternalExecutable(Plugin):

    implements(IExternalExecutable, service=True)

    def __init__(self, **kwds):
        if 'doc' in kwds:
            self.exec_doc = kwds["doc"]
        else:
            self.exec_doc = ""
        if 'name' in kwds:
            self.name = kwds['name']
            declare_option(
                kwds['name'],
                local_name="executable",
                section="executables",
                default=None,
                doc=self.exec_doc,
                cls=ExecutableOption)
        else:
            raise PluginError("An ExternalExectuable requires a name")
        if 'path' in kwds:
            self.path = kwds['path']
        else:
            self.path = None
        if 'validate' in kwds:
            self.validate = kwds['validate']
        else:
            self.validate = None
        self.find_executable()

    def find_executable(self):
        if not self.path is None:
            self.exec_default = self.path
        else:
            self.exec_default = pyutilib.misc.search_file(
                self.name,
                implicitExt=pyutilib.misc.executable_extension,
                executable=True,
                validate=self.validate)

    def enabled(self):
        return self._enable and ((self.executable is not None) or
                                 (self.exec_default is not None))

    def get_path(self):
        if not self.enabled():
            return None
        tmp = self.executable
        if tmp is None:
            return self.exec_default
        return tmp
