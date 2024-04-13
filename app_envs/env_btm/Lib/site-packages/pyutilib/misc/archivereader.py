#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________

__all__ = ['ArchiveReaderFactory', 'ArchiveReader', 'ZipArchiveReader',
           'TarArchiveReader', 'DirArchiveReader', 'FileArchiveReader',
           'GzipFileArchiveReader', 'BZ2FileArchiveReader']

import os
import tempfile
import shutil
import posixpath

_sep = '/'

zipfile_available = False
tarfile_available = False
gzip_available = False
bz2_available = False
try:
    import zipfile
    zipfile_available = True
except:
    pass
try:
    import tarfile
    tarfile_available = True
except:
    pass
try:
    import gzip
    gzip_available = True
except:
    pass
try:
    import bz2
    bz2_available = True
except:
    pass

_WindowsError = None
try:
    _WindowsError = WindowsError
except NameError:
    # not windows
    pass

#
# This class presents a simple interface for unpacking
# archives such a .zip and .tar (bz2 or gzip) as well as
# normal directories. Keywords make convenient it to partially unpack
# archives based on a subdirectory name or maximum recursion depth,
#
#
#
# Bugs:
#  * Python 2.5 and 2.6: The tarfile module incorrectly recognizes plain
#    text files as tar archives. This prevents an exception from being thrown
#    in the ArchiveReaderFactory when a non-archive/directory element is provided.
#


def ArchiveReaderFactory(dirname, **kwds):
    if not os.path.exists(ArchiveReader.normalize_name(dirname)):
        raise IOError("Cannot find file or directory `" + dirname +
                      "'\nPath expanded to: '" + ArchiveReader.normalize_name(
                          dirname) + "'")
    if ArchiveReader.isDir(dirname):
        return DirArchiveReader(dirname, **kwds)
    elif zipfile_available and ArchiveReader.isZip(dirname):
        return ZipArchiveReader(dirname, **kwds)
    elif tarfile_available and ArchiveReader.isTar(dirname):
        return TarArchiveReader(dirname, **kwds)
    elif gzip_available and ArchiveReader.isGzipFile(dirname):
        return GzipFileArchiveReader(dirname, **kwds)
    elif bz2_available and ArchiveReader.isBZ2File(dirname):
        return BZ2FileArchiveReader(dirname, **kwds)
    elif ArchiveReader.isFile(dirname):
        return FileArchiveReader(dirname, **kwds)
    else:
        raise ValueError("ArchiveReaderFactory was given an "
                         "unrecognized archive type with "
                         "name '%s'" % dirname)


