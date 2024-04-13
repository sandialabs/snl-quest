#
# Unit Tests for util/misc/import_file
#
#

import os
import sys
from os.path import abspath, dirname
pkgdir = dirname(abspath(__file__)) + os.sep + ".." + os.sep + ".."
currdir = dirname(abspath(__file__)) + os.sep

import pyutilib.misc
import pyutilib.th as unittest
import pyutilib.misc.comparison

try:
    import runpy
    _runpy = True
except:
    _runpy = False


class TestRunFile(unittest.TestCase):

    def test_run_file1(self):
        pyutilib.misc.run_file(
            currdir + "import1.py", logfile=currdir + "import1.log")
        if not os.path.exists(currdir + "import1.log"):
            self.fail("test_run_file - failed to create logfile")
        self.assertFalse(
            pyutilib.misc.comparison.compare_file(currdir + "import1.log",
                                                  currdir + "import1.txt")[0])
        os.remove(currdir + "import1.log")

    def test_run_file2(self):
        pyutilib.misc.run_file(
            "import1.py", logfile=currdir + "import1.log", execdir=currdir)
        if not os.path.exists(currdir + "import1.log"):
            self.fail("test_run_file - failed to create logfile")
        self.assertFalse(
            pyutilib.misc.comparison.compare_file(currdir + "import1.log",
                                                  currdir + "import1.txt")[0])
        os.remove(currdir + "import1.log")

    def test_run_file3(self):
        try:
            pyutilib.misc.run_file(
                "import2.py", logfile=currdir + "import2.log", execdir=currdir)
            self.fail("test_run_file - expected type error in import2.py")
        except TypeError:
            pass
        self.assertFalse(
            pyutilib.misc.comparison.compare_file(currdir + "import2.log",
                                                  currdir + "import2.txt")[0])
        os.remove(currdir + "import2.log")

    def test_run_file_exception(self):
        orig_path = list(sys.path)
        with self.assertRaisesRegexp(RuntimeError, "raised from __main__"):
            pyutilib.misc.run_file(
                "import_main_exception.py",
                logfile=currdir + "import_main_exception.log", execdir=currdir)

        self.assertFalse(
            pyutilib.misc.comparison.compare_file(
                currdir + "import_main_exception.log",
                currdir + "import_main_exception.txt")[0])
        os.remove(currdir + "import_main_exception.log")
        self.assertIsNot(orig_path, sys.path)
        self.assertEqual(orig_path, sys.path)


