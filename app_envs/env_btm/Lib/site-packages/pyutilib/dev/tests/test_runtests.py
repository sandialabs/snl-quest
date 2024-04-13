import os
import re
import six
import pyutilib.misc
from pyutilib.dev.runtests import runPyUtilibTests

import pyutilib.th as unittest

class Test_Runtests(unittest.TestCase):
    def _run(self, args):
        oldCat = os.environ.get('PYUTILIB_UNITTEST_CATEGORY',None)
        if oldCat is not None:
            del os.environ['PYUTILIB_UNITTEST_CATEGORY']
        stream_out = six.StringIO()
        pyutilib.misc.setup_redirect(stream_out)
        rc = runPyUtilibTests(['nosetests', '-v', '--no-xunit'] + args +
                              ['pyutilib.th.tests.test_pyunit'],
                              use_exec=False)
        pyutilib.misc.reset_redirect()
        if oldCat is not None:
            os.environ['PYUTILIB_UNITTEST_CATEGORY'] = oldCat

        if rc:
            self.fail("running nosetests failed (rc=%s)" % (rc,))

        result = []
        for line in stream_out.getvalue().splitlines():
            if '...' not in line:
                continue
            g = re.match('(\S+) \(([^\)]+)\)', line)
            if g:
                result.append("%s.%s" % (g.group(2), g.group(1)))
        return result

    def test_all(self):
        result = self._run(['--cat=all'])
        ref = [
            'pyutilib.th.tests.test_pyunit.TestExpensive.test_custom',
            'pyutilib.th.tests.test_pyunit.TestExpensive.test_expensive',
            'pyutilib.th.tests.test_pyunit.TestExpensive.test_fragile',
            'pyutilib.th.tests.test_pyunit.TestExpensive.test_fragile_smoke',
            'pyutilib.th.tests.test_pyunit.TestExpensive.test_multi',
            'pyutilib.th.tests.test_pyunit.TestExpensive.test_noCategory',
            'pyutilib.th.tests.test_pyunit.TestExpensive.test_notExpensive',
            'pyutilib.th.tests.test_pyunit.TestExpensive.test_smoke',
            'pyutilib.th.tests.test_pyunit.TestNoCategory.test_custom',
            'pyutilib.th.tests.test_pyunit.TestNoCategory.test_expensive',
            'pyutilib.th.tests.test_pyunit.TestNoCategory.test_fragile',
            'pyutilib.th.tests.test_pyunit.TestNoCategory.test_fragile_smoke',
            'pyutilib.th.tests.test_pyunit.TestNoCategory.test_multi',
            'pyutilib.th.tests.test_pyunit.TestNoCategory.test_noCategory',
            'pyutilib.th.tests.test_pyunit.TestNoCategory.test_notExpensive',
            'pyutilib.th.tests.test_pyunit.TestNoCategory.test_smoke',
        ]
        self.assertEqual(sorted(result), sorted(ref))

    def test_noCategory(self):
        result = self._run([])
        ref = [
            #'pyutilib.th.tests.test_pyunit.TestExpensive.test_custom',
            #'pyutilib.th.tests.test_pyunit.TestExpensive.test_expensive',
            #'pyutilib.th.tests.test_pyunit.TestExpensive.test_fragile',
            #'pyutilib.th.tests.test_pyunit.TestExpensive.test_fragile_smoke',
            'pyutilib.th.tests.test_pyunit.TestExpensive.test_multi',
            #'pyutilib.th.tests.test_pyunit.TestExpensive.test_noCategory',
            #'pyutilib.th.tests.test_pyunit.TestExpensive.test_notExpensive',
            'pyutilib.th.tests.test_pyunit.TestExpensive.test_smoke',
            #'pyutilib.th.tests.test_pyunit.TestNoCategory.test_custom',
            #'pyutilib.th.tests.test_pyunit.TestNoCategory.test_expensive',
            #'pyutilib.th.tests.test_pyunit.TestNoCategory.test_fragile',
            #'pyutilib.th.tests.test_pyunit.TestNoCategory.test_fragile_smoke',
            'pyutilib.th.tests.test_pyunit.TestNoCategory.test_multi',
            'pyutilib.th.tests.test_pyunit.TestNoCategory.test_noCategory',
            #'pyutilib.th.tests.test_pyunit.TestNoCategory.test_notExpensive',
            'pyutilib.th.tests.test_pyunit.TestNoCategory.test_smoke',
        ]
        self.assertEqual(sorted(result), sorted(ref))


    def test_smoke(self):
        result = self._run(['--cat=smoke'])
        ref = [
            #'pyutilib.th.tests.test_pyunit.TestExpensive.test_custom',
            #'pyutilib.th.tests.test_pyunit.TestExpensive.test_expensive',
            #'pyutilib.th.tests.test_pyunit.TestExpensive.test_fragile',
            #'pyutilib.th.tests.test_pyunit.TestExpensive.test_fragile_smoke',
            'pyutilib.th.tests.test_pyunit.TestExpensive.test_multi',
            #'pyutilib.th.tests.test_pyunit.TestExpensive.test_noCategory',
            #'pyutilib.th.tests.test_pyunit.TestExpensive.test_notExpensive',
            'pyutilib.th.tests.test_pyunit.TestExpensive.test_smoke',
            #'pyutilib.th.tests.test_pyunit.TestNoCategory.test_custom',
            #'pyutilib.th.tests.test_pyunit.TestNoCategory.test_expensive',
            #'pyutilib.th.tests.test_pyunit.TestNoCategory.test_fragile',
            #'pyutilib.th.tests.test_pyunit.TestNoCategory.test_fragile_smoke',
            'pyutilib.th.tests.test_pyunit.TestNoCategory.test_multi',
            'pyutilib.th.tests.test_pyunit.TestNoCategory.test_noCategory',
            #'pyutilib.th.tests.test_pyunit.TestNoCategory.test_notExpensive',
            'pyutilib.th.tests.test_pyunit.TestNoCategory.test_smoke',
        ]
        self.assertEqual(sorted(result), sorted(ref))


    def test_custom(self):
        result = self._run(['--cat=custom'])
        ref = [
            'pyutilib.th.tests.test_pyunit.TestExpensive.test_custom',
            #'pyutilib.th.tests.test_pyunit.TestExpensive.test_expensive',
            #'pyutilib.th.tests.test_pyunit.TestExpensive.test_fragile',
            #'pyutilib.th.tests.test_pyunit.TestExpensive.test_fragile_smoke',
            'pyutilib.th.tests.test_pyunit.TestExpensive.test_multi',
            #'pyutilib.th.tests.test_pyunit.TestExpensive.test_noCategory',
            #'pyutilib.th.tests.test_pyunit.TestExpensive.test_notExpensive',
            #'pyutilib.th.tests.test_pyunit.TestExpensive.test_smoke',
            'pyutilib.th.tests.test_pyunit.TestNoCategory.test_custom',
            #'pyutilib.th.tests.test_pyunit.TestNoCategory.test_expensive',
            #'pyutilib.th.tests.test_pyunit.TestNoCategory.test_fragile',
            #'pyutilib.th.tests.test_pyunit.TestNoCategory.test_fragile_smoke',
            'pyutilib.th.tests.test_pyunit.TestNoCategory.test_multi',
            #'pyutilib.th.tests.test_pyunit.TestNoCategory.test_noCategory',
            #'pyutilib.th.tests.test_pyunit.TestNoCategory.test_notExpensive',
            #'pyutilib.th.tests.test_pyunit.TestNoCategory.test_smoke',
        ]
        self.assertEqual(sorted(result), sorted(ref))


    def test_expensive(self):
        result = self._run(['--cat=expensive'])
        ref = [
            'pyutilib.th.tests.test_pyunit.TestExpensive.test_custom',
            'pyutilib.th.tests.test_pyunit.TestExpensive.test_expensive',
            #'pyutilib.th.tests.test_pyunit.TestExpensive.test_fragile',
            #'pyutilib.th.tests.test_pyunit.TestExpensive.test_fragile_smoke',
            'pyutilib.th.tests.test_pyunit.TestExpensive.test_multi',
            'pyutilib.th.tests.test_pyunit.TestExpensive.test_noCategory',
            #'pyutilib.th.tests.test_pyunit.TestExpensive.test_notExpensive',
            'pyutilib.th.tests.test_pyunit.TestExpensive.test_smoke',
            #'pyutilib.th.tests.test_pyunit.TestNoCategory.test_custom',
            'pyutilib.th.tests.test_pyunit.TestNoCategory.test_expensive',
            #'pyutilib.th.tests.test_pyunit.TestNoCategory.test_fragile',
            #'pyutilib.th.tests.test_pyunit.TestNoCategory.test_fragile_smoke',
            #'pyutilib.th.tests.test_pyunit.TestNoCategory.test_multi',
            #'pyutilib.th.tests.test_pyunit.TestNoCategory.test_noCategory',
            #'pyutilib.th.tests.test_pyunit.TestNoCategory.test_notExpensive',
            #'pyutilib.th.tests.test_pyunit.TestNoCategory.test_smoke',
        ]
        self.assertEqual(sorted(result), sorted(ref))

    def test_expensive_AND_smoke(self):
        result = self._run(['--cat=expensive,smoke'])
        ref = [
            #'pyutilib.th.tests.test_pyunit.TestExpensive.test_custom',
            #'pyutilib.th.tests.test_pyunit.TestExpensive.test_expensive',
            #'pyutilib.th.tests.test_pyunit.TestExpensive.test_fragile',
            #'pyutilib.th.tests.test_pyunit.TestExpensive.test_fragile_smoke',
            'pyutilib.th.tests.test_pyunit.TestExpensive.test_multi',
            #'pyutilib.th.tests.test_pyunit.TestExpensive.test_noCategory',
            #'pyutilib.th.tests.test_pyunit.TestExpensive.test_notExpensive',
            'pyutilib.th.tests.test_pyunit.TestExpensive.test_smoke',
            #'pyutilib.th.tests.test_pyunit.TestNoCategory.test_custom',
            #'pyutilib.th.tests.test_pyunit.TestNoCategory.test_expensive',
            #'pyutilib.th.tests.test_pyunit.TestNoCategory.test_fragile',
            #'pyutilib.th.tests.test_pyunit.TestNoCategory.test_fragile_smoke',
            #'pyutilib.th.tests.test_pyunit.TestNoCategory.test_multi',
            #'pyutilib.th.tests.test_pyunit.TestNoCategory.test_noCategory',
            #'pyutilib.th.tests.test_pyunit.TestNoCategory.test_notExpensive',
            #'pyutilib.th.tests.test_pyunit.TestNoCategory.test_smoke',
        ]
        self.assertEqual(sorted(result), sorted(ref))

    def test_expensive_OR_smoke(self):
        result = self._run(['--cat=expensive', '--cat=smoke'])
        ref = [
            'pyutilib.th.tests.test_pyunit.TestExpensive.test_custom',
            'pyutilib.th.tests.test_pyunit.TestExpensive.test_expensive',
            #'pyutilib.th.tests.test_pyunit.TestExpensive.test_fragile',
            #'pyutilib.th.tests.test_pyunit.TestExpensive.test_fragile_smoke',
            'pyutilib.th.tests.test_pyunit.TestExpensive.test_multi',
            'pyutilib.th.tests.test_pyunit.TestExpensive.test_noCategory',
            #'pyutilib.th.tests.test_pyunit.TestExpensive.test_notExpensive',
            'pyutilib.th.tests.test_pyunit.TestExpensive.test_smoke',
            #'pyutilib.th.tests.test_pyunit.TestNoCategory.test_custom',
            'pyutilib.th.tests.test_pyunit.TestNoCategory.test_expensive',
            #'pyutilib.th.tests.test_pyunit.TestNoCategory.test_fragile',
            #'pyutilib.th.tests.test_pyunit.TestNoCategory.test_fragile_smoke',
            'pyutilib.th.tests.test_pyunit.TestNoCategory.test_multi',
            'pyutilib.th.tests.test_pyunit.TestNoCategory.test_noCategory',
            #'pyutilib.th.tests.test_pyunit.TestNoCategory.test_notExpensive',
            'pyutilib.th.tests.test_pyunit.TestNoCategory.test_smoke',
        ]
        self.assertEqual(sorted(result), sorted(ref))

    def test_NOT_expensive(self):
        result = self._run(['--cat=!expensive'])
        ref = [
            #'pyutilib.th.tests.test_pyunit.TestExpensive.test_custom',
            #'pyutilib.th.tests.test_pyunit.TestExpensive.test_expensive',
            #'pyutilib.th.tests.test_pyunit.TestExpensive.test_fragile',
            #'pyutilib.th.tests.test_pyunit.TestExpensive.test_fragile_smoke',
            #'pyutilib.th.tests.test_pyunit.TestExpensive.test_multi',
            #'pyutilib.th.tests.test_pyunit.TestExpensive.test_noCategory',
            'pyutilib.th.tests.test_pyunit.TestExpensive.test_notExpensive',
            #'pyutilib.th.tests.test_pyunit.TestExpensive.test_smoke',
            'pyutilib.th.tests.test_pyunit.TestNoCategory.test_custom',
            #'pyutilib.th.tests.test_pyunit.TestNoCategory.test_expensive',
            #'pyutilib.th.tests.test_pyunit.TestNoCategory.test_fragile',
            #'pyutilib.th.tests.test_pyunit.TestNoCategory.test_fragile_smoke',
            'pyutilib.th.tests.test_pyunit.TestNoCategory.test_multi',
            'pyutilib.th.tests.test_pyunit.TestNoCategory.test_noCategory',
            'pyutilib.th.tests.test_pyunit.TestNoCategory.test_notExpensive',
            'pyutilib.th.tests.test_pyunit.TestNoCategory.test_smoke',
        ]
        self.assertEqual(sorted(result), sorted(ref))

    def test_fragile(self):
        result = self._run(['--cat=fragile'])
        ref = [
            #'pyutilib.th.tests.test_pyunit.TestExpensive.test_custom',
            #'pyutilib.th.tests.test_pyunit.TestExpensive.test_expensive',
            'pyutilib.th.tests.test_pyunit.TestExpensive.test_fragile',
            'pyutilib.th.tests.test_pyunit.TestExpensive.test_fragile_smoke',
            #'pyutilib.th.tests.test_pyunit.TestExpensive.test_multi',
            #'pyutilib.th.tests.test_pyunit.TestExpensive.test_noCategory',
            #'pyutilib.th.tests.test_pyunit.TestExpensive.test_notExpensive',
            #'pyutilib.th.tests.test_pyunit.TestExpensive.test_smoke',
            #'pyutilib.th.tests.test_pyunit.TestNoCategory.test_custom',
            #'pyutilib.th.tests.test_pyunit.TestNoCategory.test_expensive',
            'pyutilib.th.tests.test_pyunit.TestNoCategory.test_fragile',
            'pyutilib.th.tests.test_pyunit.TestNoCategory.test_fragile_smoke',
            #'pyutilib.th.tests.test_pyunit.TestNoCategory.test_multi',
            #'pyutilib.th.tests.test_pyunit.TestNoCategory.test_noCategory',
            #'pyutilib.th.tests.test_pyunit.TestNoCategory.test_notExpensive',
            #'pyutilib.th.tests.test_pyunit.TestNoCategory.test_smoke',
        ]
        self.assertEqual(sorted(result), sorted(ref))


    def test_fragile_AND_smoke(self):
        result = self._run(['--cat=fragile,smoke'])
        ref = [
            #'pyutilib.th.tests.test_pyunit.TestExpensive.test_custom',
            #'pyutilib.th.tests.test_pyunit.TestExpensive.test_expensive',
            #'pyutilib.th.tests.test_pyunit.TestExpensive.test_fragile',
            'pyutilib.th.tests.test_pyunit.TestExpensive.test_fragile_smoke',
            #'pyutilib.th.tests.test_pyunit.TestExpensive.test_multi',
            #'pyutilib.th.tests.test_pyunit.TestExpensive.test_noCategory',
            #'pyutilib.th.tests.test_pyunit.TestExpensive.test_notExpensive',
            #'pyutilib.th.tests.test_pyunit.TestExpensive.test_smoke',
            #'pyutilib.th.tests.test_pyunit.TestNoCategory.test_custom',
            #'pyutilib.th.tests.test_pyunit.TestNoCategory.test_expensive',
            'pyutilib.th.tests.test_pyunit.TestNoCategory.test_fragile',
            'pyutilib.th.tests.test_pyunit.TestNoCategory.test_fragile_smoke',
            #'pyutilib.th.tests.test_pyunit.TestNoCategory.test_multi',
            #'pyutilib.th.tests.test_pyunit.TestNoCategory.test_noCategory',
            #'pyutilib.th.tests.test_pyunit.TestNoCategory.test_notExpensive',
            #'pyutilib.th.tests.test_pyunit.TestNoCategory.test_smoke',
        ]
        self.assertEqual(sorted(result), sorted(ref))


    def test_fragile_OR_smoke(self):
        result = self._run(['--cat=fragile', '--cat=smoke'])
        ref = [
            #'pyutilib.th.tests.test_pyunit.TestExpensive.test_custom',
            #'pyutilib.th.tests.test_pyunit.TestExpensive.test_expensive',
            'pyutilib.th.tests.test_pyunit.TestExpensive.test_fragile',
            'pyutilib.th.tests.test_pyunit.TestExpensive.test_fragile_smoke',
            'pyutilib.th.tests.test_pyunit.TestExpensive.test_multi',
            #'pyutilib.th.tests.test_pyunit.TestExpensive.test_noCategory',
            #'pyutilib.th.tests.test_pyunit.TestExpensive.test_notExpensive',
            'pyutilib.th.tests.test_pyunit.TestExpensive.test_smoke',
            #'pyutilib.th.tests.test_pyunit.TestNoCategory.test_custom',
            #'pyutilib.th.tests.test_pyunit.TestNoCategory.test_expensive',
            'pyutilib.th.tests.test_pyunit.TestNoCategory.test_fragile',
            'pyutilib.th.tests.test_pyunit.TestNoCategory.test_fragile_smoke',
            'pyutilib.th.tests.test_pyunit.TestNoCategory.test_multi',
            'pyutilib.th.tests.test_pyunit.TestNoCategory.test_noCategory',
            #'pyutilib.th.tests.test_pyunit.TestNoCategory.test_notExpensive',
            'pyutilib.th.tests.test_pyunit.TestNoCategory.test_smoke',
        ]
        self.assertEqual(sorted(result), sorted(ref))