class ArchiveReader(object):

    @staticmethod
    def isDir(name):
        return os.path.isdir(ArchiveReader.normalize_name(name))

    @staticmethod
    def isZip(name):
        if not zipfile_available:
            raise ImportError("zipfile support is disabled")
        try:
            return zipfile.is_zipfile(ArchiveReader.normalize_name(name))
        except:
            return False

    @staticmethod
    def isTar(name):
        if not tarfile_available:
            raise ImportError("tarfile support is disabled")
        return tarfile.is_tarfile(ArchiveReader.normalize_name(name))

    @staticmethod
    def isArchivedFile(name):
        return (not (ArchiveReader.isDir(name) or ArchiveReader.isFile(name))) and \
            (tarfile_available and ArchiveReader.isTar(name)) or \
            (zipfile_available and ArchiveReader.isZip(name)) or \
            (gzip_available and ArchiveReader.isGzipFile(name)) or \
            (bz2_available and ArchiveReader.isBZ2File(name))

    @staticmethod
    def isGzipFile(name):
        if not gzip_available:
            raise ImportError("gzip support is disabled")
        try:
            f = gzip.GzipFile(ArchiveReader.normalize_name(name))
            f.read(1)
            f.close()
        except IOError:
            return False
        return True

    @staticmethod
    def isBZ2File(name):
        if not bz2_available:
            raise ImportError("bz2 support is disabled")
        try:
            f = bz2.BZ2File(ArchiveReader.normalize_name(name))
            f.read(1)
            f.close()
        except IOError:
            return False
        except EOFError:
            return False
        return True

    @staticmethod
    def isFile(name):
        return os.path.isfile(ArchiveReader.normalize_name(name))

    @staticmethod
    def normalize_name(filename):
        """Turns the given file name into a normalized absolute path"""
        if filename is not None:
            filename = os.path.expanduser(filename)
            if not os.path.isabs(filename):
                filename = os.path.abspath(filename)
            filename = ArchiveReader._posix_name(filename)
            return posixpath.normpath(filename)

    @staticmethod
    def _posix_name(filename):
        if filename is not None:
            return filename.replace('\\', '/')

    def __init__(self, name, *args, **kwds):
        posixabsname = self.normalize_name(name)
        if not os.path.exists(posixabsname):
            raise IOError("cannot find file or directory `" + posixabsname +
                          "'")

        self._abspath = os.path.dirname(posixabsname)
        self._basename = os.path.basename(posixabsname)
        self._archive_name = posixabsname

        subdir = kwds.pop('subdir', None)
        if (subdir is not None) and (subdir.strip() == ''):
            subdir = None
        maxdepth = kwds.pop('maxdepth', None)
        self._filter = kwds.pop('filter', None)

        self._subdir = posixpath.normpath(ArchiveReader._posix_name(subdir))+_sep \
                       if (subdir is not None) else None

        self._maxdepth = maxdepth
        if (self._maxdepth is not None) and (self._maxdepth < 0):
            raise ValueError("maxdepth must be >= 0")

        self._names_list = []
        self._artificial_dirs = set()
        self._extractions = set()
        # the python zipfile or tarfile object or None for (dir)
        self._handler = None
        self._workdir = tempfile.mkdtemp()

        self._init(*args, **kwds)

        if self._filter is not None:
            self._names_list = [_f for _f in self._names_list \
                                if not self._filter(_f)]

    def name(self):
        return self._archive_name

    def getExtractionDir(self):
        return self._workdir

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        if self._handler is not None:
            self._handler.close()
        if (self._workdir is not None) and \
           (os.path.exists(self._workdir)):
            shutil.rmtree(self._workdir, True)
        self._workdir = None

    def clear_extractions(self):
        # don't do anything to directories since they may have existed
        # prior to extracting them and we don't know what they
        # contained
        for name in self._extractions:
            if os.path.exists(name) and \
               (not os.path.isdir(name)):
                os.remove(name)
        self._extractions.clear()
        # If the directories existed in the workdir, then they will be
        # taken care of here
        if (self._workdir is not None) and \
           (os.path.exists(self._workdir)):
            for root, dirs, files in os.walk(self._workdir):
                while len(dirs):
                    shutil.rmtree(posixpath.join(root, dirs.pop()), True)
                while len(files):
                    os.remove(posixpath.join(root, files.pop()))

    def getnames(self):
        return self._names_list

    def contains(self, name):
        return name in self._names_list

    def _validate_name(self, name):
        name = self._posix_name(name)
        if (name is None) and (len(self._names_list) == 0):
            raise KeyError("The archive is empty!")
        elif (name is None) and (len(self._names_list) > 1):
            raise KeyError("A name argument is required when "
                           "the archive has more than one member")
        elif name is None:
            name = self._names_list[0]

        if name in self._artificial_dirs:
            return None, name

        if not self.contains(name):
            #
            # There are cases (e.g., Windows zipped folders) where
            # directory names don't appear in the list of objects
            # available to in zipfile. We will try to retroactively
            # handle this case by check if any listed archive members
            # begin with name+_sep, and if so, adding the directory
            # name to the _names_list
            #
            checkname = name + _sep
            if (self._maxdepth is None) or (
                    checkname.count(_sep) <= self._maxdepth + 1):
                for othername in self._fulldepth_names_list:
                    if othername.startswith(checkname):
                        self._artificial_dirs.add(name)
                        self._names_list.append(name)
                        return None, name
            msg = ("There is no item named '%s' in "
                   "the archive %s" % (name, self._basename))
            if self._subdir is not None:
                msg += ", subdirectory: " + self._subdir
            raise KeyError(msg)
        absname = name if (self._subdir is None) else self._subdir + name
        return absname, name

    def open(self, name=None, *args, **kwds):
        absname, relname = self._validate_name(name)
        return self._openImp(absname, relname, *args, **kwds)

    def _openImp(self, name, *args, **kwds):
        raise NotImplementedError("This method has not been " "implemented")

    def extract(self, member=None, path=None, recursive=False, *args, **kwds):
        absolute_name, relative_name = self._validate_name(member)
        dst, children = self._extractImp(absolute_name, relative_name, path,
                                         recursive, *args, **kwds)
        self._extractions.add(dst)
        if not recursive:
            assert len(children) == 0
        else:
            self._extractions.update(children)
        return dst

    def _extractImp(self, absolute_name, relative_name, path, recursive, *args,
                    **kwds):
        raise NotImplementedError("This method has not been " "implemented")

    def extractall(self,
                   path=None,
                   members=None,
                   recursive=False,
                   *args,
                   **kwds):
        names = None
        if members is not None:
            names = set(members)
        else:
            names = set(self._names_list)
        # Save the expense checking recursions if there is no point
        if len(names) == len(self._names_list):
            recursive = False
        dsts = []
        while names:
            absolute_name, relative_name = self._validate_name(names.pop())
            dst, children = self._extractImp(absolute_name, relative_name, path,
                                             recursive, *args, **kwds)
            if not recursive:
                assert len(children) == 0
            dsts.append(dst)
            self._extractions.add(dst)
            if len(children):
                self._extractions.update(children)
                names = names - set(children)

        return dsts

    # like shutil.copytree, but will handle existing
    # directories the same way tarfile extraction
    # occurs by adding new content rather than
    # raising an exception
    @staticmethod
    def _copytree(src, dst, ignores=None, maxdepth=None):

        assert os.path.exists(src) and os.path.isdir(src)
        if not os.path.exists(dst):
            os.makedirs(dst)

        if (maxdepth is None) or (maxdepth > 0):

            if maxdepth is not None:
                maxdepth -= 1

            names = os.listdir(src)
            if ignores is not None:
                ignored_names = ignores
            else:
                ignored_names = set()

            for name in names:
                srcname = posixpath.join(src, name)
                if srcname in ignored_names:
                    continue
                dstname = posixpath.join(dst, name)
                if os.path.isdir(srcname):
                    ArchiveReader._copytree(
                        srcname, dstname, ignores=ignores, maxdepth=maxdepth)
                else:
                    shutil.copy2(srcname, dstname)
        try:
            shutil.copystat(src, dst)
        except _WindowsError:
            # can't copy file access times on Windows
            pass


