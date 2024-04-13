#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________
"""
Python modules that use Pyro to manage a generic task queue.

These modules were adapted from Pyro's distributed2 example.
"""

from pyutilib.pyro.util import get_nameserver, get_dispatchers, shutdown_pyro_components, using_pyro3, using_pyro4, Pyro
from pyutilib.pyro.task import Task, TaskProcessingError
from pyutilib.pyro.client import Client
from pyutilib.pyro.worker import TaskWorker, MultiTaskWorker, TaskWorkerServer
from pyutilib.pyro.dispatcher import Dispatcher, DispatcherServer
from pyutilib.pyro.nameserver import start_ns, start_nsc

#
# Pyro3 License
#

#
#Pyro Software License (MIT license):
#
#Pyro is Copyright (c) by Irmen de Jong.
#
#Permission is hereby granted, free of charge, to any person obtaining a
#copy of this software and associated documentation files (the "Software"),
#to deal in the Software without restriction, including without limitation
#the rights to use, copy, modify, merge, publish, distribute, sublicense,
#and/or sell copies of the Software, and to permit persons to whom the
#Software is furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included
#in all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
#THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
#OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
#OTHER DEALINGS IN THE SOFTWARE.
#
#This is the "MIT Software License" which is Open
#Source Initiative (OSI) certified, and GPL-compatible.  See
#http://www.opensource.org/licenses/mit-license.php (it strongly resembles
#the modified BSD license).
#

#
# Pyro4 License
#

#
#Pyro - Python Remote Objects
#Software License, copyright, and disclaimer
#
#  Pyro is Copyright (c) by Irmen de Jong (irmen@razorvine.net).
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.
#
#
#This is the "MIT Software License" which is OSI-certified, and GPL-compatible.
#See http://www.opensource.org/licenses/mit-license.php
