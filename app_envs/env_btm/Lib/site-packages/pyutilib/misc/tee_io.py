#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________

import sys
try:
    from io import StringIO
except:
    from StringIO import StringIO


class TeeStream(object):
    """This class implements a simple 'Tee' of the specified python
    stream.  Since this presents a full file interface, TeeStream
    objects may be arbitrarily nested."""

    def __init__(self, stream):
        self.stream = stream
        self.buffer = StringIO()

    def write(self, data):
        self.buffer.write(data)
        self.stream.write(data)

    def writelines(self, sequence):
        for x in sequence:
            self.write(x)

    def reset(self):
        self.buffer = StringIO()


class ConsoleBuffer(object):
    """This class implements a simple 'Tee' of the python stdout and
    stderr so the output can be captured and reported programmatically.
    We need a specialized class here because other applications /
    methods explicitly write to sys.stderr and sys.stdout, so it is
    insufficient to 'wrap' the streams like the TeeStream class;
    instead, we must replace the standard stdout and stderr objects with
    our own duplicator."""

    class _Duplicate(object):

        def __init__(self, a, b):
            self.a = a
            self.b = b

        def write(self, data):
            self.a.write(data)
            self.b.write(data)

    def __init__(self):
        self._dup_out = self._dup_err = None
        self._raw_out = sys.stdout
        self._raw_err = sys.stderr
        self.reset()

    def __del__(self):
        if self._dup_out is not None and self._dup_out is not sys.stdout:
            raise RuntimeError("ConsoleBuffer: Nesting violation " \
                  "(attempting to delete the buffer while stdout is " \
                  "redirected away from this buffer).")
        if self._dup_err is not None and self._dup_err is not sys.stderr:
            raise RuntimeError("ConsoleBuffer: Nesting violation " \
                  "(attempting to delete the buffer while stderr is " \
                  "redirected away from this buffer).")
        sys.stdout = self._raw_out
        sys.stderr = self._raw_err

    def reset(self):
        if self._dup_out is not None and self._dup_out is not sys.stdout:
            raise RuntimeError("ConsoleBuffer: Nesting violation " \
                  "(attempting to reset() when stdout has been redirected " \
                  "away from this buffer).")
        if self._dup_err is not None and self._dup_err is not sys.stderr:
            raise RuntimeError("ConsoleBuffer: Nesting violation " \
                  "(attempting to reset() when stderr has been redirected " \
                  "away from this buffer).")

        self.out = StringIO()
        self.err = StringIO()
        self._dup_out = sys.stdout = \
                        ConsoleBuffer._Duplicate(self.out, self._raw_out)
        self._dup_err = sys.stderr = \
                        ConsoleBuffer._Duplicate(self.err, self._raw_err)
