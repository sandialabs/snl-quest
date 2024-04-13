__all__ = ['FileResource']

import os.path
from pyutilib.workflow import resource


class FileResource(resource.Resource):

    def __init__(self, name=None):
        resource.Resource.__init__(self)
        self.filename = name
        if name is None:
            self.name = "File" + self.id
        else:
            self.name = "File_" + os.path.basename(name)