class _ziptar_base(ArchiveReader):

    @staticmethod
    def _fixnames(names, subdir, maxdepth):
        names_list = [posixpath.normpath(name) for name in names]
        subdir_depth = 0
        if subdir is not None:
            names_list = [name for name in names_list \
                          if name.startswith(subdir)]
            subdir_depth = subdir.count(_sep)
        fulldepth_names_list = list(names_list)
        if maxdepth is not None:
            names_list = [name for name in fulldepth_names_list \
                          if (name.count(_sep) - subdir_depth) <= maxdepth]
        if subdir is not None:
            names_list = [name.replace(subdir,'') \
                          for name in names_list]
            fulldepth_names_list = [name.replace(subdir,'') \
                               for name in fulldepth_names_list]
        return names_list, fulldepth_names_list, subdir_depth

    def _extractImp(self, absolute_name, relative_name, path, recursive):

        use_handler = True
        if absolute_name is None:
            # This case implies that this was an artificially
            # added directory that was not appearing in the
            # archive even though it technically exists
            # (a rare but possible edge case)
            use_handler = False
            absolute_name = relative_name if (
                self._subdir is None) else self._subdir + relative_name

        tmp_dst = posixpath.join(self._workdir, absolute_name)

        if use_handler:
            try:
                self._handler.extract(absolute_name, self._workdir)
            except KeyError:  # sometimes directories need an _sep ending
                self._handler.extract(absolute_name + _sep, self._workdir)
        else:
            if not os.path.exists(tmp_dst):
                os.makedirs(tmp_dst)

        dst = tmp_dst
        if path is not None:

            dst = posixpath.join(path, relative_name)
            if os.path.isdir(tmp_dst):
                # updated the timestamp if it exists, otherwise
                # just create the directory
                self._copytree(tmp_dst, dst, maxdepth=0)
            else:
                if not os.path.exists(os.path.dirname(dst)):
                    os.makedirs(os.path.dirname(dst))
                try:
                    os.rename(tmp_dst, dst)
                except OSError:
                    shutil.copy2(tmp_dst, dst)

        children = []
        if os.path.isdir(dst) and recursive:
            new_names = [relname for relname in self._names_list \
                         if relname.startswith(relative_name)]
            if relative_name in new_names:
                new_names.remove(relative_name)
            for childname in new_names:
                absolute_childname, relative_childname = self._validate_name(
                    childname)
                childdst, recursives = self._extractImp(
                    absolute_childname, relative_childname, path, False)
                assert len(recursives) == 0
                children.append(childdst)

        return dst, children


