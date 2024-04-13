#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________

# Q: When passing options, these values do not initialize the startup task.
#    Is this a bug?
# TODO: only set option values for variables that show up in a workflow's inputs
# TODO: add graceful management of exceptions
#       show the task tree, etc...

__all__ = ['Workflow']

import argparse
from collections import deque
from six import iterkeys

from pyutilib.workflow.task import Task, EmptyTask, NoTask
from pyutilib.misc import Options

try:
    from collections import OrderedDict
except:
    from ordereddict import OrderedDict


def _collect_parser_groups(t):
    for key in t._parser_group:
        #
        # NOTE: we are changing the properties of the group
        # instances here.  This is OK _only_ because we are
        # printing the help info and then terminating.
        #

        # FIXME: The 'parser' object is not defined in the lines below
        raise NotImplementedError("")
        #t._parser_group[key].parser = parser
        #parser.add_argument_group(t._parser_group[key])


def _set_arguments(t):
    for arg in t._parser_arg:
        args = arg[0]
        kwargs = arg[1]
        try:
            t._parser.add_argument(*args, **kwargs)
        except argparse.ArgumentError:
            pass


class Workflow(Task):

    def __init__(self, id=None, name=None, parser=None):
        Task.__init__(self, id=id, name=name, parser=None)
        self._tasks = {}
        self._start_task = EmptyTask()
        self._final_task = EmptyTask()
        self.add(self._start_task)
        self.add(self._final_task)

    def add(self, task, loadall=True):
        if self.debug:
            print("ADDING", task.id)  #pragma:nocover
        if task.id == NoTask.id:
            return
        if task.id in self._tasks:
            return
        self._tasks[task.id] = task
        if not loadall:
            return
        for name in task.inputs:
            for t in task.inputs[name].from_tasks():
                self.add(t)

            if len(task.inputs[name].from_tasks()) > 0:
                continue

            if not task.inputs[name].constant:
                #
                # Constant input values are not added to the start task
                #
                if not name in self._start_task.outputs:
                    self._start_task.outputs.declare(name)
                    self.inputs.declare(name, optional=True)
                # TODO: this is a bit of a hack...
                val = getattr(task.inputs, name).get_value()
                try:
                    setattr(task.inputs, name, getattr(self._start_task.outputs,
                                                       name))
                except ValueError:
                    # TBD: when do we get this exception?
                    pass
                getattr(self.inputs, name).set_value(val)
        for name in task.output_controls:
            for c in task.output_controls[name].output_connections:
                self.add(c.to_port.task())
        #
        for name in task.outputs:
            if len(task.outputs[name].output_connections) > 0:
                for c in task.outputs[name].output_connections:
                    self.add(c.to_port.task())
            else:
                if name in self._final_task.inputs:
                    raise ValueError(
                        "Cannot declare a workplan with multiple output values that share the same name: %s"
                        % name)
                self.outputs.declare(name)
                self._final_task.inputs.declare(name)
                setattr(self._final_task.inputs, name, task.outputs[name])

    def _call_init(self, *options, **kwds):
        Task._call_init(self, *options, **kwds)
        for i in self.inputs:
            val = self.inputs[i].get_value()
            if val is not None:
                self._start_task.outputs[i].set_value(val)
                self._start_task.outputs[i].set_ready()
        #
        # TBD: this appears to be redundant
        #
        #for key in kwds:
        #    if key not in self._start_task.outputs:
        #        raise ValueError, "Cannot specify value for option %s.  Valid option names are %s" % (key, self._start_task.outputs.keys())
        #    self._start_task.outputs[key].set_value( kwds[key] )

    def _call_fini(self, *options, **kwds):
        ans = Options()
        for key in self._final_task.inputs:
            self._final_task.inputs[key].compute_value()
            ans[key] = self._final_task.inputs[key].get_value()
            getattr(self.outputs, key).set_value(ans[key])
        for key in self.outputs:
            self.outputs[key].set_ready()
        return ans

    def set_options(self, args):
        self._dfs_([self._start_task.id], lambda t: t.set_options(args))

    def options(self):
        return self._start_task.outputs.keys()

    def print_help(self):
        parser = argparse.ArgumentParser()
        self._dfs_([self._start_task.id], _collect_parser_groups)
        parser.print_help()

    def set_arguments(self, parser=None):
        if parser is None:
            parser = self._parser
        self._dfs_([self._start_task.id], _set_arguments)

    def reset(self):
        return self._dfs_([self._start_task.id], lambda t: t.reset())

    def execute(self):
        #return self._dfs_([self._start_task.id], lambda t: t.__call__())
        if self.debug:  #pragma:nocover
            print(self.name, '---------------')
            print(self.name, '---------------')
            print(self.name, '   STARTING')
            print(self.name, '---------------')
            print(self.name, '---------------')
        #
        queued = set([self._start_task.id])
        queue = deque([self._start_task])
        waiting = OrderedDict()
        while len(queue) + len(waiting) > 0:
            for id in list(iterkeys(waiting)):
                t = waiting[id]
                if not t.id in queued and t.ready():
                    #
                    if self.debug:  #pragma:nocover
                        print(self.name, "WAITING: ", t.id,
                              " not queued and task ready")
                        print(self.name, "Waiting task", t.name, t.id,
                              t.ready())
                    #
                    queue.append(t)
                    queued.add(t.id)
                    del waiting[t.id]
            if len(queue) == 0:
                break
                # TBD: should we sleep and add a timelimit before raising this exception?
                #if len(waiting) == 0:
                #    break
                #print self.name, "ERROR", waiting.keys()
                #raise RuntimeError, "Workflow failed to terminate normally.  All available tasks are blocked."
            task = queue.popleft()
            #
            if self.debug:  #pragma:nocover
                print(self.name, "TASK   ", str(task))
                print(self.name, "QUEUE  ", queued)
                print(self.name, "WAITING", waiting.keys())
                print(self.name, "Executing Task " + task.name,
                      task.next_task_ids())
            #
            queued.remove(task.id)
            task()
            for t in task.next_tasks():
                if t.id in queued:
                    continue
                if t.ready():
                    #
                    if self.debug:  #pragma:nocover
                        print(self.name, "NEXT: ", t.id,
                              " not queued and task ready")
                        print(self.name, "Scheduling task", t.name, t.id,
                              t.ready())
                    #
                    queue.append(t)
                    queued.add(t.id)
                    if t.id in waiting:
                        del waiting[t.id]
                else:
                    if not t.id in waiting:
                        waiting[t.id] = t
                    #
                    if self.debug:  #pragma:nocover
                        print(self.name, "NEXT: ", t.id,
                              " not queued and task NOT ready")
                        print(self.name, "Ignoring task", t.name, t.id,
                              t.ready())
            if self.debug:  #pragma:nocover
                print(self.name, "FINAL QUEUE  ", queued)
                print(self.name, "FINAL WAITING", waiting.keys())
                print(self.name, '---------------')
                print(self.name, "    LOOP")
                print(self.name, '---------------')
        if self.debug:  #pragma:nocover
            print(self.name, '---------------')

    def __str__(self):
        return "\n".join(["Workflow %s:" % self.name] + self._dfs_(
            [self._start_task.id], lambda t: t._name()))

    def __repr__(self):
        return "Workflow %s:\n" % self.name + Task.__repr__(
            self) + '\n' + "\n".join(
                self._dfs_([self._start_task.id], lambda t: str(t)))

    def _dfs_(self, indices, fn, touched=None):
        if touched is None:
            touched = set()
        ans = []
        for i in indices:
            if i in touched:
                # With this design, this condition should never be triggered
                # TODO: verify that this is an O(n) search algorithm; I think it's
                # O(n^2)
                continue  #pragma:nocover
            ok = True
            task = self._tasks[i]
            for j in task.prev_task_ids():
                if (j == NoTask.id) or (j in touched):
                    continue
                ok = False
                break
            if not ok:
                continue
            tmp = fn(task)
            if tmp is not None:
                ans.append(tmp)
            touched.add(i)
            ans = ans + self._dfs_(task.next_task_ids(), fn, touched)
        return ans
