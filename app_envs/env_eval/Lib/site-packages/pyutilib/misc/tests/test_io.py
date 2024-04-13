#
# Unit Tests for util/*_io
#
#

import os
import sys
from os.path import abspath, dirname
pkgdir = dirname(abspath(__file__)) + os.sep + ".." + os.sep + ".."
currdir = dirname(abspath(__file__)) + os.sep
import six

import pyutilib.th as unittest
import pyutilib.misc


def filter1(str):
    return True


def filter2(str):
    return ""


def filter3(str):
    str = str.replace('THERE', 'HERE')
    str = str.replace('[4, 5, 6]', '[1,2,3]')
    return str


class IODebug(unittest.TestCase):

    def test_redirect1(self):
        # Verify that IO redirection works
        pyutilib.misc.setup_redirect(currdir + "redirect_io.out")
        print("HERE")
        print([1, 2, 3])
        #
        # Force a flush to ensure code coverage
        #
        sys.stdout.flush()
        pyutilib.misc.reset_redirect()
        self.assertFalse(
            pyutilib.misc.comparison.compare_file(
                currdir + "redirect_io.out", currdir + "redirect_io1.txt")[0])
        self.assertFalse(
            pyutilib.misc.comparison.compare_file(
                currdir + "redirect_io.out",
                currdir + "redirect_io2.txt",
                filter=filter1)[0])
        self.assertFalse(
            pyutilib.misc.comparison.compare_file(
                currdir + "redirect_io.out",
                currdir + "redirect_io2.txt",
                filter=filter2)[0])
        os.remove(currdir + "redirect_io.out")

    def test_redirect2(self):
        # Verify that IO redirection will create an empty file is no output is generated
        pyutilib.misc.setup_redirect(currdir + "redirect_io.out")
        pyutilib.misc.reset_redirect()
        if not os.path.exists(currdir + "redirect_io.out"):
            self.fail("Redirection did not create an empty file.")
        self.assertFalse(
            pyutilib.misc.comparison.compare_file(
                currdir + "redirect_io.out", currdir + "redirect_io2.txt")[0])
        os.remove(currdir + "redirect_io.out")

    def test_redirect3(self):
        # Verify that IO redirection can be nested
        pyutilib.misc.setup_redirect(currdir + "redirect_io1.out")
        print("HERE")
        pyutilib.misc.setup_redirect(currdir + "redirect_io3.out")
        print("THERE")
        print([4, 5, 6])
        pyutilib.misc.reset_redirect()
        print([1, 2, 3])
        #
        # Force a flush to ensure code coverage
        #
        sys.stdout.flush()
        pyutilib.misc.reset_redirect()
        self.assertFalse(
            pyutilib.misc.comparison.compare_file(
                currdir + "redirect_io1.out", currdir + "redirect_io1.txt")[0])
        os.remove(currdir + "redirect_io1.out")
        self.assertFalse(
            pyutilib.misc.comparison.compare_file(
                currdir + "redirect_io3.out", currdir + "redirect_io3.txt")[0])
        self.assertFalse(
            pyutilib.misc.comparison.compare_file(
                currdir + "redirect_io3.out",
                currdir + "redirect_io3.txt",
                filter=filter3)[0])
        os.remove(currdir + "redirect_io3.out")

    def test_redirect4(self):
        # Verify that IO redirection works with file-like objects
        output = six.StringIO()
        pyutilib.misc.setup_redirect(output)
        print("HERE")
        print([1, 2, 3])
        #
        # Force a flush to ensure code coverage
        #
        sys.stdout.flush()
        pyutilib.misc.reset_redirect()
        self.assertEqual(output.getvalue(), "HERE\n[1, 2, 3]\n")

    def test_format_io(self):
        # Test that formated IO looks correct.
        pyutilib.misc.setup_redirect(currdir + "format_io.out")
        print(pyutilib.misc.format_io(0.0))
        print(pyutilib.misc.format_io(0))
        print(pyutilib.misc.format_io(1e-1))
        print(pyutilib.misc.format_io(1e+1))
        print(pyutilib.misc.format_io(1e-9))
        print(pyutilib.misc.format_io(1e+9))
        print(pyutilib.misc.format_io(1e-99))
        print(pyutilib.misc.format_io(1e+99))
        print(pyutilib.misc.format_io(1e-100))
        print(pyutilib.misc.format_io(1e+100))
        print(pyutilib.misc.format_io(-1e-1))
        print(pyutilib.misc.format_io(-1e+1))
        print(pyutilib.misc.format_io(-1e-9))
        print(pyutilib.misc.format_io(-1e+9))
        print(pyutilib.misc.format_io(-1e-99))
        print(pyutilib.misc.format_io(-1e+99))
        print(pyutilib.misc.format_io(-1e-100))
        print(pyutilib.misc.format_io(-1e+100))
        print(pyutilib.misc.format_io('string'))
        pyutilib.misc.reset_redirect()
        self.assertFalse(
            pyutilib.misc.comparison.compare_file(currdir + "format_io.out",
                                                  currdir + "format_io.txt")[0])
        os.remove(currdir + "format_io.out")

    def test_format_float_err1(self):
        # Test that errors are generated for non floats
        try:
            pyutilib.misc.format_float('1')
            self.fail("Should have thrown a TypeError exception")
        except TypeError:
            pass

    def test_indenter_write(self):
        output = six.StringIO()
        indenter = pyutilib.misc.StreamIndenter(output, "X ")
        indenter.write("foo")
        self.assertEqual(output.getvalue(), "X foo")
        indenter.write("\n")
        self.assertEqual(output.getvalue(), "X foo\n")
        indenter.write("foo\n")
        self.assertEqual(output.getvalue(), "X foo\nX foo\n")
        indenter.write("")
        self.assertEqual(output.getvalue(), "X foo\nX foo\n")
        indenter.write("\n")
        self.assertEqual(output.getvalue(), "X foo\nX foo\nX\n")
        indenter.write("baz\nbin")
        self.assertEqual(output.getvalue(), "X foo\nX foo\nX\nX baz\nX bin")
        indenter.write("a\nb\n\nc\n")
        self.assertEqual(output.getvalue(),
                         "X foo\nX foo\nX\nX baz\nX bina\nX b\nX\nX c\n")

        self.assertEqual(indenter.closed, False)
        indenter.close()
        self.assertEqual(indenter.closed, True)

    def test_indenter_writelines(self):
        output = six.StringIO()
        indenter = pyutilib.misc.StreamIndenter(output, "X")
        indenter.writelines(["foo"])
        self.assertEqual(output.getvalue(), "Xfoo")
        indenter.writelines(["foo\n", "bar\n"])
        self.assertEqual(output.getvalue(), "Xfoofoo\nXbar\n")
        indenter.writelines(["", ""])
        self.assertEqual(output.getvalue(), "Xfoofoo\nXbar\n")

        self.assertEqual(indenter.closed, False)
        indenter.close()
        self.assertEqual(indenter.closed, True)

    def test_redirected_stdout(self):
        with pyutilib.misc.capture_output() as output:
            print("test1")
            print("test2")
        self.assertEqual(output.getvalue(), "test1\ntest2\n")

    def test_redirected_stdout_with_arg(self):
        stream = six.StringIO()
        stream.write("before\n")
        with pyutilib.misc.capture_output(stream) as output:
            print("test1")
            print("test2")
        self.assertEqual(output.getvalue(), "before\ntest1\ntest2\n")


if __name__ == "__main__":
    unittest.main()
