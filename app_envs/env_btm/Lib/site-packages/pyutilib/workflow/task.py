#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________
"""Definitions for workflow task objects."""

__all__ = ['Task', 'EmptyTask', 'Component', 'Port', 'Ports', 'InputPorts',
           'OutputPorts', 'Connector', 'DirectConnector']

import argparse
import pprint
import weakref
from pyutilib.misc import Options
from pyutilib.workflow import globals


class Task(object):
    """
    A Task object represents a single action in a workflow.
    """

    def __init__(self, id=None, name=None, parser=None):
        """Constructor."""
        if not id is None:
            self.id = id
        else:
            self.id = globals.unique_id()
        if name is None:
            self.name = "Task" + str(self.id)
        else:
            self.name = name
        self.inputs = InputPorts(self)
        self.inputs.set_name(self.name + "-inputs")
        self.outputs = OutputPorts(self)
        self.outputs.set_name(self.name + "-outputs")
        self._resources = {}
        self._predecessors = []
        self._create_parser(parser)
        self.input_controls = InputPorts(self)
        self.input_controls.set_name(self.name + '-input-controls')
        self.output_controls = OutputPorts(self)
        self.output_controls.set_name(self.name + '-output-controls')
        self.debug = False

    def add_resource(self, resource):
        """Add a resource that is required for this task to execute."""
        self._resources[resource.name] = resource

    def resource(self, name):
        """Return the specified resource object."""
        return self._resources[name]

    def next_tasks(self):
        """Return the set of tasks that succeed this task in the workflow."""
        return set(t.to_port.task()
                   for name in self.outputs
                   for t in self.outputs[name].output_connections) | set(
                       t.to_port.task()
                       for name in self.output_controls
                       for t in self.output_controls[name].output_connections)

    def prev_tasks(self):
        """Return the set of tasks that precede this task in the workflow."""
        return set([task
                    for name in self.inputs
                    for task in self.inputs[name].from_tasks()
                    if task.id != NoTask.id]) | set(
                        task for task in self._predecessors) | set(
                            [task
                             for name in self.input_controls
                             for task in self.input_controls[name].from_tasks()
                             if task.id != NoTask.id])

    def next_task_ids(self):
        """Return the set of ids for tasks that succeed this task in the workflow."""
        return set(task.id for task in self.next_tasks())

    def prev_task_ids(self):
        """Return the set of ids for tasks that precede this task in the workflow."""
        return set(task.id for task in self.prev_tasks())

    def execute(self, debug=False):
        """Execute this task."""
        raise ValueError(
            "There is no default execution for an abstract Task object! Task=%s"
            % self._name())  #pragma:nocover

    def busy_resources(self):
        """Return the list of resources that this task is waiting for."""
        return [name for name in self._resources
                if not self._resources[name].available()]

    def ready(self):
        if self.busy():
            return False
        for name in self.inputs:
            #print "XYZ",self.name, name, self.inputs[name].ready(),self.inputs[name]._ready
            #for connection in self.inputs[name].input_connections:
            #print "XYZ",self.name, name,connection.from_port._ready, connection.ready(), len(connection.from_port.input_connections), connection.from_port.task.name
            if not self.inputs[name].ready():
                #print "FALSE - input", name
                #print self.inputs[name]
                return False
        for name in self.input_controls:
            if not self.input_controls[name].ready():
                #print "FALSE - control", name
                return False
        return True

    def busy(self):
        """Return the list of resources that this task is waiting for."""
        return len(self.busy_resources())

    def __call__(self, *options, **kwds):
        """Setup inputs and output parameters and execute this task.

        Copy the inputs into this Task's dictionary, then execute the task, then copy
        the outputs out of the dictionary.
        """
        self._call_init(*options, **kwds)
        self.execute()
        return self._call_fini(*options, **kwds)

    def _call_init(self, *options, **kwds):
        self._call_start()
        busy = self.busy_resources()
        if len(busy) > 0:
            raise IOError("Cannot execute task %s.  Busy resources: %s" %
                          (self.name, str(busy)))
        # Set inputs
        for opt in options:
            self._set_inputs(opt)
        self._set_inputs(kwds)
        #
        for name, res in self._resources.items():
            res.lock()
        for i in self.outputs:
            #print "z",i,getattr(self.outputs,i).get_value()
            setattr(self, i, None)
        for i in self.inputs:
            #print "OIUOX",i,self.inputs[i].get_value(),str(self.inputs[i])
            # TODO: validate that non-optional inputs have a value other than None
            self.inputs[i].compute_value()
            setattr(self, i, self.inputs[i].get_value())

    def _call_fini(self, *options, **kwds):
        for i in self.outputs:
            #print "Z",i,getattr(self.outputs,i).get_value()
            # TODO: validate that non-optional outputs have a value other than None
            self.outputs[i].set_value(getattr(self, i))

        for name, res in self._resources.items():
            res.unlock()
        self._call_finish()
        self.set_ready()
        #
        opt = Options()
        for i in self.outputs:
            setattr(opt, i, getattr(self.outputs, i).get_value())
        return opt

    def set_options(self, args):
        """Use a list of command-line options to initialize this task."""
        [self.options, args] = self._parser.parse_known_args(args)
        tmp = {}
        for action in self._parser._actions:
            try:
                val = getattr(self.options, action.dest)
                tmp[action.dest] = val
            except:
                pass
        self._set_inputs(tmp)

    def _call_start(self):
        """This method is executed when the task is started."""
        pass

    def _call_finish(self):
        """This method is executed when the task is finished."""
        pass

    def _set_inputs(self, options):
        """Set the inputs from a dictionary."""
        for key in options:
            self.inputs[key].set_value(options[key])

    def set_arguments(self, parser=None):
        if parser is None:
            return
        for arg in self._parser_arg:
            args = arg[0]
            kwargs = arg[1]
            self._parser.add_argument(*args, **kwargs)

    def add_argument(self, *args, **kwargs):
        self._parser_arg.append([args, kwargs])
        self._parser.add_argument(*args, **kwargs)

    def _create_parser(self, parser=None):
        """Create the OptionParser object and populate it with option groups."""
        if parser is None:
            self._parser = argparse.ArgumentParser()
        else:
            self._parser = parser
        self._parser_arg = []
        self._parser_group = {}
        self._create_parser_groups()
        for key in self._parser_group:
            self._parser.add_argument_group(self._parser_group[key])

    def _create_parser_groups(self):
        """This method is called by the _create_parser method to setup the
        parser groups that are registered for this task."""

    def _repn_(self):
        tmp = {}
        tmp['A_TYPE'] = 'Task'
        tmp['Name'] = self.name
        tmp['Id'] = self.id
        tmp['Inputs'] = self.inputs._repn_()
        tmp['Outputs'] = self.outputs._repn_()
        tmp['InputControls'] = self.input_controls._repn_()
        tmp['OutputControls'] = self.output_controls._repn_()
        return tmp

    #def __repr__(self):
    #"""Return a string representation for this task."""
    #return pprint.pformat(self._repn_(), 2)

    def __str__(self):
        """Return a string representation for this task."""
        return pprint.pformat(self._repn_(), 2)

    def _name(self):
        return "%s prev: %s next: %s resources: %s" % (
            str(self.name), str(sorted(list(self.prev_task_ids()))),
            str(sorted(list(self.next_task_ids()))),
            str(sorted(self._resources.keys())))

    def reset(self):
        #print "RESETING "+self.name
        for i in self.outputs:
            self.outputs[i].reset()
        for i in self.output_controls:
            self.output_controls[i].reset()

    def set_ready(self):
        for i in self.outputs:
            self.outputs[i].set_ready()


