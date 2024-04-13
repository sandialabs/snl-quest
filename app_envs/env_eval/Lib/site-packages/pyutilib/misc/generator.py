#
# Copyright (C) 2009, All Rights Reserved
# David Beazley
# Permission granted to distribute with PyUtilib under the BSD license
#


def coroutine(func):

    def start(*args, **kwargs):
        cr = func(*args, **kwargs)
        #print 'y',cr.send(None)
        return cr

    return start
