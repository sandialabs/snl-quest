#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________

__all__ = ('Task', 'TaskProcessingError')

from pyutilib.pyro.util import using_pyro4

#
# Task returns a native Python data type.  This provides more
# more flexibility in the choice of serialization schemes than
# a user-defined class.  Also, the default serializer used by Pyro4
# ('serpent') does not support most user defined classes. The
# serializer can be set to 'pickle' by the user if they need
# this functionality (see: Pyro4 docs).
#


def Task(id=None, data=None, generateResponse=True):
    return {'id': id,
            'data': data,
            'result': None,
            'generateResponse': generateResponse,
            'processedBy': None,
            'client': None,
            'type': None}


#
# A simple yet identifiable type that indicates
# when an exception is encountered during task
# processing by a worker. We provide custome
# serialization hooks
#
class TaskProcessingError(Exception):

    def __init__(self, message):
        super(TaskProcessingError, self).__init__(message)

#
# register the special serialization hooks because
# the default Pyro4 serializer (Serpent) can not deal
# with custom classes
#
#
# Note: We can use this same mechanism to allow Task to be
#       re-implemented as a custom class.  HOWEVER,
#       TaskProcessingError is designed to be returned on the result
#       "slot" of Task, and when I've attempted to register
#       (de)serialization hooks for both Task and TaskProcessingError,
#       the end result is that the TaskProcessingError
#       de-serialization hook never gets called (leaving it in its
#       serialized dict form on the deserialized Task object). This
#       defeats the purpose of creating a TaskProcessingError type.
#       Perhaps there is a way around this, but for now I am giving
#       priority to having an error type that can be transmitted
#       for all serializers in both Pyro and Pyro4 (over making
#       Task a class again).
#
if using_pyro4:
    import Pyro4
    from Pyro4.util import SerializerBase

    # register hooks for TaskProcessingError
    def TaskProcessingError_to_dict(obj):
        return {"__class__": "pyutilib.pyro.task.TaskProcessingError",
                "message": obj.args[0]}

    def dict_to_TaskProcessingError(classname, d):
        return TaskProcessingError(d['message'])

    SerializerBase.register_class_to_dict(TaskProcessingError,
                                          TaskProcessingError_to_dict)
    SerializerBase.register_dict_to_class(
        "pyutilib.pyro.task.TaskProcessingError", dict_to_TaskProcessingError)
