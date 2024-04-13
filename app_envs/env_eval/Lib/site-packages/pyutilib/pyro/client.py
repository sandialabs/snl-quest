#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________

__all__ = ['Client']

import sys
import os, socket
import time

from six import iteritems

import pyutilib.pyro.util
from pyutilib.pyro.util import get_nameserver, using_pyro3, using_pyro4
from pyutilib.pyro.util import Pyro as _pyro

if sys.version_info >= (3, 0):
    xrange = range
    import queue as Queue
else:
    import Queue


class Client(object):

    def __init__(self,
                 group=":PyUtilibServer",
                 type=None,
                 host=None,
                 port=None,
                 num_dispatcher_tries=30,
                 caller_name="Client",
                 dispatcher=None):

        if _pyro is None:
            raise ImportError("Pyro or Pyro4 is not available")
        self.type = type
        self.id = 0

        # Deprecated in Pyro3
        # Removed in Pyro4
        if using_pyro3:
            _pyro.core.initClient()

        self.ns = None

        self.CLIENTNAME = "%d@%s" % (os.getpid(), socket.gethostname())
        self.dispatcher = None
        if dispatcher is None:
            self.ns = get_nameserver(
                host=host, port=port, caller_name=caller_name)
            if self.ns is None:
                raise RuntimeError("Client failed to locate Pyro name "
                                   "server on the network!")
            print('Client attempting to find Pyro dispatcher object...')
            self.URI = None
            cumulative_sleep_time = 0.0
            for i in xrange(0, num_dispatcher_tries):

                dispatchers = pyutilib.pyro.util.get_dispatchers(ns=self.ns)

                for (name, uri) in dispatchers:
                    self.URI = uri
                    print("Dispatcher Object URI: " + str(self.URI))
                    break

                if self.URI is not None:
                    break

                sleep_interval = 10.0
                print("Client failed to find dispatcher object from name "
                      "server after %d attempts and %5.2f seconds - trying "
                      "again in %5.2f seconds." %
                      (i + 1, cumulative_sleep_time, sleep_interval))

                time.sleep(sleep_interval)
                cumulative_sleep_time += sleep_interval
            if self.URI is None:
                print('Client could not find dispatcher object - giving up')
                raise SystemExit

            # connect to the dispatcher
            if using_pyro3:
                self.dispatcher = _pyro.core.getProxyForURI(self.URI)
            else:
                self.dispatcher = _pyro.Proxy(self.URI)

            print("Connection to dispatch server established after %d "
                  "attempts and %5.2f seconds - this is client: %s" %
                  (i + 1, cumulative_sleep_time, self.CLIENTNAME))

            # There is no need to retain the proxy connection to the
            # nameserver, so free up resources on the nameserver thread
            if using_pyro4:
                self.ns._pyroRelease()
            else:
                self.ns._release()

        else:
            assert port is None
            assert host is None
            self.dispatcher = dispatcher
            if using_pyro4:
                self.URI = self.dispatcher._pyroUri
            else:
                self.URI = self.dispatcher.URI
            print('Client assigned dispatcher with URI=%s' % (self.URI))

    def close(self):
        if self.dispatcher is not None:
            if using_pyro4:
                self.dispatcher._pyroRelease()
            else:
                self.dispatcher._release()

    def clear_queue(self, override_type=None, verbose=False):
        task_type = override_type if (override_type is not None) else self.type
        if verbose:
            print("Clearing all tasks and results for "
                  "type=" + str(task_type))
        self.dispatcher.clear_queue(type=task_type)

    def add_tasks(self, tasks, verbose=False):
        for task_type in tasks:
            for task in tasks[task_type]:
                if task['id'] is None:
                    self.id += 1
                task['client'] = self.CLIENTNAME
                if verbose:
                    print("Adding task " + str(task['id']) + " to dispatcher "
                          "queue with type=" + str(task_type) + " - in bulk")
        self.dispatcher.add_tasks(tasks)

    def add_task(self, task, override_type=None, verbose=False):
        task_type = override_type if (override_type is not None) else self.type
        if task['id'] is None:
            self.id += 1
        task['client'] = self.CLIENTNAME
        if verbose:
            print("Adding task " + str(task['id']) + " to dispatcher "
                  "queue with type=" + str(task_type) + " - individually")
        self.dispatcher.add_task(task, type=task_type)

    def get_result(self, override_type=None, block=True, timeout=5):
        task_type = override_type if (override_type is not None) else self.type
        return self.dispatcher.get_result(
            type=task_type, block=block, timeout=timeout)

    def get_results(self, override_type=None, block=True, timeout=5):
        task_type = override_type if (override_type is not None) else self.type
        return self.dispatcher.get_results(
            [(task_type, block, timeout)])[task_type]

    def get_results_all_queues(self):
        return self.dispatcher.get_results_all_queues()

    def num_tasks(self, override_type=None):
        task_type = override_type if (override_type is not None) else self.type
        return self.dispatcher.num_tasks(type=task_type)

    def num_results(self, override_type=None):
        task_type = override_type if (override_type is not None) else self.type
        return self.dispatcher.num_results(type=override_type)

    def queues_with_results(self):
        return self.dispatcher.queues_with_results()
