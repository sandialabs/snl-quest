#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________

__all__ = ['Resource']

from pyutilib.workflow import globals


class Resource(object):

    def __init__(self, id=None, name=None):
        if not id is None:
            # TBD:  does this ever happen?
            self.id = id
        else:
            self.id = globals.unique_id()
        if name is None:
            self.description = "Resource" + str(self.id)
            self.name = self.description
        else:
            # TBD:  does this ever happen?
            self.description = name
            self.name = name
        self._busy = False

    def available(self):
        return not self._busy  #pragma:nocover

    def lock(self):
        self._busy = True  #pragma:nocover

    def unlock(self):
        self._busy = False  #pragma:nocover

    def __repr__(self):
        return str(self)  #pragma:nocover

    def __str__(self):
        return "%s" % str(self.name)  #pragma:nocover
