__all__ = ['ExecutableResource']

import os.path
from pyutilib.workflow import resource
import pyutilib.services
import pyutilib.subprocess

# TODO: add support for logging


class ExecutableResource(resource.Resource):

    def __init__(self, name=None, executable=None):
        resource.Resource.__init__(self)
        if name is None and not executable is None:
            name = os.path.basename(executable)
        if executable is None:
            executable = name
        self.register(name, executable)

    def register(self, name, executable):
        self.filename = executable
        if name is None:
            # TBD: when is this branch executed?
            self.description = "Executable" + self.id
            self.name = self.description
        else:
            self.description = "Executable_" + name
            self.name = name
        pyutilib.services.register_executable(executable)

    def run(self, args, logfile=None, debug=False):
        executable = pyutilib.services.registered_executable(self.filename)
        if executable is None:
            # TBD: tests generating this error do not cause global exceptions in a workflow ...
            raise IOError("Cannot find executable '%s'" % self.filename)
        cmd = executable.get_path() + " " + args
        if debug:
            print("Running... %s" % cmd)
        pyutilib.subprocess.run(cmd, outfile=logfile)

    def available(self):
        return not pyutilib.services.registered_executable(
            self.filename) is None
