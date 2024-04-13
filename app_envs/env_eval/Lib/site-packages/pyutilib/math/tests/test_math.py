#
# Unit Tests for util/math
#
#

import unittest
import pyutilib.math


class MathDebug(unittest.TestCase):

    def test_isint(self):
        # Verify that isint() identifies ints
        if pyutilib.math.isint([1, 2]):
            self.fail("test_isint - thought that a list was an integer")
        if pyutilib.math.isint("a"):
            self.fail("test_isint - thought that a string was integer")
        if not pyutilib.math.isint(" 1 "):
            self.fail(
                "test_isint - thought that an integer string was not an integer")
        if not pyutilib.math.isint(" 1.0 "):
            self.fail(
                "test_isint - thought that an integer float string was not an integer")
        if pyutilib.math.isint(" 1.1 "):
            self.fail("test_isint - thought that a float string was an integer")
        if pyutilib.math.isint(1.1):
            self.fail("test_isint - thought that a float was integer")
        if not pyutilib.math.isint(1.0):
            self.fail(
                "test_isint - thought that an integer float was not an integer")
        if not pyutilib.math.isint(1):
            self.fail("test_isint - thought that an integer was not an integer")

    def test_argmax(self):
        # Test that argmax works
        a = [0, 1, 2, 3]
        self.assertEqual(a[pyutilib.math.argmax(a)], a[3])
        a = [3, 2, 1, 0]
        self.assertEqual(a[pyutilib.math.argmax(a)], a[0])

    def test_argmin(self):
        # Test that argmin works
        a = [0, 1, 2, 3]
        self.assertEqual(a[pyutilib.math.argmin(a)], a[0])
        a = [3, 2, 1, 0]
        self.assertEqual(a[pyutilib.math.argmin(a)], a[3])

    def test_mean(self):
        # Verify that mean() works
        self.assertEqual(pyutilib.math.mean((1, 2, 3)), 2.0)
        try:
            val = pyutilib.math.mean([])
            self.fail("test_mean - should have failed with an empty list")
        except ArithmeticError:
            pass

    def test_median(self):
        # Verify that median() works
        self.assertEqual(pyutilib.math.median((1, 2, 3)), 2.0)
        self.assertEqual(pyutilib.math.median((2,)), 2.0)
        self.assertEqual(pyutilib.math.median((1, 2, 3, 4)), 2.5)
        try:
            val = pyutilib.math.median([])
            self.fail("test_median - should have failed with an empty list")
        except ArithmeticError:
            pass

    def test_factorial(self):
        # Verify that factorial() works
        self.assertEqual(pyutilib.math.factorial(0), 1)
        self.assertEqual(pyutilib.math.factorial(1), 1)
        self.assertEqual(pyutilib.math.factorial(2), 2)
        self.assertEqual(pyutilib.math.factorial(3), 6)
        self.assertEqual(pyutilib.math.factorial(4), 24)
        try:
            val = pyutilib.math.factorial(-1)
            self.fail(
                "test_factorial - should have failed with a negative value")
        except ArithmeticError:
            pass

    def test_perm(self):
        # Verify that perm() works
        self.assertEqual(pyutilib.math.perm(7, 1), 7)
        self.assertEqual(pyutilib.math.perm(7, 2), 21)


if __name__ == "__main__":
    unittest.main()
