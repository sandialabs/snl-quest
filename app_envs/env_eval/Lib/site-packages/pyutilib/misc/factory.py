#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________


class Factory(object):
    """
    Class that provides a generic constructor mechanism.

    Adapted from code developed by Andres Tuells and submitted to
    the ActiveState Programmer Network http://aspn.activestate.com
    """

    def __init__(self):
        """ Constructor """
        self.Keys = []
        self.constructors = {}

    def register(self, methodName, constructor, *args, **kargs):
        """ Register a constructor """
        self.Keys = self.Keys + [methodName]
        _args = [constructor]
        _args.extend(args)
        mname = "construct_" + methodName
        self.constructors[methodName] = _Functor(*_args, **kargs)
        #self.constructors[methodName] = apply(_Functor,_args, kargs)
        setattr(self, methodName, _Functor(*_args, **kargs))
        #setattr(self, methodName,apply(_Functor,_args, kargs))

    def construct(self, name):
        """
        Use the string name to create an object.
        """
        try:
            method = getattr(self, str(name))
        except AttributeError:
            return None
        return method()

    def __call__(self, name):
        """
        Use the string name to create an object.
        """
        return self.construct(name)

    def unregister(self, methodName):
        """ Unregister a constructor """
        delattr(self, methodName)
        self.Keys.remove(methodName)

    def keys(self):
        """
        Returns the list of names that can are registered in this factory
        """
        return self.Keys

    def __len__(self):
        """
        Returns the number of names in the factory
        """
        return len(self.Keys)

    def __iter__(self):
        """ Returns an iterator for the factory keys """
        return self.Keys.__iter__()

    def __getitem__(self, index):
        """ Allows an index into the list of factory keys """
        return self.Keys[index]


class _Functor:
    """
    A class that wraps a function to act like the function.
    """

    def __init__(self, function, *args, **kargs):
        """ Constructor """
        assert hasattr(function,
                       '__call__'), "function should be a callable obj"
        self._function = function
        self._args = args
        self._kargs = kargs

    def __call__(self, *args, **kargs):
        """ Call function """
        _args = list(self._args)
        _args.extend(args)
        _kargs = self._kargs.copy()
        _kargs.update(kargs)
        return self._function(*_args, **_kargs)
