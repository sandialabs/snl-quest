import sys

__all__ = ['SparseMapping']

import six

try:
    if six.PY2:
        from collections import MutableMapping
    else:
        from collections.abc import MutableMapping

    class SparseMapping(MutableMapping):
        """
        Class that provides a default value for keys that are not defined in
        the dictionary, a specified index for keys, and a specified value that
        mappings are within.
        """

        def __init__(self, default=None, index=None, within=None, *args,
                     **kwds):
            self._map = kwds
            self.default = default
            self._index = index
            self.within = within
            self.update(dict(*args, **kwds))

        def nondefault_keys(self):
            return self._map.keys()

        def nondefault_iter(self):
            return iter(self._map)

        def __len__(self):
            if self._index is None or self.default is None:
                return len(self._map)
            return len(self._index)

        def __contains__(self, key):
            if self._index is None:
                return key in self._map
            return key in self._index

        def __iter__(self):
            if self._index is None or self.default is None:
                return iter(self._map)
            return iter(self._index)

        def __getitem__(self, key):
            if key in self._map:
                return self._map[key]
            if not self.default is None and (self._index is None or
                                             key in self._index):
                return self.default
            if (self.default is None) and (not self._index is None) and (
                    key in self._index):
                raise ValueError(
                    "Legal key '%s' specified in SparseMapping, but value is uninitialized and there is no default value"
                    % key)
            raise KeyError("Unknown key value: %s" % str(key))

        def __setitem__(self, key, value):
            if not self._index is None and not key in self._index:
                raise KeyError("Unknown key value: %s" % str(key))
            if not self.within is None and not value in self.within:
                raise ValueError("Bad mapping value: %s" % str(value))
            self._map[key] = value

        def index(self):
            return self._index

        def set_item(self, key, value):
            self._map[key] = value

        def __delitem__(self, key):
            del self._map[key]

except ImportError:

    class SparseMapping(dict):
        """
        Class that provides a default value for keys that are not defined in
        the dictionary.

        Adapted from code developed by Andreas Kloss and submitted to
        the ActiveState Programmer Network http://aspn.activestate.com
        """

        def __init__(self, default=None, index=None, within=None, *args,
                     **kwds):
            super(SparseMapping, self).__init__()
            self.update(kwds)
            self.default = default
            self._index = index
            self.within = within

        def nondefault_keys(self):
            return self.keys()

        def nondefault_iter(self):
            return iter(self)

        def set_item(self, key, value):
            self[key] = value

        def index(self):
            return self._index

        def __len__(self):
            if self._index is None or self.default is None:
                return dict.__len__(self)
            return len(self._index)

        def __getitem__(self, key):
            try:
                return dict.__getitem__(self, key)
            except KeyError:
                err = sys.exc_info()[1]
                if not self.default is None and (self._index is None or
                                                 key in self._index):
                    return self.default
                raise err

        def __copy__(self):
            return SparseMapping(self.default, self)
