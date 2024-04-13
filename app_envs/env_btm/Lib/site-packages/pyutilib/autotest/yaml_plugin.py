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
    import yaml
    using_yaml = True
except ImportError:  #pragma:nocover
    using_yaml = False
from pyutilib.component.core import SingletonPlugin, implements
from pyutilib.autotest import plugins
import pyutilib.misc


class YamlTestParser(SingletonPlugin):

    implements(plugins.ITestParser)

    def __init__(self, **kwds):
        SingletonPlugin.__init__(self, **kwds)
        self.name = 'yml'

    def load_test_config(self, filename):
        if using_yaml:
            INPUT = open(filename, 'r')
            repn = yaml.load(INPUT, yaml.SafeLoader)
            INPUT.close()
            return repn
        #
        # If PyYaml is not available, then we use a simple yaml parser
        #
        INPUT = open(filename, 'r')
        repn = pyutilib.misc.simple_yaml_parser(INPUT)
        INPUT.close()
        return repn

    def print_test_config(self, repn):
        print(repn)  #pragma:nocover

    def enabled(self):
        return True
