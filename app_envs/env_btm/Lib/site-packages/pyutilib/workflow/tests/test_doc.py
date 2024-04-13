# Imports
import sys
import os
from os.path import dirname, abspath, abspath

import pyutilib.th as unittest

currdir = dirname(abspath(__file__)) + os.sep
datadir = os.sep.join([dirname(dirname(dirname(dirname(abspath(__file__))))),
                       'doc', 'workflow', 'examples']) + os.sep

sys.path.insert(0, datadir)
try:
    from test_example import *
finally:
    sys.path.remove(datadir)

# Execute the tests
if __name__ == '__main__':
    unittest.main()
