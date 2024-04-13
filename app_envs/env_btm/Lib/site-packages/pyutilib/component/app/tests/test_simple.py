#
# Test simple applications
#

import os
import sys
from os.path import abspath, dirname
currdir = dirname(abspath(__file__)) + os.sep

import pyutilib.th as unittest
import pyutilib.subprocess


class Test(unittest.TestCase):

    def test_app1a(self):
        pyutilib.subprocess.run(sys.executable + " " + currdir + os.sep +
                                "app1a.py " + currdir)
        self.assertFileEqualsBaseline(currdir + "config1.out",
                                      currdir + "config1.txt")

    def test_app1b(self):
        pyutilib.subprocess.run(sys.executable + " " + currdir + os.sep +
                                "app1b.py " + currdir)
        self.assertFileEqualsBaseline(currdir + "config1.out",
                                      currdir + "config1.txt")

    def test_app2(self):
        pyutilib.subprocess.run(sys.executable + " " + currdir + os.sep +
                                "app2.py " + currdir)
        self.assertFileEqualsBaseline(currdir + "summary.out",
                                      currdir + "summary.txt")

    def test_app3(self):
        pyutilib.subprocess.run(sys.executable + " " + currdir + os.sep +
                                "app3.py " + currdir)
        if not os.path.exists(currdir + "app3.log"):
            self.fail("expected log file")
        else:
            os.remove(currdir + "app3.log")

    def test_app4(self):
        pyutilib.subprocess.run(sys.executable + " " + currdir + os.sep +
                                "app4.py " + currdir)
        if not os.path.exists(currdir + "tmp2.ini"):
            self.fail("expected ini file")
        else:
            os.remove(currdir + "tmp2.ini")


if __name__ == "__main__":
    unittest.main()
