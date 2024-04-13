import os
import sys
from os.path import abspath, dirname
currdir = dirname(abspath(__file__)) + os.sep

import pyutilib.th as unittest
import pyutilib.workflow
import pyutilib.workflow.globals


class DummyResource(pyutilib.workflow.Resource):

    def __init__(self, name=None):
        pyutilib.workflow.Resource.__init__(self)

    def available(self):
        return False


class TaskA(pyutilib.workflow.Task):

    def __init__(self, *args, **kwds):
        pyutilib.workflow.Task.__init__(self, *args, **kwds)
        self.inputs.declare('x')
        self.inputs.declare('y')
        self.outputs.declare('z')

    def execute(self):
        self.z = self.x + self.y


class TaskAA1(pyutilib.workflow.Task):

    def __init__(self, *args, **kwds):
        pyutilib.workflow.Task.__init__(self, *args, **kwds)
        self.inputs.declare('x', action='append')
        self.outputs.declare('z')

    def execute(self):
        self.z = sum(self.x)


class TaskAA2(pyutilib.workflow.Task):

    def __init__(self, *args, **kwds):
        pyutilib.workflow.Task.__init__(self, *args, **kwds)
        self.inputs.declare('x', action='map')
        self.outputs.declare('z')

    def execute(self):
        self.z = sum(self.x.keys())


class TaskAA3(pyutilib.workflow.Task):

    def __init__(self, *args, **kwds):
        pyutilib.workflow.Task.__init__(self, *args, **kwds)
        self.inputs.declare('x', action='map_any')
        self.outputs.declare('z')

    def execute(self):
        self.z = sum(self.x.keys())


class TaskB(pyutilib.workflow.Task):

    def __init__(self, *args, **kwds):
        pyutilib.workflow.Task.__init__(self, *args, **kwds)
        self.inputs.declare('a')
        self.inputs.declare('i')
        self.outputs.declare('b')

    def execute(self):
        self.b = 100 * self.i + 2 * self.a


class TaskAAA(pyutilib.workflow.Task):

    def __init__(self, *args, **kwds):
        pyutilib.workflow.Task.__init__(self, *args, **kwds)
        self.inputs.declare('a', optional=True)
        self.outputs.declare('a', self.inputs.a)

    def execute(self):
        pass


class TaskBB(TaskB):

    def __init__(self, *args, **kwds):
        TaskB.__init__(self, *args, **kwds)

    def _create_parser(self, parser=None):
        pyutilib.workflow.Task._create_parser(self, parser)
        self.add_argument("--a", dest="a", type=int)
        self.add_argument("--i", dest="i", type=int)


class TaskC(pyutilib.workflow.Task):

    def __init__(self, *args, **kwds):
        pyutilib.workflow.Task.__init__(self, *args, **kwds)
        self.inputs.declare('i')
        self.outputs.declare('o')

    def execute(self):
        self.o = 10 * self.i


class TaskCC(TaskC):

    def __init__(self, *args, **kwds):
        TaskC.__init__(self, *args, **kwds)

    def _create_parser(self, parser=None):
        pyutilib.workflow.Task._create_parser(self, parser)
        self.add_argument("--i", dest="i", type=int)


class TaskD(pyutilib.workflow.Task):

    def __init__(self, *args, **kwds):
        pyutilib.workflow.Task.__init__(self, *args, **kwds)
        self.inputs.declare('i')
        self.outputs.declare('o')
        self.outputs.declare('z')

    def execute(self):
        self.o = 10 * self.i
        self.z = -999


class TaskE(pyutilib.workflow.Task):

    def __init__(self, *args, **kwds):
        pyutilib.workflow.Task.__init__(self, *args, **kwds)
        self.inputs.declare('I')
        self.outputs.declare('O')

    def execute(self):
        self.O = self.I


