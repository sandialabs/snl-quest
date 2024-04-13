#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________

from pyutilib.th.pyunit import TestCase, TestResult, TestSuite, TextTestRunner, main, nottest, category
try:
    from pyutilib.th.pyunit import skip, skipIf, skipUnless, expectedFailure, SkipTest
except:
    pass

try:
    import pyutilib.th.nose_testdata
except ImportError:
    pass
try:
    import pyutilib.th.nose_gc
except ImportError:
    pass
try:
    import pyutilib.th.nose_timeout
except ImportError:
    pass


mock_available = False
try:
    from unittest import mock

    mock_available = True
except ImportError:
    try:
        import mock

        mock_available = True
    except ImportError:
        pass
