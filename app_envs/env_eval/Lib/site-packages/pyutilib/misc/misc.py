#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________

import fnmatch
import errno
import linecache
import os
import re
import shutil
import stat
import sys
import warnings

if (sys.platform[0:3] == "win"):  #pragma:nocover
    executable_extension = ".exe"
else:  #pragma:nocover
    executable_extension = ""

import six


def deprecated(deprecated_function):
    """ Code slightly adapted from the Python Decorator Library

    This is a decorator which can be used to mark functions as deprecated.
    It will result in a warning being emitted when the function is used.

    Example use:

    @deprecated
    def some_func ( ):
        ...
    """

    def wrapper_function(*args, **kwargs):
        warnings.warn_explicit(
            "Use of deprecated function '%s'." % deprecated_function.__name__,
            category=DeprecationWarning,
            filename=deprecated_function.__code__.co_filename,
            lineno=deprecated_function.__code__.co_firstlineno + 1)
        return deprecated_function(*args, **kwargs)

    return wrapper_function


def tostr(array):
    """ Create a string from an array of numbers """
    tmpstr = ""
    for val in array:
        tmpstr = tmpstr + " " + repr(val)
    return tmpstr.strip()


def flatten(x):
    """Flatten nested iterables"""

    def _flatten(x, ans_):
        for el in x:
            if not type(el) is str and hasattr(el, "__iter__"):
                # NB: isinstance can be SLOW if it is going to return false,
                # so we will do one extra hasattr() check that will pretty
                # much assure that it will be True
                # NB: we will flatten anything that looks iterable, except strings
                try:
                    el_it = iter(el)
                    _flatten(el_it, ans_)
                except:
                    ans_.append(el)
            else:
                ans_.append(el)

    # flatten() is really just a recursive routine; however, if we do a
    # naive recursive call, we end up creating small temporary lists and
    # throwing them away.  We could add an optional second argument
    # (like _flatten), but then we need to do an "if ans is None: ans =
    # []" check.  This dual-function approach appears to be the most
    # efficient.
    if type(x) is str or not hasattr(x, "__iter__"):
        return x
    ans = []
    _flatten(x, ans)
    return ans


def flatten_list(x):
    """Flatten nested lists"""
    if type(x) is not list:
        return x
    x_len = len(x)
    i = 0
    while i < x_len:
        if type(x[i]) is list:
            x_len += len(x[i]) - 1
            x[i:i + 1] = x[i]
        else:
            i += 1
    return x


def recursive_flatten_tuple(val):
    """ Flatten nested tuples """
    if type(val) is not tuple:
        return val
    rv = ()
    for i in val:
        if type(i) is tuple:
            rv = rv + flatten_tuple(i)
        else:
            rv = rv + (i,)
    return rv


def flatten_tuple(x):
    """ Flatten nested tuples """
    if type(x) is not tuple:
        return x
    x_len = len(x)
    i = 0
    while i < x_len:
        if type(x[i]) is tuple:
            x_len += len(x[i]) - 1
            x = x[:i] + x[i] + x[i + 1:]
        else:
            i += 1
    return x


#
# A better method for removing directory trees, which handles MSWindows errors
# that are associated with read-only files.
#
def handleRemoveReadonly(func, path, exc):
    excvalue = exc[1]
    if func in (os.rmdir, os.remove) and excvalue.errno == errno.EACCES:
        os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)  # 0777
        func(path)
    else:
        raise


def rmtree(dir):
    if not os.path.exists(dir):
        return
    shutil.rmtree(dir, ignore_errors=False, onerror=handleRemoveReadonly)


whitespace_re = re.compile('\s+')


