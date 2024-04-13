#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________

import sys
from pyutilib.misc import misc

if sys.version_info >= (3, 0):
    xrange = range


def _cross_exec(set_tuple):
    """
    Function used by cross() to generate the cross-product of a tuple
    """
    resulting_set = []
    if len(set_tuple) == 1:
        for val in set_tuple[0]:
            resulting_set.append([val])
    else:
        tmp_set = _cross_exec(set_tuple[1:])
        for val in set_tuple[0]:
            for item in tmp_set:
                #print val, item
                resulting_set.append([val] + item)
    return resulting_set


def cross(set_tuple):
    """
    Returns the cross-product of a tuple of values
    """
    result_set = []
    tmp_set = _cross_exec(set_tuple)
    for val in tmp_set:
        result_set.append(tuple(val))
    return result_set

#def tmp_cross(*args):
#    ans = [[]]
#    for arg in args:
#      ans = [x+[y] for x in ans for y in arg]
#    return ans

if sys.version_info < (3, 0):

    def cross_iter(*sets):
        """
        An iterator function that generates a cross product of
        a set.

        Derived from code developed by Steven Taschuk
        """
        wheels = map(iter, sets)  # wheels like in an odometer
        digits = [it.next() for it in wheels]
        while True:
            yield tuple(digits[:])
            for i in xrange(len(digits) - 1, -1, -1):
                try:
                    digits[i] = wheels[i].next()
                    break
                except StopIteration:
                    wheels[i] = iter(sets[i])
                    digits[i] = wheels[i].next()
            else:
                break

    def flattened_cross_iter(*sets):
        """
        An iterator function that generates a cross product of
        a set, and flattens it.
        """
        wheels = map(iter, sets)  # wheels like in an odometer
        digits = [it.next() for it in wheels]
        ndigits = len(digits)
        while True:
            yield misc.flatten_tuple(tuple(digits[:]))
            for i in xrange(ndigits - 1, -1, -1):
                try:
                    digits[i] = wheels[i].next()
                    break
                except StopIteration:
                    wheels[i] = iter(sets[i])
                    digits[i] = wheels[i].next()
            else:
                break

else:

    def cross_iter(*sets):
        """
        An iterator function that generates a cross product of
        a set.

        Derived from code developed by Steven Taschuk
        """
        wheels = list(map(iter, sets))  # wheels like in an odometer
        digits = [next(it) for it in wheels]
        while True:
            yield tuple(digits[:])
            for i in range(len(digits) - 1, -1, -1):
                try:
                    digits[i] = next(wheels[i])
                    break
                except StopIteration:
                    wheels[i] = iter(sets[i])
                    digits[i] = next(wheels[i])
            else:
                break

    def flattened_cross_iter(*sets):
        """
        An iterator function that generates a cross product of
        a set, and flattens it.
        """
        wheels = list(map(iter, sets))  # wheels like in an odometer
        digits = [next(it) for it in wheels]
        ndigits = len(digits)
        while True:
            yield misc.flatten_tuple(tuple(digits[:]))
            for i in range(ndigits - 1, -1, -1):
                try:
                    digits[i] = next(wheels[i])
                    break
                except StopIteration:
                    wheels[i] = iter(sets[i])
                    digits[i] = next(wheels[i])
            else:
                break
