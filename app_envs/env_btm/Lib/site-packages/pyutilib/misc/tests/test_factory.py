#
# Unit Tests for util/math
#
#

from os.path import abspath, dirname
pkgdir = dirname(abspath(__file__)) + "/../.."

import pyutilib.th as unittest
import pyutilib.misc


class FactoryDebug(unittest.TestCase):

    class A(object):

        def __init__(self, *args, **kargs):
            pass

    class B(object):

        def __init__(self, *args, **kargs):
            pass

    def Afunc(*args, **kargs):
        return FactoryDebug.A(*args, **kargs)

    def Bfunc(*args, **kargs):
        return FactoryDebug.B(*args, **kargs)

    def setUp(self):
        self.factory = pyutilib.misc.Factory()
        self.factory.register("classA", self.Afunc, None, None)
        self.factory.register("classB", self.Bfunc, None, None)

    def test_kyes(self):
        self.assertEqual(self.factory.keys(), ["classA", "classB"])

    def test_len(self):
        self.assertEqual(len(self.factory), 2)

    def test_iter(self):
        ans = {0: "classA", 1: "classB"}
        i = 0
        for name in self.factory:
            self.assertEqual(name, ans[i])
            i = i + 1

    def test_getitem(self):
        self.assertEqual(self.factory[0], "classA")
        self.assertEqual(self.factory[1], "classB")

    def test_unregister(self):
        self.factory.unregister("classA")
        self.assertEqual(len(self.factory), 1)
        self.assertEqual(self.factory[0], "classB")

    def test_call(self):
        a = self.factory("classA")
        self.assertEqual(FactoryDebug.A, type(a))
        b = self.factory("classB")
        self.assertEqual(FactoryDebug.B, type(b))
        c = self.factory("classC")
        self.assertEqual(None, c)


if __name__ == "__main__":
    unittest.main()
