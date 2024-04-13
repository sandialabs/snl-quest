#
# Unit Tests for util/method
#
#

import pyutilib.th as unittest
import pyutilib.misc


class MethodDebug(unittest.TestCase):

    def test_add_method(self):
        # Verify that we can add a method to a class
        class A(object):

            def __init__(self):
                pass

        def foo(self, x):
            return (x,)

        a = A()
        pyutilib.misc.add_method(a, foo)
        self.assertEqual(a.foo("a"), ("a",))
        pyutilib.misc.add_method(a, foo, "bar")
        self.assertEqual(a.bar("b"), ("b",))

    def test_add_method_by_name(self):
        # Verify that we can add a method to a class
        class A(object):

            def __init__(self):
                pass

        def foo(self, x):
            return (x,)

        a = A()
        pyutilib.misc.add_method_by_name(a, "foo", locals=locals())
        self.assertEqual(a.foo("a"), ("a",))
        pyutilib.misc.add_method_by_name(a, "foo", "bar", locals=locals())
        self.assertEqual(a.bar("b"), ("b",))


if __name__ == "__main__":
    unittest.main()
