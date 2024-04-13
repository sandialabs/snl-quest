#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________

import re
import copy
import sys
import os
import os.path
import difflib
import zipfile
import gzip
import filecmp
import math
if sys.version_info >= (3, 0):
    xrange = range
    import io

strict_float_p = re.compile(
    r"(?<![\w+-\.])(?:[+-])?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?\b")
relaxed_float_p = re.compile(
    r"(?:[+-])?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?")
whitespace_p = re.compile(r" +")


def remove_chars_in_list(s, l):
    if len(l) == 0:
        return s

    return "".join(x for x in s if x not in l)


def get_desired_chars_from_file(f, nchars, l=""):
    retBuf = ""
    while nchars > 0:
        buf = f.read(nchars)
        if len(buf) == 0:
            break

        buf = remove_chars_in_list(buf, l)
        nchars -= len(buf)
        retBuf = retBuf + buf

    return retBuf


def open_possibly_compressed_file(filename):
    if not os.path.exists(filename):
        raise IOError("cannot find file `" + filename + "'")
    try:
        is_zipfile = zipfile.is_zipfile(filename)
    except:
        is_zipfile = False
    if is_zipfile:
        zf1 = zipfile.ZipFile(filename, "r")
        if len(zf1.namelist()) != 1:
            raise IOError("cannot compare with a zip file that contains "
                          "multiple files: `" + filename + "'")
        if sys.version_info < (3, 0):
            return zf1.open(zf1.namelist()[0], 'r')
        else:
            return io.TextIOWrapper(
                zf1.open(zf1.namelist()[0], 'r'), encoding='utf-8', newline='')
    elif filename.endswith('.gz'):
        if sys.version_info < (3, 0):
            return gzip.open(filename, "r")
        else:
            return io.TextIOWrapper(
                gzip.open(filename, 'r'), encoding='utf-8', newline='')
    else:
        return open(filename, "r")


def file_diff(filename1, filename2, lineno=None, context=None):
    INPUT1 = open_possibly_compressed_file(filename1)
    lines1 = INPUT1.readlines()
    for i in range(0, len(lines1)):
        lines1[i] = lines1[i].strip()
    INPUT1.close()

    INPUT2 = open_possibly_compressed_file(filename2)
    lines2 = INPUT2.readlines()
    for i in range(0, len(lines2)):
        lines2[i] = lines2[i].strip()
    INPUT2.close()

    s = ""
    if lineno is None:
        for line in difflib.unified_diff(
                lines2, lines1, fromfile=filename2, tofile=filename1):
            s += line + "\n"
    else:
        if context is None:
            context = 3
        start = lineno - context
        stop = lineno + context
        if start < 0:
            start = 0
        if stop > len(lines1):
            stop = len(lines1)
        if stop > len(lines2):
            stop = len(lines2)
        for line in difflib.unified_diff(
                lines2[start:stop],
                lines1[start:stop],
                fromfile=filename2,
                tofile=filename1):
            s += line + "\n"
    return s


def read_and_filter_line(stream, ignore_chars, filter):
    # If either line is composed entirely of characters to
    # ignore, then get another one.  In this way we can
    # skip blank lines that are in one file but not the other
    lineno = 0
    line = ""
    while not line:
        line = stream.readline()
        lineno += 1
        if line == "":
            return None, lineno
        line_ = remove_chars_in_list(line, ignore_chars)
        if not line_:
            line = False
            continue
        if filter is not None:
            filtered = filter(line)
            if filtered is True:
                line = False  # Ignore this line
            elif filtered is False:
                line = line_
            else:
                line = filtered
        else:
            line = line_
    return line, lineno


def _extract_floats(line, regex):
    ans = []
    while True:
        g = regex.search(line)
        if g is None:
            return ans, line
        ans.append(float(g.group()))
        line = regex.sub(" # ", line, count=1)


