#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________


def add_method(self, method, name=None):
    """
    Add a method to a class:

      self   - the object that is modified
      method - a function
      name   - a string that describes the new method name

    Adapted from code submitted by Moshe Zadka to the
    ActiveState Programmer Network http://aspn.activestate.com
    """
    if name is None:
        name = method.__name__

    class new(self.__class__):
        pass

    setattr(new, name, method)
    self.__class__ = new
    return getattr(self, name)


def add_method_by_name(self,
                       method_name,
                       name=None,
                       globals=globals(),
                       locals=None):
    """
    Add a method to a class given a function class

      self        - the object that is modified
      method_name - the name of a function
      name        - a string that describes the new method name
      globals     - the global dictionary
      locals      - the local dictionary

    Adapted from code submitted by Moshe Zadka to the
    ActiveState Programmer Network http://aspn.activestate.com
    """
    add_method(self, eval(method_name, globals, locals), name)
