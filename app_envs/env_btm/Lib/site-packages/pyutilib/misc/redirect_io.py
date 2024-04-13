#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________

import sys
from contextlib import contextmanager
from six import StringIO

_old_stdout = []
_old_stderr = []
_local_file = []

try:
    unicode
except:
    basestring = str


def setup_redirect(output):
    """
    Redirect stdout and stderr to a specified output, which
    is either the string name for a file, or a file-like class.
    """
    _old_stdout.append(sys.stdout)
    _old_stderr.append(sys.stderr)
    if isinstance(output, basestring):
        sys.stderr = _Redirecter(output)
        _local_file.append(True)
    else:
        sys.stderr = output
        _local_file.append(False)
    sys.stdout = sys.stderr


def reset_redirect():
    """ Reset redirection to use standard stdout and stderr """
    if len(_old_stdout) > 0:
        if _local_file.pop():
            sys.stdout.close()
        sys.stdout = _old_stdout.pop()
        sys.stderr = _old_stderr.pop()


@contextmanager
def capture_output(output=None):
    """Temporarily redirect stdout into a string buffer."""
    if output is None:
        output = StringIO()
    try:
        setup_redirect(output)
        yield output
    finally:
        reset_redirect()


#
# A class used to manage the redirection of IO.  The sys.stdout and
# sys.stderr values are set to an instance of this class.
#
class _Redirecter:

    def __init__(self, ofile):
        """ Constructor. """
        self.ofile = ofile
        self._out = open(ofile, "w")

    def write(self, s):
        """ Write an item. """
        self._out.write(s)

    def flush(self):
        """ Flush the output. """
        self._out.flush()

    def close(self):
        """ Close the stream. """
        self._out.close()
