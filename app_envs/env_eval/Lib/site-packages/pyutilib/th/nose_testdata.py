"""This module defines a nose plugin that allows the user to archive test data.

Use the following command-line option with nosetests ::

    nosetests --with-testdata

By default, a file named testdata.csv will be written to the working directory.
If you need to change the name or location of the file, you can set the
``--testdata-file`` option.

Here is an abbreviated version of what the CSV file might look like::

    classname,name,time
    pyutilib.th.tests.test_pyunit.Tester,test_fail,0.00291109085083
    pyutilib.th.tests.test_pyunit.Tester,test_pass,5.57899475098e-05
    pyutilib.th.tests.test_pyunit.Tester2,test_pass,0.000113964080811
    pyutilib.th.tests.test_pyunit.Tester3,test_fail,7.60555267334e-05

"""

import os
import re
from time import time

from nose.plugins.base import Plugin

from six import text_type

# Invalid CSV characters, control characters 0-31 sans \t, \n and \r
CONTROL_CHARACTERS = re.compile(r"[\000-\010\013\014\016-\037]")


def csv_safe(value):
    """Replaces invalid CSV characters with '?'."""
    return CONTROL_CHARACTERS.sub('?', value).replace(',', '_')


class TestData(Plugin):
    """This plugin archives test data in standard CSV format."""
    name = 'testdata'
    score = 2000
    encoding = 'UTF-8'
    report_file = None
    datakeys = set()

    def _timeTaken(self):
        if hasattr(self, '_timer'):
            taken = time() - self._timer
        else:
            # test died before it ran (probably error in setup())
            # or success/failure added before test started probably
            # due to custom TestResult munging
            taken = 0.0
        return taken

    def _quoteattr(self, attr):
        """Escape a CSV attribute. Value can be unicode."""
        attr = csv_safe(attr)
        if isinstance(attr, text_type):
            attr = attr.encode(self.encoding)
        return attr

    def options(self, parser, env):
        """Sets additional command line options."""
        Plugin.options(self, parser, env)
        parser.add_option(
            '--testdata-file',
            action='store',
            dest='testdata_file',
            metavar="FILE",
            default=env.get('NOSE_TESTDATA_FILE', 'testdata.csv'),
            help=("Path to CSV file to store the test data. "
                  "Default is testdata.csv in the working directory "
                  "[NOSE_TESTDATA_FILE]"))
        parser.add_option(
            '--testdata-table',
            action='store_true',
            dest='testdata_table',
            default=env.get('NOSE_TESTDATA_TABLE', False),
            help=(
                "If this option is specified, then the CSV file is "
                " formatted as a table.  By default, the format is a sparse list. "
            ))

    def configure(self, options, config):
        """Configures the testdata plugin."""
        Plugin.configure(self, options, config)
        self.config = config
        self.reportdata = []
        if options.testdata_table:
            self.format = 'table'
        else:
            self.format = 'sparse'
        if self.enabled:
            self.report_file = open(options.testdata_file, 'w')
            self.datakeys.add('time')

    def report(self, stream):
        """Writes a CSV file with test data. """
        if not os.environ.get('HUDSON_URL', None) is None:
            colprefix = 'job,build,node,'
            prefix = "%s,%s,%s," % (os.environ['JOB_NAME'],
                                    os.environ['BUILD_NUMBER'],
                                    os.environ['NODE_NAME'])
        else:
            colprefix = ''
            prefix = ''
        if self.format == 'table':
            keys = ['classname', 'name'] + sorted(list(self.datakeys))
            self.report_file.write(colprefix + ','.join(
                map(self._quoteattr, keys)) + '\n')
            for data in self.reportdata:
                tmp = []
                for key in keys:
                    tmp.append(str(data[2].get(key, '')))
                self.report_file.write(prefix + ','.join(tmp) + '\n')
            self.report_file.close()
        else:
            self.report_file.write(colprefix +
                                   'classname,name,dataname,value\n')
            for data in self.reportdata:
                for key in data[2]:
                    self.report_file.write(prefix)
                    self.report_file.write(str(data[0]) + ',' + str(data[1]))
                    self.report_file.write(',' + str(key) + ',' + str(data[2][
                        key]))
                    self.report_file.write('\n')

        if self.config.verbosity > 1:
            stream.writeln("-" * 70)
            stream.writeln("CSV: %s" % self.report_file.name)

    def startTest(self, test):
        """Initializes a timer before starting a test."""
        self._timer = time()
        test.test.testdata = {}

    def addSuccess(self, test, capt=None):
        """Add success output to test data file.
        """
        taken = self._timeTaken()
        id = test.id()
        for key in test.test.testdata:
            self.datakeys.add(key)
        classname = self._quoteattr('.'.join(id.split('.')[:-1]))
        name = self._quoteattr(id.split('.')[-1])
        test.test.testdata['time'] = taken
        self.reportdata.append((classname, name, test.test.testdata))