class ZipArchiveReader(_ziptar_base):

    def _init(self, *args, **kwds):
        if zipfile is None:
            raise ImportError("zipfile support is disabled")
        assert (self._abspath is not None)
        assert (self._basename is not None)
        assert (self._archive_name is not None)

        if not self.isZip(self._archive_name):
            raise TypeError("Unrecognized zipfile format for file: %s" %
                            (self._archive_name))

        self._handler = zipfile.ZipFile(self._archive_name, *args, **kwds)
        self._names_list, self._fulldepth_names_list, self._subdir_depth = \
            self._fixnames(self._handler.namelist(), self._subdir, self._maxdepth)

    def _openImp(self, absolute_name, relative_name, *args, **kwds):
        f = None
        try:
            if absolute_name is None:
                raise KeyError
            f = self._handler.open(absolute_name, *args, **kwds)
        except KeyError:
            # when this method is called we have already verified the name
            # existed in the list, so this must be a directory
            raise IOError("Failed to open with zipfile, this must be a "
                          "directory: %s" % (absolute_name))
        return f


class TarArchiveReader(_ziptar_base):

    def _init(self, *args, **kwds):
        if not tarfile_available:
            raise ImportError("tarfile support is disabled")
        assert (self._abspath is not None)
        assert (self._basename is not None)
        assert (self._archive_name is not None)

        if not self.isTar(self._archive_name):
            raise TypeError("Unrecognized tarfile format for file: %s" %
                            (self._archive_name))

        self._handler = tarfile.open(self._archive_name, *args, **kwds)
        self._names_list, self._fulldepth_names_list, self._subdir_depth = \
            self._fixnames(self._handler.getnames(), self._subdir, self._maxdepth)

    def _openImp(self, absolute_name, relative_name, *args, **kwds):
        f = None
        if absolute_name is not None:
            f = self._handler.extractfile(absolute_name, *args, **kwds)
        if f is None:
            # when this method is called we have already verified the name
            # existed in the list, so this must be a directory
            raise IOError("Failed to open with tarfile, this must be a "
                          "directory: %s" % (absolute_name))
        return f


class DirArchiveReader(ArchiveReader):

    def _init(self, *args, **kwds):
        assert (self._abspath is not None)
        assert (self._basename is not None)
        assert (self._archive_name is not None)

        if kwds:
            raise ValueError("Unexpected keyword options found "
                             "while initializing '%s':\n\t%s" %
                             (type(self).__name__,
                              ','.join(sorted(kwds.keys()))))
        if args:
            raise ValueError("Unexpected arguments found "
                             "while initializing '%s':\n\t%s" %
                             (type(self).__name__, ','.join(args)))

        if not self.isDir(self._archive_name):
            raise TypeError("Path not recognized as a directory: %s" %
                            (self._archive_name))

        rootdir = self._archive_name
        if self._subdir is not None:
            rootdir = posixpath.join(rootdir, self._subdir)
            if not os.path.exists(rootdir):
                raise IOError(
                    "Subdirectory '%s' does not exists in root directory: %s" %
                    (self._subdir, self._archive_name))
            self._names_list = self._walk(rootdir, maxdepth=self._maxdepth + 1)
        else:
            self._names_list = self._walk(rootdir, maxdepth=self._maxdepth)
        self._fulldepth_names_list = self._walk(rootdir)

    @staticmethod
    def _walk(rootdir, maxdepth=None):
        names_list = []
        for root, dirs, files in os.walk(rootdir, topdown=True):
            prefix = posixpath.relpath(ArchiveReader._posix_name(root), rootdir)
            if prefix.endswith(_sep):
                prefix = prefix[:-1]
            if prefix == '.':
                prefix = ''
            for dname in dirs:
                names_list.append(posixpath.join(prefix, dname))
            if maxdepth is not None and prefix.count(_sep) >= maxdepth:
                continue
            for fname in files:
                names_list.append(posixpath.join(prefix, fname))
        return names_list

    def _extractImp(self, absolute_name, relative_name, path, recursive):

        assert absolute_name is not None

        if path is not None:
            dst = posixpath.join(path, relative_name)
        else:
            dst = posixpath.join(self._workdir, absolute_name)
        src = posixpath.join(self._archive_name, absolute_name)
        children = []
        if os.path.isdir(src):
            if recursive:
                ignores = []
                for child in self._walk(src):
                    rname = posixpath.join(relative_name, child)
                    if rname in self._names_list:
                        children.append(rname)
                    else:
                        ignores.append(posixpath.join(src, child))
                self._copytree(src, dst, ignores=ignores)

            elif not os.path.exists(dst):
                os.makedirs(dst)
            # if not recursive and the destination is an existing
            # directory, then there is nothing to do
        else:
            if not os.path.exists(posixpath.dirname(dst)):
                os.makedirs(os.path.dirname(dst))
            shutil.copy2(src, dst)

        return dst, children

    def _openImp(self, absolute_name, relative_name, *args, **kwds):
        assert absolute_name is not None
        return open(
            posixpath.join(self._archive_name, absolute_name), 'rb', *args, **
            kwds)