def compare_file_with_numeric_values(filename1,
                                     filename2,
                                     ignore=["\n", "\r"],
                                     filter=None,
                                     tolerance=0.0,
                                     strict_numbers=True):
    """
    Do a simple comparison of two files that ignores differences
    in newline types and whitespace.  Numeric values are compared within a specified tolerance.

    The return value is the tuple: (status,lineno).  If status is True,
    then a difference has occured on the specified line number.  If
    the status is False, then lineno is None.

    The goal of this utility is to simply indicate whether there are
    differences in files.  The Python 'difflib' is much more comprehensive
    and consequently more costly to apply.  The shutil.filecmp utility is
    similar, but it does not ignore differences in file newlines.  Also,
    this utility can ignore an arbitrary set of characters.
    """
    if not os.path.exists(filename1):
        raise IOError("compare_file: cannot find file `" + filename1 + "' (in "
                      + os.getcwd() + ")")
    if not os.path.exists(filename2):
        raise IOError("compare_file: cannot find file `" + filename2 + "' (in "
                      + os.getcwd() + ")")

    #if filecmp.cmp(filename1, filename2):
    #    return [False, None, ""]

    if strict_numbers:
        float_p = strict_float_p
    else:
        float_p = relaxed_float_p

    try:
        absolute_tolerance, relative_tolerance = tolerance
    except:
        absolute_tolerance = relative_tolerance = tolerance

    INPUT1 = INPUT2 = None
    try:
        INPUT1 = open_possibly_compressed_file(filename1)
        INPUT2 = open_possibly_compressed_file(filename2)

        lineno = 0
        while True:

            # If either line is composed entirely of characters to
            # ignore, then get another one.  In this way we can
            # skip blank lines that are in one file but not the other

            try:
                line1, delta_lineno = read_and_filter_line(
                    INPUT1, ignore, filter)
            except UnicodeDecodeError:
                err = sys.exc_info()[1]
                raise RuntimeError(
                    "Decoding error while processing file %s: %s" %
                    (filename1, str(err)))

            lineno += delta_lineno
            try:
                line2 = read_and_filter_line(INPUT2, ignore, filter)[0]
            except UnicodeDecodeError:
                err = sys.exc_info()[1]
                raise RuntimeError(
                    "Decoding error while processing file %s: %s" %
                    (filename2, str(err)))

            #print "line1 '%s'" % line1
            #print "line2 '%s'" % line2

            if line1 is None and line2 is None:
                return [False, None, ""]

            if line1 is None or line2 is None:
                return [True, lineno, file_diff(
                    filename1, filename2, lineno=lineno)]

            try:
                floats1, line1 = _extract_floats(line1, float_p)
                floats2, line2 = _extract_floats(line2, float_p)
            except:
                return [True, lineno, file_diff(
                    filename1, filename2, lineno=lineno)]

            #print "floats1 '%s'" % floats1
            #print "floats2 '%s'" % floats2

            if len(floats1) != len(floats2):
                return [True, lineno, file_diff(
                    filename1, filename2, lineno=lineno)]

            for v1, v2 in zip(floats1, floats2):
                vDiff = math.fabs(v1 - v2)
                vMax = max(math.fabs(v1), math.fabs(v2))
                if vDiff > absolute_tolerance and \
                   vDiff / vMax > relative_tolerance:
                    return [True, lineno, file_diff(
                        filename1, filename2, lineno=lineno)]

            line1 = whitespace_p.sub(' ', line1.strip())
            line2 = whitespace_p.sub(' ', line2.strip())

            #print "Line1 '%s'" % line1
            #print "Line2 '%s'" % line2

            if line1 != line2:
                return [True, lineno, file_diff(
                    filename1, filename2, lineno=lineno)]
    finally:
        if INPUT1 is not None:
            INPUT1.close()
        if INPUT2 is not None:
            INPUT2.close()

    return [False, None, ""]


