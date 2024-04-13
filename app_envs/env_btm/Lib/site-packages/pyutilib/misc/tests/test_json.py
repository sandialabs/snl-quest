#
# Unit Tests for json (in json_utils)
#
#

import os
from os.path import abspath, dirname
currdir = dirname(abspath(__file__)) + os.sep
import pyutilib.th as unittest
import pyutilib.misc

try:
    import json
    json_available = True
except ImportError:
    json_available = False


class Test(unittest.TestCase):

    def setUp(self):
        if not json_available:
            self.skipTest("Cannot execute test because JSON is not available.")

    def test1(self):
        # Verify that data 1 is not equal to data 2
        self.assertRaises(
            IOError,
            pyutilib.misc.compare_json_files,
            currdir + 'jsondata1.jsn',
            currdir + 'jsondata2.jsn',
            exact=True)

    def test2(self):
        # Verify that data 1 is a subset of data 2
        pyutilib.misc.compare_json_files(
            currdir + 'jsondata1.jsn', currdir + 'jsondata2.jsn', exact=False)

    def test3(self):
        # Verify that data 2 is not a subset of data 1
        self.assertRaises(
            IOError,
            pyutilib.misc.compare_json_files,
            currdir + 'jsondata2.jsn',
            currdir + 'jsondata1.jsn',
            exact=True)

    def test4(self):
        # Verify check to confirm that YAML data has a different type
        self.assertRaises(
            IOError,
            pyutilib.misc.compare_json_files,
            currdir + 'jsondata1.jsn',
            currdir + 'jsondata3.jsn',
            exact=True)

    def test5(self):
        # Verify that data 1 is not equal to data 1
        pyutilib.misc.compare_json_files(
            currdir + 'jsondata1.jsn', currdir + 'jsondata1.jsn', exact=True)

    def test6(self):
        # Verify that data 1 is a subset of data 4
        pyutilib.misc.compare_json_files(
            currdir + 'jsondata1.jsn',
            currdir + 'jsondata4.txt',
            output_begin='BEGIN',
            output_end='END',
            exact=False)

    def test7(self):
        # Verify that data 6 is a subset of data 5
        pyutilib.misc.compare_json_files(
            currdir + 'jsondata6.jsn', currdir + 'jsondata5.jsn', exact=False)

    def test8(self):
        # Verify that data 5 is not a subset of data 6
        self.assertRaises(
            IOError,
            pyutilib.misc.compare_json_files,
            currdir + 'jsondata5.jsn',
            currdir + 'jsondata6.jsn',
            exact=False)

    def test9(self):
        # Verify that data 7 is not a subset of data 5
        self.assertRaises(
            IOError,
            pyutilib.misc.compare_json_files,
            currdir + 'jsondata7.jsn',
            currdir + 'jsondata5.jsn',
            exact=False)

    def test10(self):
        # Verify that data 6 is not equal to data 5
        self.assertRaises(
            IOError,
            pyutilib.misc.compare_json_files,
            currdir + 'jsondata6.jsn',
            currdir + 'jsondata5.jsn',
            exact=True)

    def test11(self):
        # Verify that data 8 is not equal to data 5
        self.assertRaises(
            IOError,
            pyutilib.misc.compare_json_files,
            currdir + 'jsondata8.jsn',
            currdir + 'jsondata5.jsn',
            exact=True)

    def test12(self):
        # Verify that data 9 is not a subset of data 1
        self.assertRaises(
            IOError,
            pyutilib.misc.compare_json_files,
            currdir + 'jsondata9.jsn',
            currdir + 'jsondata1.jsn',
            exact=True)

    def test13(self):
        # Verify that data 10 is not a subset of data 1
        self.assertRaises(
            ValueError,
            pyutilib.misc.compare_json_files,
            currdir + 'jsondata10.jsn',
            currdir + 'jsondata1.jsn',
            exact=True)

    def test14(self):
        # Verify that data 10 is a subset of data 1 with a loose tolerance
        pyutilib.misc.compare_json_files(
            currdir + 'jsondata10.jsn',
            currdir + 'jsondata1.jsn',
            tolerance=1.0,
            exact=True)

    def test15a(self):
        # Verify that compressed files can be compared
        pyutilib.misc.compare_json_files(
            currdir + 'jsondata2.jsn', currdir + 'jsondata2.jsn.gz', exact=True)

    def test15b(self):
        # Verify that compressed files can be compared
        pyutilib.misc.compare_json_files(
            currdir + 'jsondata2.jsn.gz', currdir + 'jsondata2.jsn', exact=True)


if __name__ == "__main__":
    unittest.main()