class TestImportFile(unittest.TestCase):

    def setUp(self):
        self._mods = list(sys.modules.keys())

    def tearDown(self):
        to_del = [m for m in sys.modules.keys() if m not in self._mods]
        for mod in to_del:
            del sys.modules[mod]

    def test_import_file_context1(self):
        pyutilib.misc.import_file(currdir + "import1.py")
        if "import1" in globals():
            self.fail(
                "test_import_file - globals() should not be affected by import")

    def test_import_file_context2(self):
        import1 = pyutilib.misc.import_file(currdir + "import1.py")
        try:
            c = import1.a
        except:
            self.fail("test_import_file - could not access data in import.py")

    def test_import_file_context3(self):
        pyutilib.misc.import_file(currdir + "import1.py", context=globals())
        if not "import1" in globals():
            self.fail("test_import_file - failed to import the import1.py file")

    def test_import_exception(self):
        orig_path = list(sys.path)
        with self.assertRaisesRegexp(RuntimeError, "raised during import"):
            pyutilib.misc.import_file(currdir + "import_exception.py")
        self.assertIsNot(orig_path, sys.path)
        self.assertEqual(orig_path, sys.path)

    def test1(self):
        try:
            pyutilib.misc.import_file('tfile.py')
        except IOError:
            pass
        else:
            self.fail('File does not exist. Expected IOError.')

    def test2(self):
        try:
            pyutilib.misc.import_file('tfile')
        except ImportError:
            pass
        else:
            self.fail('Module does not exist. Expected ImportError.')

    def test3(self):
        dirname = currdir + 'import_data' + os.sep + 'a'
        sys.path.insert(0, dirname)
        context = {}
        m = pyutilib.misc.import_file('tfile', context=context)
        self.assertEqual(id(m), id(context['tfile']))
        self.assertEqual(m.f(), 'a')
        sys.path.remove(dirname)

    def test4(self):
        dirname = currdir + 'import_data' + os.sep + 'a'
        sys.path.insert(0, dirname)
        context = {}
        m = pyutilib.misc.import_file('tfile', context=context)
        self.assertEqual(id(m), id(context['tfile']))
        self.assertEqual(m.f(), 'a')
        sys.path.remove(dirname)
        dirname = currdir + 'import_data' + os.sep + 'b'
        sys.path.insert(0, dirname)
        m = pyutilib.misc.import_file('tfile', context=context, name='junk')
        self.assertEqual(id(m), id(context['junk']))
        self.assertEqual(m.f(), 'b')
        sys.path.remove(dirname)

    def test4a(self):
        dirname = currdir + 'import_data' + os.sep + 'a'
        sys.path.insert(0, dirname)
        context = {}
        m = pyutilib.misc.import_file('tfile', context=context)
        self.assertEqual(id(m), id(context['tfile']))
        self.assertEqual(m.f(), 'a')
        sys.path.remove(dirname)
        dirname = currdir + 'import_data' + os.sep + 'b'
        sys.path.insert(0, dirname)
        m = pyutilib.misc.import_file('tfile', context=context)
        self.assertEqual(id(m), id(context['tfile']))
        self.assertEqual(m.f(), 'a')
        sys.path.remove(dirname)

    def test5(self):
        dirname = currdir + 'import_data' + os.sep + 'a' + os.sep
        context = {}
        m = pyutilib.misc.import_file(dirname + 'tfile', context=context)
        self.assertEqual(id(m), id(context['tfile']))
        self.assertEqual(m.f(), 'a')

    def test6(self):
        dirname = currdir + 'import_data' + os.sep + 'a' + os.sep
        context = {}
        m = pyutilib.misc.import_file(dirname + 'tfile', context=context)
        self.assertEqual(id(m), id(context['tfile']))
        self.assertEqual(m.f(), 'a')
        dirname = currdir + 'import_data' + os.sep + 'b' + os.sep
        m = pyutilib.misc.import_file(
            dirname + 'tfile', context=context, name='junk')
        self.assertEqual(id(m), id(context['junk']))
        self.assertEqual(m.f(), 'b')

    def test6a(self):
        dirname = currdir + 'import_data' + os.sep + 'a' + os.sep
        context = {}
        m = pyutilib.misc.import_file(dirname + 'tfile', context=context)
        self.assertEqual(id(m), id(context['tfile']))
        self.assertEqual(m.f(), 'a')
        dirname = currdir + 'import_data' + os.sep + 'b' + os.sep
        m = pyutilib.misc.import_file(dirname + 'tfile', context=context)
        self.assertEqual(id(m), id(context['tfile']))
        self.assertEqual(m.f(), 'a')

    def test7(self):
        dirname = currdir + 'import_data' + os.sep + 'a' + os.sep
        context = {}
        m = pyutilib.misc.import_file(dirname + 'tfile.py', context=context)
        self.assertEqual(id(m), id(context['tfile']))
        self.assertEqual(m.f(), 'a')

    def test8(self):
        dirname = currdir + 'import_data' + os.sep + 'a' + os.sep
        context = {}
        m = pyutilib.misc.import_file(dirname + 'tfile.py', context=context)
        self.assertEqual(id(m), id(context['tfile']))
        self.assertEqual(m.f(), 'a')
        dirname = currdir + 'import_data' + os.sep + 'b' + os.sep
        m = pyutilib.misc.import_file(
            dirname + 'tfile.py', context=context, name='junk')
        self.assertEqual(id(m), id(context['junk']))
        self.assertEqual(m.f(), 'b')

    def test8a(self):
        dirname = currdir + 'import_data' + os.sep + 'a' + os.sep
        context = {}
        m = pyutilib.misc.import_file(dirname + 'tfile.py', context=context)
        self.assertEqual(id(m), id(context['tfile']))
        self.assertEqual(m.f(), 'a')
        dirname = currdir + 'import_data' + os.sep + 'b' + os.sep
        m = pyutilib.misc.import_file(dirname + 'tfile.py', context=context)
        self.assertEqual(id(m), id(context['tfile']))
        self.assertEqual(m.f(), 'a')

    def test9(self):
        try:
            pyutilib.misc.import_file('foo/bar')
        except ImportError:
            pass
        else:
            self.fail('Module does not exist. Expected ImportError.')

    def test9a(self):
        try:
            pyutilib.misc.import_file('foo/bar', name='junk')
        except ImportError:
            pass
        else:
            self.fail('Module does not exist. Expected ImportError.')

    def test10(self):
        try:
            pyutilib.misc.import_file('foo.bar')
        except ImportError:
            pass
        else:
            self.fail('Module does not exist. Expected ImportError.')

    def test10a(self):
        try:
            pyutilib.misc.import_file('foo.bar', name='junk')
        except ImportError:
            pass
        else:
            self.fail('Module does not exist. Expected ImportError.')

    def test11(self):
        try:
            pyutilib.misc.import_file('baz/foo.bar')
        except ImportError:
            pass
        else:
            self.fail('Module does not exist. Expected ImportError.')

    def test11a(self):
        try:
            pyutilib.misc.import_file('baz/foo.bar', name='junk')
        except ImportError:
            pass
        else:
            self.fail('Module does not exist. Expected ImportError.')

    def test12(self):
        dirname = currdir + 'import_data'
        sys.path.insert(0, dirname)
        context = {}
        m = pyutilib.misc.import_file('tfile1.0', context=context)
        self.assertEqual(id(m), id(context['tfile1.0']))
        self.assertEqual(m.f(), 'tfile1.0')
        sys.path.remove(dirname)

    def test12a(self):
        dirname = currdir + 'import_data'
        sys.path.insert(0, dirname)
        context = {}
        m = pyutilib.misc.import_file('tfile1.0', context=context, name='junk')
        self.assertEqual(id(m), id(context['junk']))
        self.assertEqual(m.f(), 'tfile1.0')
        sys.path.remove(dirname)

    def test13(self):
        dirname = currdir + 'import_data' + os.sep
        context = {}
        m = pyutilib.misc.import_file(dirname + 'tfile1.0', context=context)
        self.assertEqual(id(m), id(context['tfile1.0']))
        self.assertEqual(m.f(), 'tfile1.0')

    def test13a(self):
        dirname = currdir + 'import_data' + os.sep
        context = {}
        m = pyutilib.misc.import_file(
            dirname + 'tfile1.0', context=context, name='junk')
        self.assertEqual(id(m), id(context['junk']))
        self.assertEqual(m.f(), 'tfile1.0')

    def test14(self):
        context = {}
        m = pyutilib.misc.import_file(
            'pyutilib.misc.tests.import_data.a.tfile', context=context)
        self.assertEqual(
            id(m), id(context['pyutilib.misc.tests.import_data.a.tfile']))
        self.assertEqual(m.f(), 'a')

# Apply decorator explicitly
TestRunFile = unittest.skipIf(not _runpy, "Cannot import 'runpy'")(TestRunFile)

if __name__ == "__main__":
    unittest.main()
