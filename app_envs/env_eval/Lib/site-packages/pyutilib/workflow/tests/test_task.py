import logging
import os
from os.path import abspath, dirname
currdir = dirname(abspath(__file__)) + os.sep

import pyutilib.th as unittest
import pyutilib.misc
from pyutilib.workflow import *

try:
    import json
    json_available = True
except:
    json_available = False


class Handler(logging.StreamHandler):

    def emit(self, record):
        raise RuntimeError(str(record))


handler = Handler()
logger = logging.getLogger('pyutilib.workflow')


class TestData(unittest.TestCase):

    def test1(self):
        # Print FunctorAPIData string
        data = FunctorAPIData()
        data.a = 1
        data.b = [1, 2]
        data.c = FunctorAPIData()
        data.c.x = 1
        data.c.y = 2
        data.aa = 'here is more'
        data.clean()
        pyutilib.misc.setup_redirect(currdir + 'test1.out')
        print(data)
        pyutilib.misc.reset_redirect()
        self.assertFileEqualsBaseline(currdir + 'test1.out',
                                      currdir + 'test1.txt')
        self.assertEquals(len(data._dirty_), 0)

    @unittest.skipIf(not json_available, "JSON not available")
    def test2(self):
        # Print FunctorAPIData representation
        data = FunctorAPIData()
        data.a = 1
        data.b = [1, 2]
        data.c = FunctorAPIData()
        data.c.x = 1
        data.c.y = 2
        data['aa'] = 'here is more'
        data.clean()
        FILE = open(currdir + 'test2.out', 'w')
        json.dump(data, FILE)
        FILE.close()
        self.assertMatchesJsonBaseline(currdir + 'test2.out',
                                       currdir + 'test2.txt')
        self.assertEquals(len(data._dirty_), 0)

    @unittest.expectedFailure
    def test_err1(self):
        # Unknown attribute
        data = FunctorAPIData()
        data._x

    @unittest.expectedFailure
    def test_err2(self):
        # Undeclared attribute
        data = FunctorAPIData()
        data.declare('a')
        data.x

    @unittest.expectedFailure
    def test_err3(self):
        # Undeclared attribute
        data = FunctorAPIData()
        data.declare(['a'])
        data.x


class TestAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Disable the pyutilib.workflow logging handler
        if len(logger.handlers) > 0:
            cls._handler = logger.handlers[0]
            logger.removeHandler(cls._handler)
        else:
            cls._handler = None
        logger.addHandler(handler)

    @classmethod
    def tearDownClass(cls):
        # Re-enable the pyutilib.workflow logging handler
        logger.removeHandler(handler)
        if not cls._handler is None:
            logger.addHandler(cls._handler)

    def test1(self):
        # Simple test: no keyword arguments or return values
        @functor_api
        def test1(data):
            # Required:
            #     data: input data
            data.a = 2
            data.b[0] = 2
        #
        options = FunctorAPIData()
        options.a = 1
        options.b = [1, 2]
        retval = test1(options)
        self.assertEquals(retval.data.a, 2)
        self.assertEquals(retval.data.b, [2, 2])
        retval = test1(data=options)
        self.assertEquals(retval.data.a, 2)
        self.assertEquals(retval.data.b, [2, 2])
        #
        self.assertTrue('test1' in FunctorAPIFactory.services())

    def test1a(self):
        """Simple test: no keyword arguments or return values"""

        @functor_api
        def test1a(data):
            """
            Required:
                data: input data
            Return:
                data: output data
            """
            data.a = 2
            data.b[0] = 2
        #
        options = FunctorAPIData()
        options.a = 1
        options.b = [1, 2]
        retval = test1a(options)
        self.assertEquals(retval.data.a, 2)
        self.assertEquals(retval.data.b, [2, 2])
        retval = test1a(data=options)
        self.assertEquals(retval.data.a, 2)
        self.assertEquals(retval.data.b, [2, 2])

    def test1b(self):
        """Simple test: data keyword argument, no return values"""

        @functor_api
        def test1b(data=None):
            data.a = 2
            data.b[0] = 2
        #
        options = FunctorAPIData()
        options.a = 1
        options.b = [1, 2]
        retval = test1b(options)
        self.assertEquals(retval.data.a, 2)
        self.assertEquals(retval.data.b, [2, 2])
        retval = test1b(data=options)
        self.assertEquals(retval.data.a, 2)
        self.assertEquals(retval.data.b, [2, 2])

    def test2(self):
        """Simple test: no keyword arguments, returning data"""

        @functor_api
        def test2(data):
            data.a = 2
            data.b[0] = 2
            return data
        #
        options = FunctorAPIData()
        options.a = 1
        options.b = [1, 2]
        retval = test2(options)
        self.assertEquals(retval.data.a, 2)
        self.assertEquals(retval.data.b, [2, 2])
        retval = test2(data=options)
        self.assertEquals(retval.data.a, 2)
        self.assertEquals(retval.data.b, [2, 2])

    def test2a(self):
        """Simple test: no keyword arguments, returning data"""

        @functor_api
        def test2a(data):
            """
            Required:
                data: input data
            Return:
                data: output data
            """
            data.a = 2
            data.b[0] = 2
            return data
        #
        options = FunctorAPIData()
        options.a = 1
        options.b = [1, 2]
        retval = test2a(options)
        self.assertEquals(retval.data.a, 2)
        self.assertEquals(retval.data.b, [2, 2])
        retval = test2a(data=options)
        self.assertEquals(retval.data.a, 2)
        self.assertEquals(retval.data.b, [2, 2])

    def test3(self):
        """Simple test: keyword arguments, no return values"""

        @functor_api
        def test3(data, x=1, y=2):
            """
            Required:
                data: input data
                x: integer
            Optional:
                y: integer
            """
            data.a = y
            data.b[0] = x
        #
        options = FunctorAPIData()
        options.a = 1
        options.b = [1, 2]
        retval = test3(options, x=2)
        self.assertEquals(retval.data.a, 2)
        self.assertEquals(retval.data.b, [2, 2])
        retval = test3(data=options, x=2)
        self.assertEquals(retval.data.a, 2)
        self.assertEquals(retval.data.b, [2, 2])

    def test3a(self):
        """Simple test: keyword arguments, no return values"""

        @functor_api
        def test3a(x=1, y=2, data=None):
            """
            Required:
                data: input data
                x: integer
            Optional:
                y: integer
            """
            data.a = y
            data.b[0] = x
        #
        options = FunctorAPIData()
        options.a = 1
        options.b = [1, 2]
        retval = test3a(options, x=2)
        self.assertEquals(retval.data.a, 2)
        self.assertEquals(retval.data.b, [2, 2])
        retval = test3a(data=options, x=2)
        self.assertEquals(retval.data.a, 2)
        self.assertEquals(retval.data.b, [2, 2])

    def test4(self):
        """Simple test: keyword arguments, simple return value"""

        @functor_api
        def test4(data, x=1, y=2):
            """
            Required:
                data: input data
                x: integer
            Optional:
                y: integer
            Return:
                data: output data
            """
            data.a = y
            data.b[0] = x
            return data
        #
        options = FunctorAPIData()
        options.a = 1
        options.b = [1, 2]
        retval = test4(options, x=2)
        self.assertEquals(retval.data.a, 2)
        self.assertEquals(retval.data.b, [2, 2])
        retval = test4(data=options, x=2)
        self.assertEquals(retval.data.a, 2)
        self.assertEquals(retval.data.b, [2, 2])

    def test5(self):
        """Simple test: keyword arguments, non-data return values"""

        @functor_api(outputs=('z'))
        def test5(data, x=1, y=2):
            """
            Required:
                data: input data
                x: integer
            Optional:
                y: integer
            Return:
                data: output data
                z: integer
            """
            data.a = y
            data.b[0] = x
            return FunctorAPIData(z=x)
        #
        options = FunctorAPIData()
        options.a = 1
        options.b = [1, 2]
        retval = test5(options, x=2)
        self.assertEquals(retval.data.a, 2)
        self.assertEquals(retval.data.b, [2, 2])
        retval = test5(data=options, x=2)
        self.assertEquals(retval.data.a, 2)
        self.assertEquals(retval.data.b, [2, 2])
        self.assertEquals(retval.z, 2)

    def test6(self):
        """Simple test: keyword arguments, non-data return values with data"""

        @functor_api(outputs=('z'))
        def test6(data, x=1, y=2):
            """
            Required:
                data: input data
                x: integer
            Optional:
                y: integer
            Return:
                data: output data
                z: integer
            """
            data.a = y
            data.b[0] = x
            return FunctorAPIData(data=data, z=x)
        #
        options = FunctorAPIData()
        options.a = 1
        options.b = [1, 2]
        retval = test6(options, x=2)
        self.assertEquals(retval.data.a, 2)
        self.assertEquals(retval.data.b, [2, 2])
        retval = test6(data=options, x=2)
        self.assertEquals(retval.data.a, 2)
        self.assertEquals(retval.data.b, [2, 2])
        self.assertEquals(retval.z, 2)

    def test5a(self):
        """Outputs specified in docstring: keyword arguments, non-data return values"""

        @functor_api
        def test5a(data, x=1, y=2):
            """
            Required:
                data: input data
                x: integer
            Optional:
                y: integer
            Return:
                data: output data
                z: integer
            """
            data.a = y
            data.b[0] = x
            return FunctorAPIData(z=x)
        #
        options = FunctorAPIData()
        options.a = 1
        options.b = [1, 2]
        retval = test5a(options, x=2)
        self.assertEquals(retval.data.a, 2)
        self.assertEquals(retval.data.b, [2, 2])
        retval = test5a(data=options, x=2)
        self.assertEquals(retval.data.a, 2)
        self.assertEquals(retval.data.b, [2, 2])
        self.assertEquals(retval.z, 2)

    def test6a(self):
        """Outputs specified in docstring: keyword arguments, non-data return values with data"""

        @functor_api
        def test6a(data, x=1, y=2):
            """
            Required:
                data: input data
                x: integer
            Optional:
                y: integer
            Return:
                data: output data
                z: integer
            """
            data.a = y
            data.b[0] = x
            return FunctorAPIData(data=data, z=x)
        #
        options = FunctorAPIData()
        options.a = 1
        options.b = [1, 2]
        retval = test6a(options, x=2)
        self.assertEquals(retval.data.a, 2)
        self.assertEquals(retval.data.b, [2, 2])
        retval = test6a(data=options, x=2)
        self.assertEquals(retval.data.a, 2)
        self.assertEquals(retval.data.b, [2, 2])
        self.assertEquals(retval.z, 2)

    def test7a(self):
        """Test with dict data"""

        @functor_api
        def test7a(data, x=1, y=2):
            """
            Required:
                data: input data
                x: integer
            Optional:
                y: integer
            """
            data.a = y
            data.b[0] = x
        #
        options = {}
        options['a'] = 1
        options['b'] = [1, 2]
        retval = test7a(options, x=2)
        self.assertEquals(retval.data.a, 2)
        self.assertEquals(retval.data.b, [2, 2])
        retval = test7a(data=options, x=2)
        self.assertEquals(retval.data.a, 2)
        self.assertEquals(retval.data.b, [2, 2])

    def test7b(self):
        """Test with dict data and return a dictionary"""

        @functor_api
        def test7b(data, x=1, y=2):
            """
            Required:
                data: input data
                x: integer
            Optional:
                y: integer
            """
            data.a = y
            data.b[0] = x
            return {'data': data}
        #
        options = {}
        options['a'] = 1
        options['b'] = [1, 2]
        retval = test7b(options, x=2)
        self.assertEquals(retval.data.a, 2)
        self.assertEquals(retval.data.b, [2, 2])
        retval = test7b(data=options, x=2)
        self.assertEquals(retval.data.a, 2)
        self.assertEquals(retval.data.b, [2, 2])

    def test7c(self):
        """Test with dict data and return a dictionary"""

        @functor_api
        def test7c(data, x=1, y=2):
            """
            Required:
                data: input data
                x: integer
            Optional:
                y: integer
            Return:
                z: integer
            """
            data.a = y
            data.b[0] = x
            return {'data': data, 'z': x}
        #
        options = {}
        options['a'] = 1
        options['b'] = [1, 2]
        retval = test7c(options, x=2)
        self.assertEquals(retval.data.a, 2)
        self.assertEquals(retval.data.b, [2, 2])
        retval = test7c(data=options, x=2)
        self.assertEquals(retval.data.a, 2)
        self.assertEquals(retval.data.b, [2, 2])
        self.assertEquals(retval.z, 2)

    def test8(self):
        """Simple test with required nested data"""

        @functor_api
        def test8(data):
            """
            Required:
                data: input data
                data.foo.bar:
            """
            data.foo.foo = 3
            #data.a = 2
            #data.b[0] = 2
        #

        options = FunctorAPIData()
        options.foo = FunctorAPIData()
        options.foo.bar = 1
        options.a = 1
        options.b = [1, 2]
        retval = test8(options)
        self.assertEquals(retval.data.a, 1)
        self.assertEquals(retval.data.b, [1, 2])
        self.assertEquals(retval.data.foo.foo, 3)
        #retval = test8(data=options)
        #self.assertEquals(retval.data.a, 2)
        #self.assertEquals(retval.data.b, [2,2])

    def test9(self):
        """Simple test: no keyword arguments or return values"""

        @functor_api
        def test9(data):
            """
            This is the
            short
            documentation.

            This

            is
  
            the
  
            long documentation.
            Required:
                data: multiline
                      description of 
                      input data object
                data.a: More data
            """
            data.a = 2
            data.b[0] = 2
        #
        options = FunctorAPIData()
        options.a = 1
        options.b = [1, 2]
        retval = test9(options)
        self.assertEquals(retval.data.a, 2)
        self.assertEquals(retval.data.b, [2, 2])
        retval = test9(data=options)
        self.assertEquals(retval.data.a, 2)
        self.assertEquals(retval.data.b, [2, 2])
        #
        self.assertTrue('test1' in FunctorAPIFactory.services())
        self.assertEquals(test9.__short_doc__,
                          'This is the\nshort\ndocumentation.')
        self.assertEquals(test9.__long_doc__,
                          'This\n\nis\n\nthe\n\nlong documentation.')

    @unittest.expectedFailure
    def test10(self):
        """Simple test: no keyword arguments or return values"""

        @functor_api
        def test10(data=None, x=1):
            """
            Required:
                x: 
            Optional:
                data:
            """
            return FunctorAPIData(z=2 * x)
        #
        retval = test10(x=3)
        self.assertEquals(retval.z, 6)

    @unittest.expectedFailure
    def test_err1(self):
        """Expect an error when variable length arguments are supported"""

        @functor_api
        def err1(*args):
            pass

    @unittest.expectedFailure
    def test_err2(self):
        """Expect an error when variable length keyword arguments are supported"""

        @functor_api
        def err2(**kwargs):
            pass

    @unittest.expectedFailure
    def test_err3(self):
        """Expect an error when return value is not None or Options()"""

        @functor_api
        def err3(data):
            return 1

        f(FunctorAPIData())

    @unittest.expectedFailure
    def test_err4(self):
        """Expect an error when no data argument is specified"""

        @functor_api
        def err4(data):
            data.a = 2
            data.b[0] = 2

        test1()

    @unittest.expectedFailure
    def test_err5(self):
        """Expect an error when an unspecified return value is given"""

        @functor_api
        def err5(data):
            return FunctorAPIData(z=None)

        f(FunctorAPIData())

    @unittest.expectedFailure
    def test_err6(self):
        """Expect an error when no data argument is specified"""

        @functor_api
        def err6():
            pass

        f(FunctorAPIData())

    @unittest.expectedFailure
    def test_err7a(self):
        """Argument missing from docstring"""

        @functor_api
        def err7a(data, x=1, y=2):
            """
            Optional:
                y: integer
            """
            pass

    @unittest.expectedFailure
    def test_err7b(self):
        """Argument missing from docstring"""

        @functor_api
        def err7b(data, x=1, y=2):
            """
            Required:
                x: integer
            """
            pass

    @unittest.expectedFailure
    def test_err7c(self):
        """Argument missing from docstring"""

        @functor_api(outputs=('z'))
        def err7c(data, x=1, y=2):
            """
            Required:
                x: integer
            Optional:
                y: integer
            """
            return FunctorAPIData(z=1)

    @unittest.expectedFailure
    def test_err7A(self):
        """Unexpected required argument"""

        @functor_api
        def err7A(data, x=1, y=2):
            """
            Required:
                x: integer
                bad: integer
            Optional:
                y: integer
            """
            pass

    @unittest.expectedFailure
    def test_err7B(self):
        """Argument missing from docstring"""

        @functor_api
        def err7B(data, x=1, y=2):
            """
            Required:
                x: integer
            Optional:
                y: integer
                bad: integer
            """
            pass

    @unittest.expectedFailure
    def test_err7C(self):
        """Argument missing from docstring"""

        @functor_api(outputs=('z'))
        def err7C(data, x=1, y=2):
            """
            Required:
                x: integer
            Optional:
                y: integer
            Return:
                z: integer
                bad: integer
            """
            return FunctorAPIData(z=1)

    @unittest.expectedFailure
    def test_err8a(self):
        """Missing nested value"""

        @functor_api
        def err8a(data):
            """
            Required:
                data.x: integer
            """
            pass

        err8a(FunctorAPIData())

    @unittest.expectedFailure
    def test_err8b(self):
        """Nested value with None value"""

        @functor_api
        def err8b(data):
            """
            Required:
                data.x: integer
            """
            pass

        err8b(FunctorAPIData(data=FunctorAPIData()))

    @unittest.expectedFailure
    def test_err8c(self):
        """Nested value with None value"""

        @functor_api
        def err8c(data):
            """
            Required:
                data.x.y: integer
            """
            pass

        err8c(FunctorAPIData(x={}))

    @unittest.expectedFailure
    def test_err9(self):
        """Redefinied test functions"""

        @functor_api
        def err9(data):
            pass

        @functor_api
        def err9(data):
            pass

    @unittest.expectedFailure
    def test_err10(self):
        """Simple test with required nested data"""

        @functor_api
        def err10(data):
            """
            Required:
                data: input data
                data.foo.bar:
            """
            data.foo.foo = 3
            data.a = 2
        #
        options = FunctorAPIData()
        options.foo = FunctorAPIData()
        options.foo.bar = 1
        options.a = 1
        options.b = [1, 2]
        retval = err10(options)
        self.assertEquals(retval.data.a, 1)
        self.assertEquals(retval.data.b, [1, 2])
        self.assertEquals(retval.data.foo.foo, 3)

    @unittest.expectedFailure
    def test_err10a(self):
        """Expect an error when the same functor is defined twice"""

        @functor_api
        def err10a(data):
            pass

        @functor_api
        def err10a(data):
            pass

    @unittest.expectedFailure
    def test_err10b(self):
        """Expect an error when the same functor is defined twice"""

        @functor_api(namespace='foo')
        def err10b(data):
            pass

        @functor_api(namespace='foo')
        def err10b(data):
            pass

    @unittest.expectedFailure
    def test_err11(self):
        """Expect an error when 'data' is not defined when it is required"""

        @functor_api
        def err11(data=None, x=1):
            """
            Required:
                data: 
                x: 
            """

        err11(x=2)

    @unittest.expectedFailure
    def test_err12(self):
        """Expect an error when multiple data options are provided"""

        @functor_api
        def err12(data):
            pass

        err12({}, {})

    @unittest.expectedFailure
    def test_err13(self):
        """Expect an error when returning something other than None, FunctorAPIData or a dict object"""

        @functor_api
        def err13(data):
            return set()

        err13({})


if __name__ == "__main__":
    unittest.main()