class Component(Task):
    """
    Alias for the Task class.
    """

    def __init__(self, *args, **kwds):
        """Constructor."""
        Task.__init__(self, *args, **kwds)  #pragma:nocover


class EmptyTask(Task):

    def __call__(self, *args, **kwds):
        """Empty task execution."""

    #
    # An empty task maintains no option parser
    #

    def set_options(self, args):
        """Empty task initialization."""

    def set_arguments(self, *args, **kwds):  #pragma:nocover
        raise NotImplementedError  #pragma:nocover

    def add_argument(self, *args, **kwds):  #pragma:nocover
        raise NotImplementedError  #pragma:nocover

    def _create_parser(self, *args, **kwds):
        self._parser = None
        self._parser_arg = []
        self._parser_group = {}

    def _create_parser_groups(self):  #pragma:nocover
        raise NotImplementedError  #pragma:nocover


def define_connection(cls, from_port, to_port):
    """Define a connection by constructing the specified class."""
    # TODO: Generate a warning if required input is connect to an optional output

    #
    # Raise an exception if the port action is store and there already exists a connection.
    #
    if to_port.action == 'store' and len(to_port.input_connections) == 1:
        raise ValueError(
            "Cannot connect to task %s port %s from task %s port %s. This port is already connected from task %s port %s"
            %
            (to_port.task().name, to_port.name, from_port.task().name,
             from_port.name, to_port.input_connections[0].from_port.task().name,
             to_port.input_connections[0].from_port.name))
    #
    #print 'connecting',from_port.task.id, to_port.task.id
    connector = cls(from_port=from_port, to_port=to_port)
    to_port.input_connections.append(connector)
    from_port.output_connections.append(connector)


