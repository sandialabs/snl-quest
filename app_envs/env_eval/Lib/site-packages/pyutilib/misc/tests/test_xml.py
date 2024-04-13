#
# Unit Tests for xml_utils
#
#

import os
from os.path import abspath, dirname
pkgdir = dirname(abspath(__file__))
currdir = dirname(abspath(__file__)) + os.sep
import pyutilib.th as unittest
import pyutilib.misc

from xml.dom import minidom


class XMLDebug(unittest.TestCase):

    def setUp(self):
        self.doc = minidom.parse(pkgdir + "/test.xml")
        self.node = self.doc.documentElement

    def tearDown(self):
        self.doc = None
        self.node = None

    def test_get_text(self):
        # Verify that we can get XML text
        str = pyutilib.misc.get_xml_text(self.node)
        target = "a b c\n  \n  d e f"
        self.assertEqual(target, str)

    def test_escape(self):
        source = "&'<>\""
        str = pyutilib.misc.escape(source)
        target = "&amp;'&lt;&gt;\""
        self.assertEqual(target, str)


class Test(unittest.TestCase):

    def test1(self):
        # Verify that data 1 is not equal to data 2
        self.assertRaises(
            IOError,
            pyutilib.misc.compare_xml_files,
            currdir + 'xmldata1.xml',
            currdir + 'xmldata2.xml',
            exact=True)

    def test2(self):
        # Verify that data 1 is a subset of data 2
        pyutilib.misc.compare_xml_files(
            currdir + 'xmldata1.xml', currdir + 'xmldata2.xml', exact=False)

    def test3(self):
        # Verify that data 2 is not a subset of data 1
        self.assertRaises(
            IOError,
            pyutilib.misc.compare_xml_files,
            currdir + 'xmldata2.xml',
            currdir + 'xmldata1.xml',
            exact=True)

    def test4(self):
        # Verify check to confirm that YAML data has a different type
        self.assertRaises(
            IOError,
            pyutilib.misc.compare_xml_files,
            currdir + 'xmldata1.xml',
            currdir + 'xmldata3.xml',
            exact=True)

    def test5(self):
        # Verify that data 1 is not equal to data 1
        pyutilib.misc.compare_xml_files(
            currdir + 'xmldata1.xml', currdir + 'xmldata1.xml', exact=True)

    def test6(self):
        # Verify that data 1 is a subset of data 4
        pyutilib.misc.compare_xml_files(
            currdir + 'xmldata1.xml',
            currdir + 'xmldata4.txt',
            output_begin='BEGIN',
            output_end='END',
            exact=False)

    def test7(self):
        # Verify that data 6 is a subset of data 5
        pyutilib.misc.compare_xml_files(
            currdir + 'xmldata6.xml', currdir + 'xmldata5.xml', exact=False)

    def test8(self):
        # Verify that data 5 is not a subset of data 6
        self.assertRaises(
            IOError,
            pyutilib.misc.compare_xml_files,
            currdir + 'xmldata5.xml',
            currdir + 'xmldata6.xml',
            exact=False)

    def test9(self):
        # Verify that data 7 is not a subset of data 5
        self.assertRaises(
            IOError,
            pyutilib.misc.compare_xml_files,
            currdir + 'xmldata7.xml',
            currdir + 'xmldata5.xml',
            exact=False)

    def test10(self):
        # Verify that data 6 is not equal to data 5
        self.assertRaises(
            IOError,
            pyutilib.misc.compare_xml_files,
            currdir + 'xmldata6.xml',
            currdir + 'xmldata5.xml',
            exact=True)

    def test11(self):
        # Verify that data 8 is not equal to data 5
        self.assertRaises(
            IOError,
            pyutilib.misc.compare_xml_files,
            currdir + 'xmldata8.xml',
            currdir + 'xmldata5.xml',
            exact=True)

    def test12(self):
        # Verify that data 9 is not a subset of data 1
        self.assertRaises(
            IOError,
            pyutilib.misc.compare_xml_files,
            currdir + 'xmldata9.xml',
            currdir + 'xmldata1.xml',
            exact=True)

    def test13(self):
        # Verify that data 10 is not a subset of data 1
        self.assertRaises(
            ValueError,
            pyutilib.misc.compare_xml_files,
            currdir + 'xmldata10.xml',
            currdir + 'xmldata1.xml',
            exact=True)

    def test14(self):
        # Verify that data 10 is a subset of data 1 with a loose tolerance
        pyutilib.misc.compare_xml_files(
            currdir + 'xmldata10.xml',
            currdir + 'xmldata1.xml',
            tolerance=1.0,
            exact=True)


if __name__ == "__main__":
    unittest.main()
