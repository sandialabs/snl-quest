#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________

__all__ = ['TaskPlugin', 'TaskFactory', 'WorkflowPlugin']

from pyutilib.workflow import task
from pyutilib.workflow import workflow
from pyutilib.component.core import Plugin, implements, Interface, CreatePluginFactory, alias


class IWorkflowTask(Interface):
    pass


TaskFactory = CreatePluginFactory(IWorkflowTask)


class TaskPlugin(Plugin, task.Task):

    implements(IWorkflowTask)

    def __init__(self, *args, **kwds):  #pragma:nocover
        Plugin.__init__(self, *args, **kwds)
        task.Task.__init__(self, *args, **kwds)

    def __repr__(self):
        return task.Task.__repr__(self)  #pragma:nocover


class WorkflowPlugin(Plugin, workflow.Workflow):

    implements(IWorkflowTask)

    def __init__(self, *args, **kwds):  #pragma:nocover
        Plugin.__init__(self, *args, **kwds)
        workflow.Workflow.__init__(self, *args, **kwds)

    def __repr__(self):  #pragma:nocover
        return workflow.Workflow.__repr__(self)


class Selection_Task(TaskPlugin):

    alias('workflow.selection')

    def __init__(self, *args, **kwds):
        TaskPlugin.__init__(self, *args, **kwds)
        #
        self.inputs.declare('index')
        self.inputs.declare('data')
        #
        self.outputs.declare('selection')

    def execute(self):
        self.selection = self.data[self.index]


class Switch_Task(TaskPlugin):

    alias('workflow.switch')

    def __init__(self, *args, **kwds):
        TaskPlugin.__init__(self, *args, **kwds)
        self._branches = {}
        self.inputs.declare('value')

    def add_branch(self, value, task):
        self._branches[value] = 'task' + str(task.id)
        self.output_controls.declare(self._branches[value])

        task.input_controls.declare('task' + str(self.id))
        setattr(task.input_controls, 'task' + str(self.id),
                self.output_controls[self._branches[value]])

    def execute(self):
        flag = False
        for key in self._branches:
            if self.value == key:
                self.output_controls[self._branches[key]].set_ready()
                flag = True
            else:
                self.output_controls[self._branches[key]].reset()
        if not flag:
            raise ValueError(
                "Branch condition has value '%s' but no branch is indexed with that value.\n    Valid branch indices: %s"
                % (str(self.value), sorted(self._branches.keys())))

    def __repr__(self):
        return TaskPlugin.__repr__(self)  #pragma:nocover


class IfThen_Task(Switch_Task):

    alias('workflow.branch')

    def __init__(self, *args, **kwds):
        Switch_Task.__init__(self, *args, **kwds)

    def __repr__(self):
        return Switch_Task.__repr__(self)  #pragma:nocover