def quote_split(regex_str, src=None):
    """
    Split a string, but do not split the string between quotes.  If only
    one argument is provided (the string to be split), regex_str
    defaults to '\s+'.  In addition, regex_str can be either a regular
    expression string, or a compiled expression.
    """

    if src is None:
        src = regex_str
        regex = whitespace_re
    elif 'match' in dir(regex_str):
        regex = regex_str
    else:
        regex = re.compile(regex_str)

    # We need to figure out where the quoted strings are.  Given that
    # lots of things may be escaped (e.g., '\\\"'), we can only find the
    # "real" quotes by walking the entire string. <sigh>.
    tokens = []
    start = 0
    inQuote = ''
    escaping = False
    for idx, char in enumerate(src):
        if escaping:
            escaping = False
        elif char == inQuote:
            inQuote = ''
        else:
            if not inQuote and start <= idx:
                g = regex.match(src[idx:])
                if g:
                    tokens.append(src[start:idx])
                    start = idx + len(g.group())
                    # NB: we still want to parse the remainder of the patern
                    # for things like escape characters so that we correctly
                    # parse the entire source string; hence, no 'elif'
            if char == '\\':
                escaping = True
            elif not inQuote and (char == '"' or char == "'"):
                inQuote = char

    if inQuote:
        raise ValueError("ERROR: unterminated quotation found in quote_split()")

    tokens.append(src[start:])
    return tokens


def traceit(frame, event, arg):  #pragma:nocover
    """
    A utility for tracing Python executions.  Use this function by
    executing:

    sys.settrace(traceit)
    """
    if event == "line":
        lineno = frame.f_lineno
        try:
            filename = frame.f_globals["__file__"]
        except:
            return traceit
        if (filename.endswith(".pyc") or filename.endswith(".pyo")):
            filename = filename[:-1]
        name = frame.f_globals["__name__"]
        line = linecache.getline(filename, lineno)
        print("%s:%s: %s" % (name, lineno, line.rstrip()))
    return traceit


def tuplize(dlist, d, name):
    """
    Convert a list into a list of tuples.
    """
    if len(dlist) % d != 0:
        raise ValueError("Cannot tuplize data for set " + str(
            name) + " because its length " + str(len(dlist)) +
                         " is not a multiple of dimen " + str(d))
    j = 0
    t = []
    rv = []
    for i in dlist:
        t.append(i)
        j += 1
        if j == d:
            rv.append(tuple(t))
            t = []
            j = 0
    return rv


def find_files(directory, *args):
    for root, dirs, files in os.walk(directory):
        for basename in files:
            for pattern in args:
                if fnmatch.fnmatch(basename, pattern):
                    filename = os.path.join(root, basename)
                    yield filename


def search_file(filename,
                search_path=None,
                implicitExt=executable_extension,
                executable=False,
                isfile=True,
                validate=None):
    """
    Given a search path, find a file.

    Can specify the following options:
       search_path - A list of directories that are searched, or the
           name of a single directory to search. If unspecified,
           then all directories in the PATH defined for the current
           environment will be searched.
       executable_extension - This string is used to see if there is an
           implicit extension in the filename
       executable - Test if the file is an executable (default=False)
       isfile - Test if the file is a file (default=True)
    """
    if search_path is None:
        #
        # Use the PATH environment if it is defined and not empty
        #
        if "PATH" in os.environ and os.environ["PATH"] != "":
            search_path = os.environ['PATH'].split(os.pathsep)
        else:
            search_path = os.defpath.split(os.pathsep)
    else:
        if isinstance(search_path, six.string_types):
            search_path = (search_path,)
    for path in search_path:
        for ext in ('', implicitExt):
            test_fname = os.path.join(path, filename + ext)
            if os.path.exists(test_fname) \
                   and (not isfile or os.path.isfile(test_fname)) \
                   and (not executable or os.access(test_fname, os.X_OK)):
                file = os.path.abspath(test_fname)
                if validate is None or validate(file):
                    return file
    return None


def sort_index(l):
    """Returns a list, where the i-th value is the index of the i-th smallest
    value in the data 'l'"""
    return list(index
                for index, item in sorted(
                    enumerate(l), key=lambda item: item[1]))


def count_lines(file):
    """Returns the number of lines in a file."""
    count = 0
    for line in open(file, "r"):
        count = count + 1
    return count


