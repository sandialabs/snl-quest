import os
from os.path import abspath, dirname
currdir = dirname(abspath(__file__)) + os.sep

import pyutilib.th as unittest


class TestNoCategory(unittest.TestCase):
    def test_noCategory(self):
        self.assertRaises(
            AttributeError, getattr, self.test_noCategory, 'smoke')
        self.assertRaises(
            AttributeError, getattr, self.test_noCategory, 'nightly')
        self.assertRaises(
            AttributeError, getattr, self.test_noCategory, 'expensive')
        self.assertRaises(
            AttributeError, getattr, self.test_noCategory, 'fragile')
        self.assertRaises(
            AttributeError, getattr, self.test_noCategory, 'custom')

    @unittest.category('smoke')
    def test_smoke(self):
        self.assertEqual(self.test_smoke.smoke, 1)
        self.assertEqual(self.test_smoke.nightly, 0)
        self.assertEqual(self.test_smoke.expensive, 0)
        self.assertEqual(self.test_smoke.fragile, 0)
        self.assertRaises(
            AttributeError, getattr, self.test_smoke, 'custom')

    @unittest.category('expensive')
    def test_expensive(self):
        self.assertEqual(self.test_expensive.smoke, 0)
        self.assertEqual(self.test_expensive.nightly, 0)
        self.assertEqual(self.test_expensive.expensive, 1)
        self.assertEqual(self.test_expensive.fragile, 0)
        self.assertRaises(
            AttributeError, getattr, self.test_expensive, 'custom')

    @unittest.category('!expensive')
    def test_notExpensive(self):
        self.assertEqual(self.test_notExpensive.smoke, 0)
        self.assertEqual(self.test_notExpensive.nightly, 0)
        self.assertEqual(self.test_notExpensive.expensive, 0)
        self.assertEqual(self.test_notExpensive.fragile, 0)
        self.assertRaises(
            AttributeError, getattr, self.test_notExpensive, 'custom')

    @unittest.category('fragile')
    def test_fragile(self):
        self.assertRaises(
            AttributeError, getattr, self.test_noCategory, 'smoke')
        self.assertRaises(
            AttributeError, getattr, self.test_noCategory, 'nightly')
        self.assertRaises(
            AttributeError, getattr, self.test_noCategory, 'expensive')
        self.assertEqual(self.test_fragile.fragile, 1)
        self.assertRaises(
            AttributeError, getattr, self.test_notExpensive, 'custom')

    @unittest.category('fragile','smoke')
    def test_fragile_smoke(self):
        self.assertEqual(self.test_fragile_smoke.smoke, 1)
        self.assertEqual(self.test_fragile_smoke.nightly, 0)
        self.assertEqual(self.test_fragile_smoke.expensive, 0)
        self.assertEqual(self.test_fragile_smoke.fragile, 1)
        self.assertRaises(
            AttributeError, getattr, self.test_notExpensive, 'custom')

    @unittest.category('custom')
    def test_custom(self):
        self.assertEqual(self.test_custom.smoke, 0)
        self.assertEqual(self.test_custom.nightly, 0)
        self.assertEqual(self.test_custom.expensive, 0)
        self.assertEqual(self.test_custom.fragile, 0)
        self.assertEqual(self.test_custom.custom, 1)

    @unittest.category('custom','smoke')
    def test_multi(self):
        self.assertEqual(self.test_multi.smoke, 1)
        self.assertEqual(self.test_multi.nightly, 0)
        self.assertEqual(self.test_multi.expensive, 0)
        self.assertEqual(self.test_multi.fragile, 0)
        self.assertEqual(self.test_multi.custom, 1)

@unittest.category('expensive')
class TestExpensive(unittest.TestCase):
    def test_noCategory(self):
        self.assertRaises(
            AttributeError, getattr, self.test_noCategory, 'smoke')
        self.assertRaises(
            AttributeError, getattr, self.test_noCategory, 'nightly')
        self.assertRaises(
            AttributeError, getattr, self.test_noCategory, 'expensive')
        self.assertRaises(
            AttributeError, getattr, self.test_noCategory, 'fragile')
        self.assertRaises(
            AttributeError, getattr, self.test_noCategory, 'custom')

    @unittest.category('smoke')
    def test_smoke(self):
        self.assertEqual(self.test_smoke.smoke, 1)
        self.assertEqual(self.test_smoke.nightly, 0)
        self.assertEqual(self.test_smoke.expensive, 1)
        self.assertEqual(self.test_smoke.fragile, 0)
        self.assertRaises(
            AttributeError, getattr, self.test_smoke, 'custom')

    @unittest.category('expensive')
    def test_expensive(self):
        self.assertEqual(self.test_expensive.smoke, 0)
        self.assertEqual(self.test_expensive.nightly, 0)
        self.assertEqual(self.test_expensive.expensive, 1)
        self.assertEqual(self.test_expensive.fragile, 0)
        self.assertRaises(
            AttributeError, getattr, self.test_expensive, 'custom')

    @unittest.category('!expensive')
    def test_notExpensive(self):
        self.assertEqual(self.test_notExpensive.smoke, 0)
        self.assertEqual(self.test_notExpensive.nightly, 0)
        self.assertEqual(self.test_notExpensive.expensive, 0)
        self.assertEqual(self.test_notExpensive.fragile, 0)
        self.assertRaises(
            AttributeError, getattr, self.test_notExpensive, 'custom')

    @unittest.category('fragile')
    def test_fragile(self):
        self.assertEqual(self.test_fragile.smoke, 0)
        self.assertEqual(self.test_fragile.nightly, 0)
        self.assertEqual(self.test_fragile.expensive, 1)
        self.assertEqual(self.test_fragile.fragile, 1)
        self.assertRaises(
            AttributeError, getattr, self.test_notExpensive, 'custom')

    @unittest.category('fragile','smoke')
    def test_fragile_smoke(self):
        self.assertEqual(self.test_fragile_smoke.smoke, 1)
        self.assertEqual(self.test_fragile_smoke.nightly, 0)
        self.assertEqual(self.test_fragile_smoke.expensive, 1)
        self.assertEqual(self.test_fragile_smoke.fragile, 1)
        self.assertRaises(
            AttributeError, getattr, self.test_notExpensive, 'custom')

    @unittest.category('custom')
    def test_custom(self):
        self.assertEqual(self.test_custom.smoke, 0)
        self.assertEqual(self.test_custom.nightly, 0)
        self.assertEqual(self.test_custom.expensive, 1)
        self.assertEqual(self.test_custom.fragile, 0)
        self.assertEqual(self.test_custom.custom, 1)

    @unittest.category('custom','smoke')
    def test_multi(self):
        self.assertEqual(self.test_multi.smoke, 1)
        self.assertEqual(self.test_multi.nightly, 0)
        self.assertEqual(self.test_multi.expensive, 1)
        self.assertEqual(self.test_multi.fragile, 0)
        self.assertEqual(self.test_multi.custom, 1)


if __name__ == "__main__":
    unittest.main()
