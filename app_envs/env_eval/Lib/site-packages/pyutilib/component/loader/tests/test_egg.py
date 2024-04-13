#
# Plugin load tests for eggs
#

import os
import sys
from os.path import abspath, dirname
currdir = dirname(abspath(__file__)) + os.sep

import pyutilib.th as unittest
import pyutilib.subprocess

try:
    import pkg_resources
    pkg_resources_avail = True
except ImportError:
    pkg_resources_avail = False
try:
    import yaml
    yaml_available = True
except ImportError:
    yaml_available = False


@unittest.skipIf(not pkg_resources_avail, "Cannot import 'pkg_resources'")
class Test(pyutilib.th.TestCase):

    def test_egg1(self):
        #
        # Load an egg for the 'project1' project.
        # Eggs are loaded in the 'eggs1' directory, but only the Project1 stuff is actually imported.
        #
        pyutilib.subprocess.run(
            [sys.executable, currdir + os.sep + "egg1.py", currdir, "json"])
        self.assertMatchesJsonBaseline(currdir + "egg1.out",
                                       currdir + "egg1.jsn")
        if yaml_available:
            pyutilib.subprocess.run(
                [sys.executable, currdir + os.sep + "egg1.py", currdir, "yaml"])
            self.assertMatchesYamlBaseline(currdir + "egg1.out",
                                           currdir + "egg1.yml")

    def test_egg2(self):
        #
        # Load an egg for the 'project1' project.
        # Eggs are loaded in the 'eggs1' and 'eggs2' directories, but only the 
        # Project1 and Project 3 stuff is actually imported.
        #
        pyutilib.subprocess.run(
            [sys.executable, currdir + os.sep + "egg2.py", currdir, "json"])
        self.assertMatchesJsonBaseline(currdir + "egg2.out",
                                       currdir + "egg2.jsn")
        if yaml_available:
            pyutilib.subprocess.run(
                [sys.executable, currdir + os.sep + "egg2.py", currdir, "yaml"])
            self.assertMatchesYamlBaseline(currdir + "egg2.out",
                                           currdir + "egg2.yml")

if __name__ == "__main__":
    unittest.main()