class Port(object):
    """A class that represents an input or output port on a task."""

    def __init__(self,
                 name,
                 task,
                 optional=False,
                 value=None,
                 action=None,
                 constant=False,
                 default=None,
                 doc=None):
        """Constructor."""
        self.name = name
        # tasks are stored as weak refs, to prevent issues with cyclic dependencies and the garbage collector.
        self.task = weakref.ref(task)
        if action is None:
            self.action = 'store'
        else:
            self.action = action
        self.optional = optional
        self.constant = constant
        self.input_connections = []
        self.output_connections = []
        self.set_value(value)
        self._ready = False
        self.default = default
        self.doc = doc

    def reset(self):
        self._ready = False
        self.value = None

    def connect(self, port):
        """Define a connection with the specified port."""
        define_connection(DirectConnector, from_port=port, to_port=self)

    def from_tasks(self):
        """Return the id of the preceding task."""
        return [c.from_port.task() for c in self.input_connections
                if c.from_port.task() != None]

    def get_value(self):
        """Get the value of this port."""
        if self.value is None:
            return self.default
        return self.value

    def set_value(self, value):
        """Set the value of this port."""
        self.value = value

    def compute_value(self):
        """Compute the value from the input connections."""
        #print 'X',self.name, self.action, len(self.input_connections)
        if self.action == 'store':
            if len(self.input_connections) == 1:
                val = self.input_connections[0].get_value()
                if not val is None:
                    self.value = val

        elif self.action == 'store_any':
            for connection in self.input_connections:
                if not connection.ready():
                    continue
                val = connection.get_value()
                if not val is None:
                    self.value = val
                    break

        elif self.action in ['append', 'append_any']:
            tmp = []
            for connection in self.input_connections:
                val = connection.get_value()
                if not val is None:
                    tmp.append(val)
            if len(tmp) > 0:
                self.value = tmp

        elif self.action in ['map', 'map_any']:
            tmp = {}
            for connection in self.input_connections:
                val = connection.get_value()
                if not val is None:
                    tmp[connection.from_port.task().id] = val
            if len(tmp) > 0:
                self.value = tmp

        self.validate()

    def validate(self):
        if self.action in ['store', 'store_any']:
            if not self.optional and self.get_value() is None:
                raise ValueError(
                    "Task %s Port %s requires a nontrivial value.  Value specified is None."
                    % (str(self.task().id), self.name))
        #
        elif self.action in ['append', 'append_any']:
            if not self.optional and self.get_value() is None:
                raise ValueError(
                    "Task %s Port %s requires a nontrivial value.  All input connections have value None."
                    % (str(self.task().id), self.name))
        #
        elif self.action in ['map', 'map_any']:
            if not self.optional and self.get_value() is None:
                raise ValueError(
                    "Task %s Port %s requires a nontrivial value.  All input connections have value None."
                    % (str(self.task().id), self.name))

    def _repn_(self):
        tmp = {}
        tmp['A_TYPE'] = 'Port'
        tmp['Name'] = self.name
        tmp['Task'] = str(self.task().id)
        tmp['Optional'] = str(self.optional)
        tmp['Constant'] = str(self.constant)
        tmp['Value'] = str(self.value)
        tmp['Ready'] = str(self.ready())
        tmp['Action'] = self.action
        tmp['Connections'] = {}
        tmp['Connections']['Inputs'] = []
        for c in self.input_connections:
            tmp['Connections']['Inputs'].append(repr(c))
        tmp['Connections']['Outputs'] = []
        for c in self.output_connections:
            tmp['Connections']['Outputs'].append(repr(c))
        return tmp

    def __repr__(self):
        return str(self)  #pragma:nocover

    def __str__(self, indentation=""):
        return pprint.pformat(self._repn_(), 2)  #pragma:nocover

    def ready(self):
        if not self.get_value() is None:
            return True
        if len(self.input_connections) == 0:
            return self._ready
        if self.action == 'store':
            return self.input_connections[0].ready()
        elif self.action in ['append_any', 'map_any', 'store_any']:
            for connection in self.input_connections:
                if connection.ready():
                    return True
            return False
        elif self.action in ['append', 'map']:
            for connection in self.input_connections:
                if not connection.ready():
                    return False
            return True
        #
        # We should never get here.
        #
        raise IOError(
            "WARNING: unknown action: " + self.action)  #pragma:nocover

    def set_ready(self):
        self._ready = True


