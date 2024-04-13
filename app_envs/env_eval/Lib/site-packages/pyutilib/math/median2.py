#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________


def median(mylist):
    """
    Returns the median value of a list
    """
    mylist = list(mylist)
    mylist.sort()
    if (len(mylist) == 0):
        raise ArithmeticError(
            "Attempting to compute the median of a zero-length list")
    elif (len(mylist) == 1):
        return mylist[0]
    elif (divmod(len(mylist), 2)[1] == 1):
        return mylist[(len(mylist) - 1) / 2]
    ndx = len(mylist) / 2
    return (mylist[ndx - 1] + mylist[ndx]) / 2.0
