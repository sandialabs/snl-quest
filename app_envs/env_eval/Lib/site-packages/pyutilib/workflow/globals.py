#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________

__all__ = ['unique_id', 'reset_id_counter']


def unique_id():
    unique_id.counter += 1
    return unique_id.counter


unique_id.counter = 0


def reset_id_counter():
    global unique_id
    unique_id.counter = 0
