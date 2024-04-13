#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________
#

try:
    import json
    json_available = True
except:  #pragma:nocover
    json_available = False
from pyutilib.component.core import SingletonPlugin, implements
from pyutilib.autotest import plugins


class JsonTestParser(SingletonPlugin):

    implements(plugins.ITestParser)

    def __init__(self, **kwds):
        SingletonPlugin.__init__(self, **kwds)
        self.name = 'json'

    def load_test_config(self, filename):
        INPUT = open(filename, 'r')
        repn = json.load(INPUT)
        INPUT.close()
        return repn

    def print_test_config(self, repn):
        print(repn)  #pragma:nocover

    def enabled(self):
        return json_available