class Ports(dict):
    """A class that specifies a set of ports."""

    def __init__(self, task):
        """Constructor."""
        self._name_ = 'Ports'
        # tasks are stored as weak refs, to prevent issues with cyclic dependencies and the garbage collector.
        self._task = weakref.ref(task)
        self._inputs = False
        self._outputs = False

    def set_name(self, name):
        """Set the name of this class instance."""
        self._name_ = name

    def declare(self,
                name,
                optional=False,
                action=None,
                constant=False,
                default=None,
                doc=None):
        """Declare a port."""
        port = Port(
            name,
            self._task(),
            optional=optional,
            action=action,
            constant=constant,
            default=default,
            doc=doc)
        setattr(self, name, port)
        return port

    def __setitem__(self, name, val):
        """Overload this operator to set an attribute with the specified name."""
        self.__setattr__(name, val)

    def __getitem__(self, name):
        """Overload this operator to get the attribute with the specified name."""
        return self.__getattr__(name)

    def __setattr__(self, name, val):
        """Overload this operator to setup a connection."""
        #
        # Directly set attributes whose names begin with '_'
        #
        if name[0] == '_':
            self.__dict__[name] = val
            return
        #
        # Declare a port
        #
        if not name in self.__dict__:
            if not isinstance(val, Port):
                raise TypeError(
                    "Error declaring port '%s' without a Port object" % name)
            dict.__setitem__(self, name, val)
            self.__dict__[name] = val
        #
        # Create a connection to another port
        #
        else:
            if not isinstance(val, Port):
                self.__dict__[name].set_value(val)
            else:
                self.__dict__[name].connect(val)

    def __getattr__(self, name):
        """Overload this operator to setup a connection."""
        try:
            return self.__dict__.__getitem__(name)
        except:
            raise AttributeError("Unknown attribute '%s'" % name)

    def _repn_(self):
        tmp = {}
        tmp['A_TYPE'] = 'Port'
        for k, v in self.__dict__.items():
            if not k.startswith("_"):
                tmp[k] = v._repn_()
        tmp['Name'] = self._name_
        if self._inputs:
            tmp['Mode'] = 'inputs'
        if self._outputs:
            tmp['Mode'] = 'outputs'
        # JPW: a port can't really exist independently of a task - we should check 
        #      this in the constructor.
        if self._task is not None:
            tmp['Owner'] = self._task()._name()
        return tmp

    def __repr__(self):  #pragma:nocover
        """Return a string representation of these connections."""
        attrs = sorted("%s = %r" % (k, v) for k, v in self.__dict__.items()
                       if not k.startswith("_"))
        return "%s(%s)" % (self.__class__.__name__, ", ".join(attrs))

    def __str__(self, nesting=1, indent='', print_name=True):
        return pprint.pformat(self._repn_(), 2, width=150)


class InputPorts(Ports):
    """A class that is used to manage set of input ports."""

    def __init__(self, task):
        """Constructor."""
        Ports.__init__(self, task)
        self._inputs = True


class OutputPorts(Ports):
    """A class that is used to manage set of output ports."""

    def __init__(self, task):
        """Constructor."""
        Ports.__init__(self, task)
        self._outputs = True


class Connector(object):

    def __init__(self, from_port=None, to_port=None):
        """Constructor."""
        if from_port is None:
            self.from_port = NoTask  #pragma:nocover
        else:
            self.from_port = from_port
        if to_port is None:
            self.to_port = NoTask  #pragma:nocover
        else:
            self.to_port = to_port

    def get_value(self):
        raise ValueError(
            "There is no value to get in an abstract Connector object!")  #pragma:nocover

    def ready(self):
        return self.from_port.ready()

    def __repr__(self):
        """Return a string representation for this connection."""
        return str(self)

    def __str__(self):
        """Return a string representation for this connection."""
        return "%s: from=(%s) to=(%s) %s" % (
            str(self.__class__.__name__), str(self.from_port.task().id),
            str(self.to_port.task().id), self.ready())


class DirectConnector(Connector):

    def __init__(self, from_port=None, to_port=None):
        Connector.__init__(self, from_port=from_port, to_port=to_port)

    def get_value(self):
        if self.ready():
            return self.from_port.get_value()
        return None

# A task instance that represents no task.
NoTask = EmptyTask(id=0)
