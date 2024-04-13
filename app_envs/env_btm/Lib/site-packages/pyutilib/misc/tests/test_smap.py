#
# Unit Tests for SparseMapping
#
#

import os
from os.path import abspath, dirname
currdir = dirname(abspath(__file__)) + os.sep
import pyutilib.th as unittest
import pyutilib.misc


class Test(unittest.TestCase):

    def test1(self):
        # Validate behavior for empty sparse map
        smap = pyutilib.misc.SparseMapping()
        self.assertEqual(len(smap), 0)

    def test2(self):
        # Validate behavior for sparse map with specified values
        smap = pyutilib.misc.SparseMapping(a=1, b=2)
        self.assertEqual(len(smap), 2)
        self.assertTrue('a' in smap)
        data = [key for key in smap]
        self.assertEqual(sorted(data), ['a', 'b'])
        try:
            smap['c']
            self.fail("Expected KeyError")
        except KeyError:
            pass
        self.assertEqual(smap['a'], 1)
        try:
            del smap['c']
            self.fail("Expected KeyError")
        except KeyError:
            pass
        del smap['b']
        self.assertEqual(len(smap), 1)
        smap['b'] = 3
        self.assertEqual(smap['b'], 3)

    def test3(self):
        # Validate behavior for sparse map with specified values and domain
        smap = pyutilib.misc.SparseMapping(a=1, b=2, index=['a', 'b', 'z'])
        self.assertEqual(len(smap), 2)
        self.assertTrue('a' in smap)
        data = [key for key in smap]
        self.assertEqual(sorted(data), ['a', 'b'])
        try:
            smap['c']
            self.fail("Expected KeyError")
        except KeyError:
            pass
        self.assertEqual(smap['a'], 1)
        try:
            del smap['c']
            self.fail("Expected KeyError")
        except KeyError:
            pass
        del smap['b']
        self.assertEqual(len(smap), 1)
        smap['b'] = 3
        self.assertEqual(len(smap), 2)
        self.assertEqual(smap['b'], 3)

    def test4(self):
        # Validate behavior for sparse map with specified values and domain and default value
        smap = pyutilib.misc.SparseMapping(
            a=1, b=2, index=['a', 'b', 'z'], default=0)
        self.assertEqual(len(smap), 3)
        self.assertTrue('a' in smap)
        data = [key for key in smap]
        self.assertEqual(sorted(data), ['a', 'b', 'z'])
        try:
            smap['c']
            self.fail("Expected KeyError")
        except KeyError:
            pass
        self.assertEqual(smap['a'], 1)
        try:
            del smap['c']
            self.fail("Expected KeyError")
        except KeyError:
            pass
        del smap['b']
        self.assertEqual(len(smap), 3)
        smap['b'] = 3
        self.assertEqual(len(smap), 3)
        self.assertEqual(smap['b'], 3)
        self.assertEqual(smap['z'], 0)

    def test6(self):
        # Validate behavior for sparse map with specified values and default value
        smap = pyutilib.misc.SparseMapping(a=1, b=2, default=0)
        self.assertEqual(len(smap), 2)
        self.assertTrue('a' in smap)
        data = [key for key in smap]
        self.assertEqual(sorted(data), ['a', 'b'])
        self.assertEqual(smap['c'], 0)
        self.assertEqual(smap['a'], 1)
        try:
            del smap['c']
            self.fail("Expected KeyError")
        except KeyError:
            pass
        del smap['b']
        self.assertEqual(len(smap), 1)
        smap['b'] = 3
        self.assertEqual(len(smap), 2)
        self.assertEqual(smap['b'], 3)
        self.assertEqual(smap['z'], 0)

    def test5(self):
        # Validate behavior for sparse map with specified values and 'within' option
        smap = pyutilib.misc.SparseMapping(a=1, b=2, within=range(10))
        self.assertEqual(len(smap), 2)
        self.assertTrue('a' in smap)
        data = [key for key in smap]
        self.assertEqual(sorted(data), ['a', 'b'])
        try:
            smap['c']
            self.fail("Expected KeyError")
        except KeyError:
            pass
        self.assertEqual(smap['a'], 1)
        try:
            del smap['c']
            self.fail("Expected KeyError")
        except KeyError:
            pass
        del smap['b']
        self.assertEqual(len(smap), 1)
        try:
            smap['b'] = -1
            self.fail("Expected ValueError")
        except ValueError:
            pass
        smap['b'] = 3
        self.assertEqual(smap['b'], 3)


if __name__ == "__main__":
    unittest.main()
