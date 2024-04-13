#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________
#
# Class to encapsulate a progress indicator

__all__ = ['progress']

import sys
import time
import unittest


class progressException(Exception):
    'Error to raise for any recursive problem.'


class progress:

    def __init__(self, period=1):
        self._twissler = ["|", "/", "-", "\\", "|"]
        self._state = 0
        self._period = period
        self._ctr = period

    def getStart(self):
        sys.stdout.write('\t[  ')  # include 2 spaces for the twissler
        sys.stdout.flush()

    def getStart(self, text):
        sys.stdout.write('\t %s [  ' %
                         (text))  # include 2 spaces for the twissler
        sys.stdout.flush()

    def moveOn(self):
        try:
            self._ctr += 1
            if self._ctr <= self._period:
                return
            self._ctr = 1
            self._state += 1
            if self._state >= 5:
                self._state = 1
            sys.stdout.write(
                chr(8) + chr(8) + self._twissler[self._state] + ']')
            sys.stdout.flush()
        except:
            raise progressException('failed to progress')


class TestCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testProgress(self):
        p = progress()
        p.getStart("HERE")
        for a in range(0, 10, 1):
            p.moveOn()
            time.sleep(0.2)


if __name__ == '__main__':
    widgetTestSuite = unittest.TestSuite()
    widgetTestSuite.addTest(TestCase("testProgress"))
    runner = unittest.TextTestRunner()
    runner.run(widgetTestSuite)