class Bunch(dict):
    """
    A class that can be used to store a bunch of data dynamically

    foo = Bunch(data=y, sq=y*y, val=2)
    print foo.data
    print foo.sq
    print foo.val

    Adapted from code developed by Alex Martelli and submitted to
    the ActiveState Programmer Network http://aspn.activestate.com
    """

    def __init__(self, **kw):
        dict.__init__(self, kw)
        self.__dict__.update(kw)


class Container(dict):
    """
    A generalization of Bunch.  This class allows all other attributes to have a
    default value of None.  This borrows the output formatting ideas from the
    ActiveState Code Container (recipe 496697).
    """

    def __init__(self, *args, **kw):
        for arg in args:
            for item in quote_split('[ \t]+', arg):
                r = item.find('=')
                if r != -1:
                    try:
                        val = eval(item[r + 1:])
                    except:
                        val = item[r + 1:]
                    kw[item[:r]] = val
        dict.__init__(self, kw)
        self.__dict__.update(kw)
        if not '_name_' in kw:
            self._name_ = self.__class__.__name__

    def update(self, d):
        """
        The update is specialized for JSON-like data.  This
        recursively replaces dictionaries with Container objects.
        """
        for k in d:
            if type(d[k]) is dict:
                tmp = Container()
                tmp.update(d[k])
                self.__setattr__(k, tmp)
            elif type(d[k]) is list:
                val = []
                for i in d[k]:
                    if type(i) is dict:
                        tmp = Container()
                        tmp.update(i)
                        val.append(tmp)
                    else:
                        val.append(i)
                self.__setattr__(k, val)
            else:
                self.__setattr__(k, d[k])

    def set_name(self, name):
        self._name_ = name

    def __setitem__(self, name, val):
        self.__setattr__(name, val)

    def __getitem__(self, name):
        return self.__getattr__(name)

    def __setattr__(self, name, val):
        if name[0] != '_':
            dict.__setitem__(self, name, val)
        self.__dict__[name] = val

    def __getattr__(self, name):
        try:
            return dict.__getitem__(self, name)
        except:
            if name[0] == '_':
                raise AttributeError("Unknown attribute %s" % name)
        return None

    def __repr__(self):
        attrs = sorted("%s = %r" % (k, v) for k, v in self.__dict__.items()
                       if not k.startswith("_"))
        return "%s(%s)" % (self.__class__.__name__, ", ".join(attrs))

    def __str__(self):
        return self.as_string()

    def __str__(self, nesting=0, indent=''):
        attrs = []
        indentation = indent + "    " * nesting
        for k, v in self.__dict__.items():
            if not k.startswith("_"):
                text = [indentation, k, ":"]
                if isinstance(v, Container):
                    if len(v) > 0:
                        text.append('\n')
                    text.append(v.__str__(nesting + 1))
                elif isinstance(v, list):
                    if len(v) == 0:
                        text.append(' []')
                    else:
                        for v_ in v:
                            text.append('\n' + indentation + "-")
                            if isinstance(v_, Container):
                                text.append('\n' + v_.__str__(nesting + 1))
                            else:
                                text.append(" " + repr(v_))
                else:
                    text.append(' ' + repr(v))
                attrs.append("".join(text))
        attrs.sort()
        return "\n".join(attrs)


class Options(Container):
    """
    This is a convenience class.  A common use of the Container class is to
    manage options that are passed into a class/solver/framework.  Thus,
    it's convenient to call this an Options object.
    """

    def __init__(self, *args, **kw):
        Container.__init__(self, *args, **kw)
        self.set_name('Options')


def create_hardlink(src, dst):
    """
    Create a hard link where dst points to src.
    """
    if os.name == 'nt' and sys.version_info[:2] < (3,2):
        # Windows; Python added native support for hard links in 3.2
        import ctypes
        if not ctypes.windll.kernel32.CreateHardLinkA(dst, src, 0):
            raise OSError("Failed to create hard link for file %s" % (src))
    else:
        # Unix; Windows >= Python3.2
        os.link(src, dst)
