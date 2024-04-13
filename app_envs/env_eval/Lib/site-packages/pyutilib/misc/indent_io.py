#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________


class StreamIndenter(object):
    """Mock-up of a file-like object that wraps another file-like object
    and indents all data using the specified string before passing it to
    the underlying file.  Since this presents a full file interface,
    StreamIndenter objects may be arbitrarily nested."""

    def __init__(self, ostream, indent="        "):
        self.os = ostream
        self.indent = indent
        self.stripped_indent = indent.rstrip()
        self.newline = True

    def __getattr__(self, name):
        return getattr(self.os, name)

    def write(self, data):
        if not len(data):
            return
        lines = data.split('\n')
        if self.newline:
            if lines[0]:
                self.os.write(self.indent+lines[0])
            else:
                self.os.write(self.stripped_indent)
        else:
            self.os.write(lines[0])
        if len(lines) < 2:
            self.newline = False
            return
        for line in lines[1:-1]:
            if line:
                self.os.write("\n"+self.indent+line)
            else:
                self.os.write("\n"+self.stripped_indent)
        if lines[-1]:
            self.os.write("\n"+self.indent+lines[-1])
            self.newline = False
        else:
            self.os.write("\n")
            self.newline = True

    def writelines(self, sequence):
        for x in sequence:
            self.write(x)
