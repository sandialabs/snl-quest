#
# Unit Tests for yaml_utils
#
#

import os
from os.path import abspath, dirname
currdir = dirname(abspath(__file__)) + os.sep
import pyutilib.th as unittest
import pyutilib.misc

try:
    import yaml
    using_yaml = True
except ImportError:
    using_yaml = False


class Test(unittest.TestCase):

    def setUp(self):
        if not using_yaml:
            self.skipTest("Cannot execute test because YAML is not available.")

    def test1(self):
        # Verify that data 1 is not equal to data 2
        self.assertRaises(
            IOError,
            pyutilib.misc.compare_yaml_files,
            currdir + 'yamldata1.yml',
            currdir + 'yamldata2.yml',
            exact=True)

    def test2(self):
        # Verify that data 1 is a subset of data 2
        pyutilib.misc.compare_yaml_files(
            currdir + 'yamldata1.yml', currdir + 'yamldata2.yml', exact=False)

    def test3(self):
        # Verify that data 2 is not a subset of data 1
        self.assertRaises(
            IOError,
            pyutilib.misc.compare_yaml_files,
            currdir + 'yamldata2.yml',
            currdir + 'yamldata1.yml',
            exact=True)

    def test4(self):
        # Verify check to confirm that YAML data has a different type
        self.assertRaises(
            IOError,
            pyutilib.misc.compare_yaml_files,
            currdir + 'yamldata1.yml',
            currdir + 'yamldata3.yml',
            exact=True)

    def test5(self):
        # Verify that data 1 is not equal to data 1
        pyutilib.misc.compare_yaml_files(
            currdir + 'yamldata1.yml', currdir + 'yamldata1.yml', exact=True)

    def test6(self):
        # Verify that data 1 is a subset of data 4
        pyutilib.misc.compare_yaml_files(
            currdir + 'yamldata1.yml',
            currdir + 'yamldata4.txt',
            output_begin='BEGIN',
            output_end='END',
            exact=False)

    def test7(self):
        # Verify that data 6 is a subset of data 5
        pyutilib.misc.compare_yaml_files(
            currdir + 'yamldata6.yml', currdir + 'yamldata5.yml', exact=False)

    def test8(self):
        # Verify that data 5 is not a subset of data 6
        self.assertRaises(
            IOError,
            pyutilib.misc.compare_yaml_files,
            currdir + 'yamldata5.yml',
            currdir + 'yamldata6.yml',
            exact=False)

    def test9(self):
        # Verify that data 7 is not a subset of data 5
        self.assertRaises(
            IOError,
            pyutilib.misc.compare_yaml_files,
            currdir + 'yamldata7.yml',
            currdir + 'yamldata5.yml',
            exact=False)

    def test10(self):
        # Verify that data 6 is not equal to data 5
        self.assertRaises(
            IOError,
            pyutilib.misc.compare_yaml_files,
            currdir + 'yamldata6.yml',
            currdir + 'yamldata5.yml',
            exact=True)

    def test11(self):
        # Verify that data 8 is not equal to data 5
        self.assertRaises(
            IOError,
            pyutilib.misc.compare_yaml_files,
            currdir + 'yamldata8.yml',
            currdir + 'yamldata5.yml',
            exact=True)

    def test12(self):
        # Verify that data 9 is not a subset of data 1
        self.assertRaises(
            IOError,
            pyutilib.misc.compare_yaml_files,
            currdir + 'yamldata9.yml',
            currdir + 'yamldata1.yml',
            exact=True)

    def test13(self):
        # Verify that data 10 is not a subset of data 1
        self.assertRaises(
            ValueError,
            pyutilib.misc.compare_yaml_files,
            currdir + 'yamldata10.yml',
            currdir + 'yamldata1.yml',
            exact=True)

    def test14(self):
        # Verify that data 10 is a subset of data 1 with a loose tolerance
        pyutilib.misc.compare_yaml_files(
            currdir + 'yamldata10.yml',
            currdir + 'yamldata1.yml',
            tolerance=1.0,
            exact=True)

    def test15a(self):
        # Verify that compressed files can be compared
        pyutilib.misc.compare_yaml_files(
            currdir + 'yamldata14.yml',
            currdir + 'yamldata14.yml.gz',
            exact=True)

    def test15b(self):
        # Verify that compressed files can be compared
        pyutilib.misc.compare_yaml_files(
            currdir + 'yamldata14.yml.gz',
            currdir + 'yamldata14.yml',
            exact=True)


class TestSimple(unittest.TestCase):

    def test1(self):
        # Parse yamldata1.yml
        self.assertEqual({
            'a': {'b': 1,
                  'c': 1.3},
            'd': {'e': 'the rain in spain',
                  'f': 'is mostly on the plain'}
        }, pyutilib.misc.simple_yaml_parser(currdir + 'yamldata1.yml'))

    def test2(self):
        # Parse yamldata2.yml
        self.assertEqual({
            'a': {'b': 1,
                  'c': 1.3},
            'd': {'e': 'the rain in spain',
                  'f': 'is mostly on the plain'},
            'g': 'again'
        }, pyutilib.misc.simple_yaml_parser(currdir + 'yamldata2.yml'))

    def test3(self):
        # Parse yamldata3.yml
        self.assertEqual(
            ['a', 'b', 'c'],
            pyutilib.misc.simple_yaml_parser(currdir + 'yamldata3.yml'))

    def test5(self):
        # Parse yamldata5.yml
        self.assertEqual(
            {'a': ['b', 1, {'c': 'ccc',
                            'e': 'eee',
                            'd': 'ddd'}, 1.3],
             'g': 'again'},
            pyutilib.misc.simple_yaml_parser(currdir + 'yamldata5.yml'))

    def test6(self):
        # Parse yamldata6.yml
        self.assertEqual(
            {'a': [1, {'c': 'ccc',
                       'e': 'eee',
                       'd': 'ddd'}, 1.3],
             'g': 'again'},
            pyutilib.misc.simple_yaml_parser(currdir + 'yamldata6.yml'))

    def test7(self):
        # Parse yamldata7.yml
        self.assertEqual(
            {'a': [1, {'c': 'ccc',
                       'e': 'eee',
                       'd': 'ddd'}, 1.3, 'x', 'y'],
             'g': 'again'},
            pyutilib.misc.simple_yaml_parser(currdir + 'yamldata7.yml'))

    def test11(self):
        # Parse yamldata11.yml
        self.assertEqual(
            ['a', ['b', 'c', ['d', 'e'], 'f', 'g'], 'h'],
            pyutilib.misc.simple_yaml_parser(currdir + 'yamldata11.yml'))

    def test12(self):
        # Parse yamldata12.yml
        self.assertEqual(
            ['a', {'X': ['b', ['d', 'e'], 'f', 'g'],
                   'Y': 'FOO'}, 'h'],
            pyutilib.misc.simple_yaml_parser(currdir + 'yamldata12.yml'))

    def test13(self):
        # Parse yamldata13.yml
        pyutilib.misc.simple_yaml_parser(currdir + 'yamldata13.yml').keys()

    def test14(self):
        # Parse yamldata14.yml
        pyutilib.misc.simple_yaml_parser(currdir + 'yamldata14.yml').keys()


if __name__ == "__main__":
    unittest.main()