class Test(unittest.TestCase):

    def test1(self):
        pyutilib.workflow.globals.reset_id_counter()
        # Define tasks
        A = TaskA()
        B = TaskB()
        C = TaskC()
        # Establish connections
        A.inputs.x = B.outputs.b
        A.inputs.y = C.outputs.o
        # Create workflow
        w = pyutilib.workflow.Workflow()
        w.add(A)
        w.add(
            A)  # This is redundant, but it double-checks the logic for adding tasks
        #
        # Print workflow
        #
        ##print "..."
        self.assertEqual(str(w),\
"""Workflow Task4:
Task5 prev: [] next: [2, 3] resources: []
Task2 prev: [5] next: [1] resources: []
Task3 prev: [5] next: [1] resources: []
Task1 prev: [2, 3] next: [6] resources: []
Task6 prev: [1] next: [] resources: []""")
        self.assertEqual(w(i=3, a=2), {'z': 334})

    def test1c(self):
        pyutilib.workflow.globals.reset_id_counter()
        # Define tasks
        A = TaskA()
        E1 = TaskE()
        E2 = TaskE()
        C = TaskC()
        # Establish connections
        A.inputs.x = E1.outputs.O
        A.inputs.y = E2.outputs.O
        E1.inputs.I = C.outputs.o
        E2.inputs.I = C.outputs.o
        # Create workflow
        w = pyutilib.workflow.Workflow()
        w.add(A)
        #
        # Print workflow
        #
        ##print "..."
        self.assertEqual(str(w),\
"""Workflow Task5:
Task6 prev: [] next: [4] resources: []
Task4 prev: [6] next: [2, 3] resources: []
Task2 prev: [4] next: [1] resources: []
Task3 prev: [4] next: [1] resources: []
Task1 prev: [2, 3] next: [7] resources: []
Task7 prev: [1] next: [] resources: []""")
        self.assertEqual(w(i=3), {'z': 60})

    def test1b(self):
        pyutilib.workflow.globals.reset_id_counter()
        # Define tasks
        A = TaskA()
        B = TaskB()
        C = TaskC()
        # Establish connections
        A.inputs.x = B.outputs.b
        A.inputs.y = C.outputs.o
        # Create workflow
        w = pyutilib.workflow.Workflow()
        w.add(A, loadall=False)
        self.assertEqual(
            str(w), "Workflow Task4:\nTask5 prev: [] next: [] resources: []")

    def test1a(self):
        pyutilib.workflow.globals.reset_id_counter()
        # Create workflow
        w = pyutilib.workflow.Workflow()
        self.assertEqual(
            str(w), "Workflow Task1:\nTask2 prev: [] next: [] resources: []")
        w.add(pyutilib.workflow.task.NoTask)
        self.assertEqual(
            str(w), "Workflow Task1:\nTask2 prev: [] next: [] resources: []")

    @unittest.skipIf(sys.version_info >= (3, 0), "There is a slight (space) formatting differences in different Python version... Skipping test.") # yapf: disable
    def test2(self):
        # Do we really want to be testing pformat output?  I think we might
        # actually want to override __cmp__ in the workflow.Task code and instead
        # use that.
        pyutilib.workflow.globals.reset_id_counter()
        A = TaskA(name="A")
        B = TaskB()
        A.inputs.x = B.outputs.b
        base = """{ 'A_TYPE': 'Task',
  'Id': 1,
  'InputControls': { 'A_TYPE': 'Port',
                     'Mode': 'inputs',
                     'Name': 'A-input-controls',
                     'Owner': 'A prev: [2] next: [] resources: []'},
  'Inputs': { 'A_TYPE': 'Port',
              'Mode': 'inputs',
              'Name': 'A-inputs',
              'Owner': 'A prev: [2] next: [] resources: []',
              'x': { 'A_TYPE': 'Port',
                     'Action': 'store',
                     'Connections': { 'Inputs': [ 'DirectConnector: from=(2) to=(1) False'],
                                      'Outputs': []},
                     'Constant': 'False',
                     'Name': 'x',
                     'Optional': 'False',
                     'Ready': 'False',
                     'Task': '1',
                     'Value': 'None'},
              'y': { 'A_TYPE': 'Port',
                     'Action': 'store',
                     'Connections': { 'Inputs': [], 'Outputs': []},
                     'Constant': 'False',
                     'Name': 'y',
                     'Optional': 'False',
                     'Ready': 'False',
                     'Task': '1',
                     'Value': 'None'}},
  'Name': 'A',
  'OutputControls': { 'A_TYPE': 'Port',
                      'Mode': 'outputs',
                      'Name': 'A-output-controls',
                      'Owner': 'A prev: [2] next: [] resources: []'},
  'Outputs': { 'A_TYPE': 'Port',
               'Mode': 'outputs',
               'Name': 'A-outputs',
               'Owner': 'A prev: [2] next: [] resources: []',
               'z': { 'A_TYPE': 'Port',
                      'Action': 'store',
                      'Connections': { 'Inputs': [], 'Outputs': []},
                      'Constant': 'False',
                      'Name': 'z',
                      'Optional': 'False',
                      'Ready': 'False',
                      'Task': '1',
                      'Value': 'None'}}}"""
        self.assertEqual(str(A), base)

    def test3(self):
        # Do we really want to be testing pformat output?  I think we might
        # actually want to override __cmp__ in the workflow.Task code and instead
        # use that.
        pyutilib.workflow.globals.reset_id_counter()
        A = TaskA()
        B = TaskB()
        A.inputs.x = B.outputs.b
        OUTPUT = open(currdir + 'test3.out', 'w')
        OUTPUT.write(str(A.inputs) + '\n')
        OUTPUT.write(str(A.outputs) + '\n')
        OUTPUT.close()
        self.assertFileEqualsBaseline(currdir + 'test3.out',
                                      currdir + 'test3.txt')

    def test4(self):
        # Do we really want to be testing pformat output?  I think we might
        # actually want to override __cmp__ in the workflow.Task code and instead
        # use that.
        pyutilib.workflow.globals.reset_id_counter()
        A = TaskA()
        A.inputs['x'] = 2
        self.assertEqual(A.inputs['x'].get_value(), 2)
        OUTPUT = open(currdir + 'test4.out', 'w')
        OUTPUT.write(str(A) + '\n')
        OUTPUT.close()
        self.assertFileEqualsBaseline(currdir + 'test4.out',
                                      currdir + 'test4.txt')

    def test5(self):
        pyutilib.workflow.globals.reset_id_counter()
        # Define tasks
        A = TaskA()
        B = TaskB()
        C = TaskC()
        # Establish connections
        A.inputs.x = B.outputs.b
        A.inputs.y = C.outputs.o
        # Create workflow
        w = pyutilib.workflow.Workflow()
        w.add(A)
        w.set_options(['--i=3', '--a=2'])
        try:
            w()
            self.fail("Expected ValueError because the inputs are not defined")
        except ValueError:
            pass

    def test5a(self):
        pyutilib.workflow.globals.reset_id_counter()
        # Define tasks
        A = TaskA()
        B = TaskBB()
        C = TaskCC()
        # Establish connections
        A.inputs.x = B.outputs.b
        A.inputs.y = C.outputs.o
        # Create workflow
        w = pyutilib.workflow.Workflow()
        w.add(A)
        w.set_options(['--i=3', '--a=2'])
        self.assertEqual(w(), {'z': 334})
        # This doesn't work, since we can't merge options that aren't
        # in groups.  The soln is to move to argparse, but I'll save that for later
        #w.print_help()

    def test5b(self):
        # Do we really want to be testing pformat output?  I think we might
        # actually want to override __cmp__ in the workflow.Task code and instead
        # use that.
        self.skipTest("This test is not portable to different Python version")

        pyutilib.workflow.globals.reset_id_counter()
        # Define tasks
        A = TaskA()
        B = TaskBB()
        C = TaskCC()
        # Establish connections
        A.inputs.x = B.outputs.b
        A.inputs.y = C.outputs.o
        # Create workflow
        w = pyutilib.workflow.Workflow()
        w.add(A)
        w.set_options(['--i=3', '--a=2'])
        w()
        OUTPUT = open(currdir + 'test5b.out', 'w')
        OUTPUT.write(str(w) + '\n')
        OUTPUT.close()
        self.assertFileEqualsBaseline(currdir + 'test5b.out',
                                      currdir + 'test5b.txt')

    def test_error1(self):
        pyutilib.workflow.globals.reset_id_counter()
        A = TaskA()
        try:
            A.inputs['inputs'] = 2
            self.fail(
                "Expected ValueError because we're using the reserved 'inputs' attribute name")
        except TypeError:
            pass

    def test_error2(self):
        pyutilib.workflow.globals.reset_id_counter()
        A = TaskA()
        try:
            print(A.inputs._foo)
            self.fail("Should have generated error for unknown attribute _foo")
        except AttributeError:
            pass

    def test_error3(self):
        pyutilib.workflow.globals.reset_id_counter()
        # Define tasks
        A = TaskA()
        B = TaskB()
        D = TaskD()
        # Establish connections
        A.inputs.x = B.outputs.b
        A.inputs.y = D.outputs.o
        # Create workflow
        w = pyutilib.workflow.Workflow()
        try:
            w.add(A)
            self.fail(
                "Expected ValueError because there are multiple outputs with the same name")
        except ValueError:
            pass

    def test_error4(self):
        pyutilib.workflow.globals.reset_id_counter()
        # Define tasks
        A = TaskAA1()
        B = TaskAAA()
        C = TaskAAA()
        # Establish connections
        A.inputs.x = B.outputs.a
        A.inputs.x = C.outputs.a
        # Create workflow
        w = pyutilib.workflow.Workflow()
        w.add(A)
        try:
            w()
            self.fail("Expected ValueError because inputs are None")
        except ValueError:
            pass

    def test_error5(self):
        pyutilib.workflow.globals.reset_id_counter()
        # Define tasks
        A = TaskAA2()
        B = TaskAAA()
        C = TaskAAA()
        # Establish connections
        A.inputs.x = B.outputs.a
        A.inputs.x = C.outputs.a
        # Create workflow
        w = pyutilib.workflow.Workflow()
        w.add(A)
        try:
            w()
            self.fail("Expected ValueError because inputs are None")
        except ValueError:
            pass

    def test_error6(self):
        driver = pyutilib.workflow.TaskDriver()
        try:
            driver.register_task('_foo_')
            self.fail("Expected ValueError because '_foo_' task is not defined")
        except ValueError:
            pass

    def test_error7(self):
        A1 = TaskA()
        A2 = TaskA()
        A3 = TaskA()
        A3.inputs.x = A1.outputs.z
        try:
            A3.inputs.x = A2.outputs.z
            self.fail(
                "Expected ValueError because we're connecting two outputs to an input with action 'store'")
        except:
            pass

    def test_error8(self):
        A1 = TaskAA1()
        A2 = TaskAA1()
        A2.inputs.x = A1.outputs.z
        try:
            A2.inputs.x.validate()
            self.fail(
                "Expected ValueError because the 'x' input does not have a nontrivial value")
        except:
            pass
        self.assertFalse(A2.ready())

    def test_error9(self):
        A1 = TaskAA2()
        A2 = TaskAA2()
        A2.inputs.x = A1.outputs.z
        try:
            A2.inputs.x.validate()
            self.fail(
                "Expected ValueError because the 'x' input does not have a nontrivial value")
        except:
            pass
        self.assertFalse(A2.ready())

    def test_error10(self):
        A1 = TaskAA3()
        A2 = TaskAA3()
        A3 = TaskAA3()
        A2.inputs.x = A1.outputs.z
        A2.inputs.x = A3.outputs.z
        try:
            A2.inputs.x.validate()
            self.fail(
                "Expected ValueError because the 'x' input does not have a nontrivial value")
        except:
            pass
        self.assertFalse(A2.ready())
        A1.outputs.z = 1
        self.assertTrue(A2.ready())

    def test_error11(self):
        A1 = TaskA()
        A1.add_resource(DummyResource())
        try:
            A1()
            self.fail("Expected IOError because resource is busy.")
        except IOError:
            pass

    def test_driver1(self):
        driver = pyutilib.workflow.TaskDriver()
        driver.register_task('workflow.selection')
        try:
            driver.parse_args(['-h'])
            self.fail("Expected system exit because of bad options")
        except SystemExit:
            pass
        try:
            driver.parse_args(['foo'])
            self.fail("Expected error because bad subcommand is specified")
        except SystemExit:
            pass
        try:
            driver.parse_args(['workflow.selection'])
            self.fail("Expected error because task input is not defined")
        except ValueError:
            pass

    def test_driver2(self):
        driver = pyutilib.workflow.TaskDriver()
        driver.register_task('workflow.selection')
        try:
            # Set sys.argv and then parse arguments
            sys.argv = ['foo', '-h']
            driver.parse_args()
            self.fail("Expected system exit because of bad options")
        except SystemExit:
            pass


if __name__ == "__main__":
    unittest.main()
