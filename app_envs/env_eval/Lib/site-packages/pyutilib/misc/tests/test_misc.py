#
# Unit Tests for util/misc
#
#

import pickle
import sys
import os
from os.path import abspath, dirname
currdir = dirname(abspath(__file__)) + os.sep
import pyutilib.th as unittest
import pyutilib.misc
import pyutilib.misc.comparison


class Test(unittest.TestCase):

    def test_tostr(self):
        # Verify that tostr() generates a string
        str = pyutilib.misc.tostr([0.0, 1])
        self.assertEqual(str, "0.0 1")
        str = pyutilib.misc.tostr([])
        self.assertEqual(str, "")

    def test_flatten_tuple1(self):
        # Verify that flatten_tuple() flattens a normal tuple
        tmp = (1, "2", 3.0)
        ans = pyutilib.misc.flatten_tuple(tmp)
        self.assertEqual(ans, tmp)

    def test_flatten_tuple2(self):
        # Verify that flatten_tuple() flattens a nested tuple
        tmp = (1, "2", (4, ("5.0", (6))), 3.0)
        ans = pyutilib.misc.flatten_tuple(tmp)
        target = (1, "2", 4, "5.0", 6, 3.0)
        self.assertEqual(ans, target)

    def test_flatten_tuple3(self):
        # Verify that flatten_tuple() returns a non-tuple
        tmp = [1, "2", 3.0]
        ans = pyutilib.misc.flatten_tuple(tmp)
        self.assertEqual(ans, tmp)

    def test_flatten_tuple4(self):
        # Verify that flatten_tuple() removes empty tuples
        tmp = ((), 1, (), "2", ((), 4, ((), "5.0", (6), ()), ()), 3.0, ())
        ans = pyutilib.misc.flatten_tuple(tmp)
        target = (1, "2", 4, "5.0", 6, 3.0)
        self.assertEqual(ans, target)

    def test_flatten_tuple5(self):
        # Verify that flatten_tuple() can collapse to a single empty tuple
        self.assertEqual((1, 2, 3, 4, 5), pyutilib.misc.flatten_tuple((
            (), 1, (), 2, ((), 3, ((), 4, ()), ()), 5, ())))
        self.assertEqual((), pyutilib.misc.flatten_tuple(((((), ()), ()), ())))
        self.assertEqual((), pyutilib.misc.flatten_tuple(((), ((), ((),)))))

    def test_flatten_list1(self):
        # Verify that flatten_list() flattens a normal list
        tmp = [1, "2", 3.0]
        ans = pyutilib.misc.flatten_list(tmp)
        self.assertEqual(ans, tmp)

    def test_flatten_list2(self):
        # Verify that flatten_list() flattens a nested list
        tmp = [1, "2", [4, ["5.0", [6]]], 3.0]
        ans = pyutilib.misc.flatten_list(tmp)
        target = [1, "2", 4, "5.0", 6, 3.0]
        self.assertEqual(ans, target)

    def test_flatten_list3(self):
        # Verify that flatten_list() returns a non-list
        tmp = (1, "2", 3.0)
        ans = pyutilib.misc.flatten_list(tmp)
        self.assertEqual(ans, tmp)

    def test_flatten_list4(self):
        # Verify that flatten_list() removes empty lists
        tmp = [[], 1, [], "2", [[], 4, [[], "5.0", [6], []], []], 3.0, []]
        ans = pyutilib.misc.flatten_list(tmp)
        target = [1, "2", 4, "5.0", 6, 3.0]
        self.assertEqual(ans, target)

    def test_flatten_list5(self):
        # Verify that flatten_list() can collapse to a single empty list
        self.assertEqual([1, 2, 3, 4, 5], pyutilib.misc.flatten_list(
            [[], 1, [], 2, [[], 3, [[], 4, []], []], 5, []]))
        self.assertEqual([], pyutilib.misc.flatten_list([[[[], []], []], []]))
        self.assertEqual([], pyutilib.misc.flatten_list([[], [[], [[],]]]))

    def test_Bunch(self):
        a = 1
        b = "b"
        tmp = pyutilib.misc.Bunch(a=a, b=b)
        self.assertEqual(tmp.a, a)
        self.assertEqual(tmp.b, b)

    def test_Container1(self):
        opt = pyutilib.misc.Container('a=None c=d e="1 2 3"', foo=1, bar='x')
        self.assertEqual(opt.ll, None)
        self.assertEqual(opt.a, None)
        self.assertEqual(opt.c, 'd')
        self.assertEqual(opt.e, '1 2 3')
        self.assertEqual(opt.foo, 1)
        self.assertEqual(opt.bar, 'x')
        self.assertEqual(opt['bar'], 'x')
        opt.xx = 1
        opt['yy'] = 2
        self.assertEqual(
            set(opt.keys()), set(['a', 'bar', 'c', 'foo', 'e', 'xx', 'yy']))
        opt.x = pyutilib.misc.Container(a=1, b=2)
        self.assertEqual(
            set(opt.keys()), set(
                ['a', 'bar', 'c', 'foo', 'e', 'xx', 'yy', 'x']))
        self.assertEqual(
            repr(opt),
            "Container(a = None, bar = 'x', c = 'd', e = '1 2 3', foo = 1, x = Container(a = 1, b = 2), xx = 1, yy = 2)")
        self.assertEqual(
            str(opt), """a: None
bar: 'x'
c: 'd'
e: '1 2 3'
foo: 1
x:
    a: 1
    b: 2
xx: 1
yy: 2""")
        opt._name_ = 'CONTAINER'
        self.assertEqual(
            set(opt.keys()), set(
                ['a', 'bar', 'c', 'foo', 'e', 'xx', 'yy', 'x']))
        self.assertEqual(
            repr(opt),
            "Container(a = None, bar = 'x', c = 'd', e = '1 2 3', foo = 1, x = Container(a = 1, b = 2), xx = 1, yy = 2)")
        self.assertEqual(
            str(opt), """a: None
bar: 'x'
c: 'd'
e: '1 2 3'
foo: 1
x:
    a: 1
    b: 2
xx: 1
yy: 2""")

    def test_Container2(self):
        o1 = pyutilib.misc.Container('a=None c=d e="1 2 3"', foo=1, bar='x')
        s = pickle.dumps(o1)
        o2 = pickle.loads(s)
        self.assertEqual(o1, o2)

    def test_flatten1(self):
        # Test that flatten works correctly
        self.assertEqual("abc", pyutilib.misc.flatten("abc"))
        self.assertEqual(1, pyutilib.misc.flatten(1))
        self.assertEqual([1, 2, 3], pyutilib.misc.flatten((1, 2, 3)))
        self.assertEqual([1, 2, 3], pyutilib.misc.flatten([1, 2, 3]))
        self.assertEqual([1, 2, 3, 4], pyutilib.misc.flatten((1, 2, [3, 4])))
        self.assertEqual([1, 2, 'abc'], pyutilib.misc.flatten((1, 2, 'abc')))
        self.assertEqual([1, 2, 'abc'], pyutilib.misc.flatten((1, 2, ('abc',))))
        a = [0, 9, 8]
        self.assertEqual([1, 2, 0, 9, 8], pyutilib.misc.flatten((1, 2, a)))
        self.assertEqual([1, 2, 3, 4, 5], pyutilib.misc.flatten(
            [[], 1, [], 2, [[], 3, [[], 4, []], []], 5, []]))
        self.assertEqual([], pyutilib.misc.flatten([[[[], []], []], []]))
        self.assertEqual([], pyutilib.misc.flatten([[], [[], [[],]]]))

    def test_quote_split(self):
        ans = pyutilib.misc.quote_split("[ ]+", "a bb ccc")
        self.assertEqual(ans, ["a", "bb", "ccc"])
        ans = pyutilib.misc.quote_split("[ ]+", "")
        self.assertEqual(ans, [""])
        ans = pyutilib.misc.quote_split("[ ]+", 'a "bb ccc"')
        self.assertEqual(ans, ["a", "\"bb ccc\""])
        ans = pyutilib.misc.quote_split("[ ]+", "a 'bb ccc'")
        self.assertEqual(ans, ["a", "'bb ccc'"])
        ans = pyutilib.misc.quote_split("[ ]+", "a X\"bb ccc\"Y")
        self.assertEqual(ans, ["a", "X\"bb ccc\"Y"])
        ans = pyutilib.misc.quote_split("[ ]+", "a X'bb ccc'Y")
        self.assertEqual(ans, ["a", "X'bb ccc'Y"])
        ans = pyutilib.misc.quote_split("[ ]+", "a X'bb ccc'Y A")
        self.assertEqual(ans, ["a", "X'bb ccc'Y", "A"])
        try:
            ans = pyutilib.misc.quote_split("[ ]+", 'a "bb ccc')
            self.fail(
                "test_quote_split - failed to detect unterminated quotation")
        except ValueError:
            pass

        ans = pyutilib.misc.quote_split("a bb\\\" ccc")
        self.assertEqual(ans, ["a", "bb\\\"", "ccc"])
        self.assertRaises(ValueError, pyutilib.misc.quote_split,
                          ("a bb\\\\\" ccc"))
        ans = pyutilib.misc.quote_split("a \"bb  ccc\"")
        self.assertEqual(ans, ["a", "\"bb  ccc\""])
        ans = pyutilib.misc.quote_split("a 'bb \" ccc'")
        self.assertEqual(ans, ["a", "'bb \" ccc'"])
        ans = pyutilib.misc.quote_split("a \"bb ' ccc\"")
        self.assertEqual(ans, ["a", "\"bb ' ccc\""])
        ans = pyutilib.misc.quote_split("a \"bb \\\\\\\" ccc\"")
        self.assertEqual(ans, ["a", "\"bb \\\\\\\" ccc\""])
        ans = pyutilib.misc.quote_split('b', "abbbccc")
        self.assertEqual(ans, ["a", '', '', 'ccc'])
        ans = pyutilib.misc.quote_split('b+', "abbbccc")
        self.assertEqual(ans, ["a", 'ccc'])
        ans = pyutilib.misc.quote_split(' ', "a b\ c")
        self.assertEqual(ans, ["a", 'b\ c'])

    def test_tuplize(self):
        ans = pyutilib.misc.tuplize([0, 1, 2, 3, 4, 5], 2, "a")
        self.assertEqual(ans, [(0, 1), (2, 3), (4, 5)])
        try:
            ans = pyutilib.misc.tuplize([0, 1, 2, 3, 4, 5, 6], 2, "a")
            self.fail("test_tuplize failed to detect bad list length")
        except ValueError:
            pass

    def test_rmtree(self):
        if os.path.exists(".test_misc"):
            pyutilib.misc.rmtree(".test_misc")
        os.makedirs(".test_misc/a/b/c")
        OUTPUT = open(".test_misc/a/file", "w")
        OUTPUT.write("HERE\n")
        OUTPUT.close()
        pyutilib.misc.rmtree(".test_misc")
        if os.path.exists(".test_misc"):
            self.fail("test_rmtree failed to delete .test_misc dir")

    def test_search_file(self):
        # Test that search_file works
        ans = pyutilib.misc.search_file("foobar")
        self.assertEqual(ans, None)
        path = sys.path + [currdir]
        ans = pyutilib.misc.search_file("test1.cfg", search_path=path)
        self.assertEqual(ans, abspath(currdir + "test1.cfg"))
        ans = pyutilib.misc.search_file("test1.cfg", search_path=currdir)
        self.assertEqual(ans, abspath(currdir + "test1.cfg"))
        ans = pyutilib.misc.search_file(
            "test1", implicitExt=".cfg", search_path=path)
        self.assertEqual(ans, abspath(currdir + "test1.cfg"))

    def test_search_file2(self):
        # Test that search_file works with an empty PATH environment
        tmp = os.environ["PATH"]
        del os.environ["PATH"]
        ans = pyutilib.misc.search_file("_cd_")
        os.environ["PATH"] = tmp
        self.assertEqual(ans, None)

    def test_search_file3(self):
        # Test that search_file works with a validation function
        def validate_ls(filename):
            if filename.endswith('ls'):
                return False
            return True

        tmp = os.environ["PATH"]
        del os.environ["PATH"]
        ans = pyutilib.misc.search_file("ls", validate=validate_ls)
        os.environ["PATH"] = tmp
        self.assertEqual(ans, None)

    def test_file_compare1(self):
        # Test that file comparison works
        [flag, lineno, diffstr] = pyutilib.misc.compare_file(
            currdir + "filecmp1.txt", currdir + "filecmp1.txt")
        if flag:
            self.fail(
                "test_file_compare1 - found differences in filecmp1.txt at line "
                + str(lineno))
        [flag, lineno, diffstr] = pyutilib.misc.compare_file(
            currdir + "filecmp1.txt", currdir + "filecmp2.txt")
        if flag:
            self.fail(
                "test_file_compare1 - found differences between filecmp1.txt filecmp2.txt at line "
                + str(lineno))
        [flag, lineno, diffstr] = pyutilib.misc.compare_file(
            currdir + "filecmp1.txt", currdir + "filecmp3.txt")
        if not flag or lineno != 4:
            self.fail("test_file_compare1 - expected difference at line 4")
        [flag, lineno, diffstr] = pyutilib.misc.compare_file(
            currdir + "filecmp1.txt", currdir + "filecmp4.txt")
        if not flag or lineno != 3:
            self.fail("test_file_compare1 - expected difference at line 3")
        try:
            [flag, lineno, diffstr] = pyutilib.misc.compare_file(
                currdir + "foo.txt", currdir + "bar.txt")
            self.fail("test_file_compare1 - should have failed to find foo.txt")
        except IOError:
            pass
        try:
            [flag, lineno, diffstr] = pyutilib.misc.compare_file(
                currdir + "filecmp1.txt", currdir + "bar.txt")
            self.fail("test_file_compare1 - should have failed to find bar.txt")
        except IOError:
            pass

    def test_file_compare1a(self):
        # Test that file comparison works without numeric values
        [flag, lineno, diffstr
        ] = pyutilib.misc.compare_file_with_numeric_values(
            currdir + "filecmp1.txt", currdir + "filecmp1.txt")
        if flag:
            self.fail(
                "test_file_compare1a - found differences in filecmp1.txt at line "
                + str(lineno))
        [flag, lineno, diffstr
        ] = pyutilib.misc.compare_file_with_numeric_values(
            currdir + "filecmp1.txt", currdir + "filecmp2.txt")
        if flag:
            self.fail(
                "test_file_compare1a - found differences between filecmp1.txt filecmp2.txt at line "
                + str(lineno))
        [flag, lineno, diffstr
        ] = pyutilib.misc.compare_file_with_numeric_values(
            currdir + "filecmp1.txt", currdir + "filecmp3.txt")
        if not flag or lineno != 4:
            self.fail("test_file_compare1a - expected difference at line 4",
                      ", got %s, %s" % (flag, lineno))
        [flag, lineno, diffstr
        ] = pyutilib.misc.compare_file_with_numeric_values(
            currdir + "filecmp1.txt", currdir + "filecmp4.txt")
        if not flag or lineno != 3:
            self.fail("test_file_compare1a - expected difference at line 3"
                      ", got %s, %s" % (flag, lineno))
        try:
            [flag, lineno, diffstr
            ] = pyutilib.misc.compare_file_with_numeric_values(
                currdir + "foo.txt", currdir + "bar.txt")
            self.fail(
                "test_file_compare1a - should have failed to find foo.txt")
        except IOError:
            pass
        try:
            [flag, lineno, diffstr
            ] = pyutilib.misc.compare_file_with_numeric_values(
                currdir + "filecmp1.txt", currdir + "bar.txt")
            self.fail(
                "test_file_compare1a - should have failed to find bar.txt")
        except IOError:
            pass

    def test_file_compare1b(self):
        # Test that file comparison works with numeric values
        [flag, lineno, diffstr] = pyutilib.misc.compare_file(
            currdir + "filecmp6.txt", currdir + "filecmp7.txt")
        if not flag:
            self.fail(
                "test_file_compare1b - expected differences in filecmp6.txt and filecmp7.txt at line 1")
        #
        #
        [flag, lineno, diffstr
        ] = pyutilib.misc.compare_file_with_numeric_values(
            currdir + "filecmp6.txt", currdir + "filecmp7.txt")
        if flag:
            self.fail(
                "test_file_compare1b - unexpected differences in filecmp6.txt and filecmp7.txt at line %d"
                % lineno)
        #
        [flag, lineno, diffstr
        ] = pyutilib.misc.compare_file_with_numeric_values(
            currdir + "filecmp6.txt", currdir + "filecmp8.txt")
        if not flag:
            self.fail(
                "test_file_compare1b - expected differences in filecmp6.txt and filecmp8.txt at line 1")
        #
        [flag, lineno, diffstr
        ] = pyutilib.misc.compare_file_with_numeric_values(
            currdir + "filecmp6.txt", currdir + "filecmp8.txt", tolerance=1e-2)
        if flag:
            self.fail(
                "test_file_compare1b - unexpected differences in filecmp6.txt and filecmp8.txt at line %d"
                % lineno)
        #
        [flag, lineno, diffstr
        ] = pyutilib.misc.compare_file_with_numeric_values(
            currdir + "filecmp10.txt",
            currdir + "filecmp11.txt",
            tolerance=1e-2)
        if flag:
            self.fail(
                "test_file_compare1b - unexpected differences in filecmp10.txt and filecmp11.txt at line %d"
                % lineno)
        #
        #
        [flag, lineno, diffstr] = pyutilib.misc.compare_file(
            currdir + "filecmp6.txt", currdir + "filecmp7.txt", tolerance=0.0)
        if flag:
            self.fail(
                "test_file_compare1b - unexpected differences in filecmp6.txt and filecmp7.txt at line %d"
                % lineno)
        #
        [flag, lineno, diffstr] = pyutilib.misc.compare_file(
            currdir + "filecmp6.txt", currdir + "filecmp8.txt", tolerance=0.0)
        if not flag:
            self.fail(
                "test_file_compare1b - expected differences in filecmp6.txt and filecmp8.txt at line 1")
        #
        [flag, lineno, diffstr] = pyutilib.misc.compare_file(
            currdir + "filecmp6.txt", currdir + "filecmp8.txt", tolerance=1e-2)
        if flag:
            self.fail(
                "test_file_compare1b - unexpected differences in filecmp6.txt and filecmp8.txt at line %d"
                % lineno)

    def test_file_compare2(self):
        # Test that large file comparison works
        flag = pyutilib.misc.compare_large_file(currdir + "filecmp1.txt",
                                                currdir + "filecmp1.txt")
        if flag:
            self.fail("test_file_compare2 - found differences in filecmp1.txt")
        flag = pyutilib.misc.compare_large_file(currdir + "filecmp1.txt",
                                                currdir + "filecmp2.txt")
        if flag:
            self.fail(
                "test_file_compare2 - found differences between filecmp1.txt filecmp2.txt")
        flag = pyutilib.misc.compare_large_file(
            currdir + "filecmp2.txt", currdir + "filecmp3.txt", bufSize=7)
        if not flag:
            self.fail(
                "test_file_compare2 - found differences between filecmp1.txt filecmp2.txt")
        flag = pyutilib.misc.compare_large_file(currdir + "filecmp1.txt",
                                                currdir + "filecmp3.txt")
        if not flag:
            self.fail("test_file_compare2 - expected difference")
        flag = pyutilib.misc.compare_large_file(currdir + "filecmp1.txt",
                                                currdir + "filecmp4.txt")
        if not flag:
            self.fail("test_file_compare2 - expected difference")
        try:
            flag = pyutilib.misc.compare_large_file(currdir + "foo.txt",
                                                    currdir + "bar.txt")
            self.fail("test_file_compare2 - should have failed to find foo.txt")
        except IOError:
            pass
        try:
            flag = pyutilib.misc.compare_large_file(currdir + "filecmp1.txt",
                                                    currdir + "bar.txt")
            self.fail("test_file_compare1 - should have failed to find bar.txt")
        except IOError:
            pass

    def test_remove_chars(self):
        # Test the remove_chars_in_list works
        a = pyutilib.misc.comparison.remove_chars_in_list("", "")
        self.assertEqual(a, "")
        a = pyutilib.misc.comparison.remove_chars_in_list("abcde", "")
        self.assertEqual(a, "abcde")
        a = pyutilib.misc.comparison.remove_chars_in_list("abcde", "ace")
        self.assertEqual(a, "bd")

    def test_get_desired_chars_from_file(self):
        # Test that get_desired_chars_from_file works
        INPUT = open(currdir + "filecmp5.txt", "r")
        a = pyutilib.misc.comparison.get_desired_chars_from_file(INPUT, 3,
                                                                 "b,d")
        self.assertEqual(a, "ace")
        INPUT.close()
        INPUT = open(currdir + "filecmp5.txt", "r")
        a = pyutilib.misc.comparison.get_desired_chars_from_file(INPUT, 100)
        self.assertEqual(a, "abcde\nfghij\n")
        INPUT.close()

    def test_sort_index1(self):
        # Test that sort_index returns the correct value for a sorted array
        ans = pyutilib.misc.sort_index(range(0, 10))
        self.assertEqual(ans, list(range(0, 10)))

    def test_sort_index2(self):
        # Test that sort_index returns an array that can be used to sort the data
        data = [4, 2, 6, 8, 1, 9, 3, 10, 7, 5]
        ans = pyutilib.misc.sort_index(data)
        sorted = []
        for i in range(0, len(data)):
            sorted.append(data[ans[i]])
        data.sort()
        self.assertEqual(data, sorted)

    def test_create_hardlink(self):
        orig = currdir + "import1.txt"
        link = currdir + "import1.txt.hardlink"

        try:
            os.remove(link)
        except OSError:
            pass
        self.assertTrue(os.path.exists(orig))
        self.assertTrue(not os.path.exists(link))
        pyutilib.misc.create_hardlink(orig, link)
        self.assertTrue(os.path.exists(link))
        self.assertTrue(os.path.isfile(link))
        os.remove(link)


if __name__ == "__main__":
    unittest.main()