def compare_file(filename1,
                 filename2,
                 ignore=["\t", " ", "\n", "\r"],
                 filter=None,
                 tolerance=None):
    """
    Do a simple comparison of two files that ignores differences
    in newline types.  If filename1 or filename2 is a zipfile, then it is
    assumed to contain a single file.

    The return value is the tuple: (status,lineno).  If status is True,
    then a difference has occured on the specified line number.  If
    the status is False, then lineno is None.

    The goal of this utility is to simply indicate whether there are
    differences in files.  The Python 'difflib' is much more comprehensive
    and consequently more costly to apply.  The shutil.filecmp utility is
    similar, but it does not ignore differences in file newlines.  Also,
    this utility can ignore an arbitrary set of characters.

    The 'filter' function evaluates each line separately.  If it returns True,
    then that line should be ignored.  If it returns a string, then that string replaces
    the line.
    """
    if tolerance is not None:
        tmp = copy.copy(ignore)
        tmp.remove(' ')
        tmp.remove('\t')
        try:
            tol, strict = tolerance
        except:
            tol = tolerance
            strict = True
        return compare_file_with_numeric_values(
            filename1,
            filename2,
            ignore=tmp,
            filter=filter,
            tolerance=tol,
            strict_numbers=strict)

    if not os.path.exists(filename1):
        raise IOError("compare_file: cannot find file `" + filename1 + "' (in "
                      + os.getcwd() + ")")
    if not os.path.exists(filename2):
        raise IOError("compare_file: cannot find file `" + filename2 + "' (in "
                      + os.getcwd() + ")")

    INPUT1 = INPUT2 = None
    try:
        INPUT1 = open_possibly_compressed_file(filename1)
        INPUT2 = open_possibly_compressed_file(filename2)
        #
        # This is check is deferred until the zipfiles are setup to ensure a
        # consistent logic for zipfile analysis.  If the files are the same,
        # but they are zipfiles with > 1 files, then we raise an exception.
        #
        if not sys.platform.startswith('win') and os.stat(filename1) == os.stat(
                filename2):
            return [False, None, ""]
        #
        lineno = 0
        while True:
            # If either line is composed entirely of characters to
            # ignore, then get another one.  In this way we can
            # skip blank lines that are in one file but not the other

            line1, delta_lineno = read_and_filter_line(INPUT1, ignore, filter)
            lineno += delta_lineno
            line2 = read_and_filter_line(INPUT2, ignore, filter)[0]

            if line1 is None and line2 is None:
                return [False, None, ""]

            if line1 != line2:
                return [True, lineno, file_diff(
                    filename1, filename2, lineno=lineno)]
    finally:
        if INPUT1 is not None:
            INPUT1.close()
        if INPUT2 is not None:
            INPUT2.close()


def compare_large_file(filename1,
                       filename2,
                       ignore=["\t", " ", "\n", "\r"],
                       bufSize=1 * 1024 * 1024):
    """
    Do a simple comparison of two files that ignores white space, or
    characters specified in "ignore" list.

    The return value is True if a difference is found, False otherwise.

    For very long text files, this function will be faster than
    compare_file() because it reads the files in by large chunks
    instead of by line.  The cost is that you don't get the lineno
    at which the difference occurs.
    """

    INPUT1 = open_possibly_compressed_file(filename1)
    try:
        INPUT2 = open_possibly_compressed_file(filename2)
    except IOError:
        INPUT1.close()
        raise
    #
    # This is check is deferred until the zipfiles are setup to ensure a consistent logic for
    # zipfile analysis.  If the files are the same, but they are zipfiles with > 1 files, then we
    # raise an exception.
    #
    if not sys.platform.startswith('win') and os.stat(filename1) == os.stat(
            filename2):
        INPUT1.close()
        INPUT2.close()
        return False

    f1Size = os.stat(filename1).st_size
    f2Size = os.stat(filename2).st_size

    result = False

    while True:
        buf1 = get_desired_chars_from_file(INPUT1, bufSize, ignore)
        buf2 = get_desired_chars_from_file(INPUT2, bufSize, ignore)

        if len(buf1) == 0 and len(buf2) == 0:
            break
        elif len(buf1) == 0 or len(buf2) == 0:
            result = True
            break

        if len(buf1) != len(buf2) or buf1 != buf2:
            result = True
            break

    INPUT1.close()
    INPUT2.close()
    return result