class FileArchiveReader(ArchiveReader):

    _handler_class = open

    def _extract_name(self, name):
        return name

    def _init(self):
        assert (self._abspath is not None)
        assert (self._basename is not None)
        assert (self._archive_name is not None)

        if self._subdir is not None:
            raise ValueError("'subdir' keyword option is not handled by "
                             "'%s'" % (type(self).__name__))
        if self._maxdepth is not None:
            raise ValueError("'maxdepth' keyword option is not handled by "
                             "'%s'" % (type(self).__name__))

        if not self.isFile(self._archive_name):
            raise TypeError("Path does not point to a file: %s" %
                            (self._archive_name))
        extract_name = self._extract_name(self._basename)
        if extract_name is not None:
            self._names_list = [extract_name]
            self._fulldepth_names_list = [extract_name]
            self._extract_name = extract_name
        else:
            self._names_list = [self._basename]
            self._fulldepth_names_list = [self._basename]
            self._extract_name = None

    def _extractImp(self, absolute_name, relative_name, path, recursive):
        assert absolute_name == self._extract_name
        assert relative_name == self._extract_name
        if recursive:
            raise ValueError("Recursive extraction does not make "
                             "sense for compressed file archive types")
        if path is not None:
            dst = posixpath.join(path, relative_name)
        else:
            dst = posixpath.join(self._workdir, absolute_name)
        with open(dst, 'wb') as dstf:
            handler = self._handler_class(self._archive_name, 'rb')
            shutil.copyfileobj(handler, dstf)
            handler.close()

        return dst, []

    def _openImp(self, absolute_name, relative_name, *args, **kwds):
        assert absolute_name == self._extract_name
        return self._handler_class(self._archive_name, 'rb', *args, **kwds)


class GzipFileArchiveReader(FileArchiveReader):

    _handler_class = gzip.GzipFile if gzip_available else None

    def _extract_name(self, name):
        # see the man page for gzip
        basename, ext = os.path.splitext(name)
        if ext == self._suffix:
            return basename
        else:
            return None

    def __init__(self, *args, **kwds):
        if not gzip_available:
            raise ImportError("gzip support is disabled")
        self._suffix = kwds.pop('suffix', '.gz')
        super(GzipFileArchiveReader, self).__init__(*args, **kwds)
        if not self.isGzipFile(self._archive_name):
            raise TypeError("Unrecognized gzip format for file: %s" %
                            (self._archive_name))

    def _extractImp(self, absolute_name, relative_name, path, recursive):
        if self._extract_name is None:
            raise TypeError(
                "Extraction disabled. File suffix %s does not "
                "match expected suffix for compression type %s. "
                "The default suffix can be changed by passing "
                "'suffix=.<ext>' into the ArchiveReader constructor." % (
                    os.path.splitext(self._basename)[1], self._suffix))
        return FileArchiveReader._extractImp(self, absolute_name, relative_name,
                                             path, recursive)


class BZ2FileArchiveReader(FileArchiveReader):

    _handler_class = bz2.BZ2File if bz2_available else None

    def _extract_name(self, name):
        # see the man page for bzip2
        basename, ext = os.path.splitext(name)
        if ext in ('.bz2', '.bz'):
            return basename
        elif ext in ('.tbz2', '.tbz'):
            return basename + '.tar'
        else:
            return name + '.out'

    def __init__(self, *args, **kwds):
        if not bz2_available:
            raise ImportError("bz2 support is disabled")
        super(BZ2FileArchiveReader, self).__init__(*args, **kwds)
        if not self.isBZ2File(self._archive_name):
            raise TypeError("Unrecognized bzip2 format for file: %s" %
                            (self._archive_name))
