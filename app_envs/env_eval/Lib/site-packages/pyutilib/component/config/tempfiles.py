#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________
"""A plugin that manages temporary files."""

__all__ = ['ITempfileManager', 'TempfileManagerPlugin', 'TempfileManager']

import os
import time
import tempfile
import logging
import shutil

from pyutilib.component.core import Interface, implements
from pyutilib.component.config.managed_plugin import ManagedSingletonPlugin
from pyutilib.component.config.options import declare_option

deletion_errors_are_fatal = True


class ITempfileManager(Interface):
    """Interface for managing temporary files."""

    def create_tempfile(self, suffix=None, prefix=None, text=False, dir=None):
        """Return the absolute path of a temporary file that is guaranteed to be unique."""

    def create_tempdir(self, suffix=None, prefix=None, dir=None):
        """Return the absolute path of a temporary directory that is guaranteed to be unique."""

    def add_tempfile(self, filename):
        """Declare this file to be temporary."""

    def clear_tempfiles(self, remove=True):
        """Delete all temporary files."""

    def sequential_files(self, ctr=0):
        """Start generating sequential files, using the specified counter"""

    def unique_files(self):
        """Start generating unique files"""

    def push(self):
        """Push tempfiles onto a stack.  This creates a new context for tempfiles."""

    def pop(self, remove=True):
        """Pop tempfiles onto a stack.  Tempfiles that are popped off the stack are deleted."""


class TempfileManagerPlugin(ManagedSingletonPlugin):
    """A plugin that manages temporary files."""

    implements(ITempfileManager)

    def __init__(self, **kwds):
        if getattr(self, '_initialized', False) is True:
            return
        self._initialized = True
        #
        kwds['name'] = 'TempfileManager'
        ManagedSingletonPlugin.__init__(self, **kwds)
        self._tempfiles = [[]]
        declare_option("tempdir", default=None)
        self._ctr = -1

    def create_tempfile(self, suffix=None, prefix=None, text=False, dir=None):
        """
        Return the absolute path of a temporary filename that is
        guaranteed to be unique.  This function generates the file and returns
        the filename.
        """
        if suffix is None:
            suffix = ''
        if prefix is None:
            prefix = 'tmp'
        if dir is None:
            dir = self.tempdir

        ans = tempfile.mkstemp(suffix=suffix, prefix=prefix, text=text, dir=dir)
        ans = list(ans)
        if not os.path.isabs(ans[1]):  #pragma:nocover
            fname = os.path.join(dir, ans[1])
        else:
            fname = ans[1]
        os.close(ans[0])
        if self._ctr >= 0:
            new_fname = os.path.join(dir, prefix + str(self._ctr) + suffix)
            # Delete any file having the sequential name and then
            # rename
            if os.path.exists(new_fname):
                os.remove(new_fname)
            shutil.move(fname, new_fname)
            fname = new_fname
            self._ctr += 1
        self._tempfiles[-1].append(fname)
        return fname

    def create_tempdir(self, suffix=None, prefix=None, dir=None):
        """
        Return the absolute path of a temporary directory that is
        guaranteed to be unique.  This function generates the directory and returns
        the directory name.
        """
        if suffix is None:
            suffix = ''
        if prefix is None:
            prefix = 'tmp'
        if dir is None:
            dir = self.tempdir
        dirname = tempfile.mkdtemp(suffix=suffix, prefix=prefix, dir=dir)
        if self._ctr >= 0:
            new_dirname = os.path.join(dir, prefix + str(self._ctr) + suffix)
            # Delete any directory having the sequential name and then
            # rename
            if os.path.exists(new_dirname):
                shutil.rmtree(new_dirname)
            shutil.move(dirname, new_dirname)
            dirname = new_dirname
            self._ctr += 1

        self._tempfiles[-1].append(dirname)
        return dirname

    def add_tempfile(self, filename, exists=True):
        """Declare this file to be temporary."""
        tmp = os.path.abspath(filename)
        if exists and not os.path.exists(tmp):
            raise IOError("Temporary file does not exist: " + tmp)
        self._tempfiles[-1].append(tmp)

    def clear_tempfiles(self, remove=True):
        """Delete all temporary files."""
        while len(self._tempfiles) > 1:
            self.pop(remove)
        self.pop(remove)

    def sequential_files(self, ctr=0):
        """Start generating sequential files, using the specified counter"""
        self._ctr = ctr

    def unique_files(self):
        """Stop generating sequential files, using the specified counter"""
        self._ctr = -1

    #
    # Support "with" statements, where the pop automatically
    # takes place on exit.
    #
    def push(self):
        self._tempfiles.append([])
        return self

    def __exit__(self, type, value, traceback):
        self.pop(remove=True)

    def pop(self, remove=True):
        files = self._tempfiles.pop()
        if remove:
            for filename in files:
                if os.path.exists(filename):
                    if os.path.isdir(filename):
                        shutil.rmtree(
                            filename,
                            ignore_errors=not deletion_errors_are_fatal)
                    else:
                        try:
                            os.remove(filename)
                        except WindowsError:
                            # Sometimes Windows doesn't release the
                            # file lock immediately when the process
                            # terminates.  If we get an error, wait a
                            # second and try again.
                            try:
                                time.sleep(1)
                                os.remove(filename)
                            except WindowsError:
                                if deletion_errors_are_fatal:
                                    raise
                                else:
                                    # Failure to delete a tempfile
                                    # should NOT be fatal
                                    logger = logging.getLogger(
                                        'pyutilib.component.config')
                                    logger.warning("Unable to delete temporary "
                                                   "file %s" % (filename,))

        if len(self._tempfiles) == 0:
            self._tempfiles = [[]]

#
# This global class provides a convenient handle to this
# singleton plugin
#
TempfileManager = TempfileManagerPlugin()
