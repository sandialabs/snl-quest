#
# Unit Tests for misc/archivereader
#
#

import os
import fnmatch
import posixpath

import pyutilib.th as unittest

from pyutilib.misc.archivereader import \
    ArchiveReaderFactory, DirArchiveReader, FileArchiveReader, \
    TarArchiveReader, ZipArchiveReader, BZ2FileArchiveReader, \
    GzipFileArchiveReader, tarfile_available, zipfile_available, \
    gzip_available, bz2_available

currdir = os.path.dirname(os.path.abspath(__file__))
testdatadir = os.path.join(currdir, 'archivereader')


class TestArchiveReaderFactory(unittest.TestCase):

    def test_ArchiveReaderFactory_dir(self):
        archive = ArchiveReaderFactory(
            os.path.join(testdatadir, 'archive_flat'))
        self.assertTrue(isinstance(archive, DirArchiveReader))

    @unittest.skipUnless(tarfile_available, "tarfile support is disabled")
    def test_ArchiveReaderFactory_tar(self):
        archive = ArchiveReaderFactory(
            os.path.join(testdatadir, 'archive_flat.tar'))
        self.assertTrue(isinstance(archive, TarArchiveReader))

    @unittest.skipUnless(tarfile_available, "tarfile support is disabled")
    def test_ArchiveReaderFactory_targz(self):
        archive = ArchiveReaderFactory(
            os.path.join(testdatadir, 'archive_flat.tar.gz'))
        self.assertTrue(isinstance(archive, TarArchiveReader))

    @unittest.skipUnless(tarfile_available, "tarfile support is disabled")
    def test_ArchiveReaderFactory_tgz(self):
        archive = ArchiveReaderFactory(
            os.path.join(testdatadir, 'archive_flat.tgz'))
        self.assertTrue(isinstance(archive, TarArchiveReader))

    @unittest.skipUnless(zipfile_available, "zipfile support is disabled")
    def test_ArchiveReaderFactory_zip(self):
        archive = ArchiveReaderFactory(
            os.path.join(testdatadir, 'archive_flat.zip'))
        self.assertTrue(isinstance(archive, ZipArchiveReader))

    def test_ArchiveReaderFactory_file(self):
        archive = ArchiveReaderFactory(os.path.join(testdatadir, 'fileC.txt'))
        self.assertTrue(isinstance(archive, FileArchiveReader))

    @unittest.skipUnless(gzip_available, "gzip support is disabled")
    def test_ArchiveReaderFactory_gzip(self):
        archive = ArchiveReaderFactory(
            os.path.join(testdatadir, 'fileC.txt.gz'))
        self.assertTrue(isinstance(archive, GzipFileArchiveReader))

    @unittest.skipUnless(bz2_available, "bz2 support is disabled")
    def test_ArchiveReaderFactory_bzip2(self):
        archive = ArchiveReaderFactory(
            os.path.join(testdatadir, 'fileC.txt.bz2'))
        self.assertTrue(isinstance(archive, BZ2FileArchiveReader))

    def test_ArchiveReaderFactory_nonexist(self):
        try:
            archive = ArchiveReaderFactory(
                os.path.join(testdatadir, '_does_not_exist_'))
        except IOError:
            pass
        else:
            self.fail(
                "ArchiveReaderFactory should raise exception with nonexistent archive")


class _TestArchiveReaderBaseNested(object):

    archive_class = None
    archive_name = None
    archive_class_kwds = {}

    def setUp(self):
        self._a = None

    def tearDown(self):
        if self._a is not None:
            self._a.close()

    def test_default(self):
        a = self._a = self.archive_class(
            os.path.join(testdatadir, self.archive_name),
            **self.archive_class_kwds)
        tmpdir = a.extract('directory', recursive=True)
        self.assertEqual(os.path.exists(tmpdir), True)
        self.assertEqual(
            os.path.exists(os.path.join(tmpdir, 'fileA.txt')), True)
        self.assertEqual(
            os.path.exists(os.path.join(tmpdir, 'fileB.txt')), True)
        a.clear_extractions()
        self.assertEqual(os.path.exists(tmpdir), False)
        self.assertEqual(
            os.path.exists(os.path.join(tmpdir, 'fileA.txt')), False)
        self.assertEqual(
            os.path.exists(os.path.join(tmpdir, 'fileB.txt')), False)

        tmpdir = a.extract('directory', recursive=True)
        self.assertEqual(os.path.exists(tmpdir), True)
        self.assertEqual(
            os.path.exists(os.path.join(tmpdir, 'fileA.txt')), True)
        self.assertEqual(
            os.path.exists(os.path.join(tmpdir, 'fileB.txt')), True)
        a.clear_extractions()
        self.assertEqual(os.path.exists(tmpdir), False)
        self.assertEqual(
            os.path.exists(os.path.join(tmpdir, 'fileA.txt')), False)
        self.assertEqual(
            os.path.exists(os.path.join(tmpdir, 'fileB.txt')), False)

        tmpnames = a.extractall()
        for name in tmpnames:
            self.assertEqual(os.path.exists(name), True)
        names = [a.normalize_name(name).replace(
            a.normalize_name(a._workdir) + '/', '') for name in tmpnames]
        self.assertEqual(
            sorted(names),
            sorted(['directory', posixpath.join('directory', 'fileA.txt'),
                    posixpath.join('directory', 'fileB.txt')]))
        a.clear_extractions()
        for name in tmpnames:
            self.assertEqual(os.path.exists(name), False)
        self.assertEqual(
            sorted(a.getnames()),
            sorted(['directory', posixpath.join('directory', 'fileA.txt'),
                    posixpath.join('directory', 'fileB.txt')]))
        f = a.open(posixpath.join('directory', 'fileA.txt'))
        try:
            self.assertEqual(f.read().strip().decode(), 'this is fileA')
        finally:
            f.close()
        f = a.open(posixpath.join('directory', 'fileB.txt'))
        try:
            self.assertEqual(f.read().strip().decode(), 'this is fileB')
        finally:
            f.close()
        a.close()

    def test_maxdepth0(self):
        a = self._a = self.archive_class(
            os.path.join(testdatadir, self.archive_name),
            maxdepth=0,
            **self.archive_class_kwds)
        tmpdir = a.extract('directory', recursive=True)
        self.assertEqual(os.path.exists(tmpdir), True)
        self.assertEqual(
            os.path.exists(os.path.join(tmpdir, 'fileA.txt')), False)
        self.assertEqual(
            os.path.exists(os.path.join(tmpdir, 'fileB.txt')), False)
        a.clear_extractions()
        self.assertEqual(os.path.exists(tmpdir), False)
        self.assertEqual(
            os.path.exists(os.path.join(tmpdir, 'fileA.txt')), False)
        self.assertEqual(
            os.path.exists(os.path.join(tmpdir, 'fileB.txt')), False)

        tmpnames = a.extractall()
        for name in tmpnames:
            self.assertEqual(os.path.exists(name), True)
        names = [a.normalize_name(name).replace(
            a.normalize_name(a._workdir) + '/', '') for name in tmpnames]
        self.assertEqual(sorted(names), sorted(['directory']))
        a.clear_extractions()
        for name in tmpnames:
            self.assertEqual(os.path.exists(name), False)

        self.assertEqual(sorted(a.getnames()), sorted(['directory']))
        a.close()

    def test_maxdepth1(self):
        a = self._a = self.archive_class(
            os.path.join(testdatadir, self.archive_name),
            maxdepth=1,
            **self.archive_class_kwds)

        tmpdir = a.extract('directory', recursive=True)
        self.assertEqual(os.path.exists(tmpdir), True)
        self.assertEqual(
            os.path.exists(os.path.join(tmpdir, 'fileA.txt')), True)
        self.assertEqual(
            os.path.exists(os.path.join(tmpdir, 'fileB.txt')), True)
        a.clear_extractions()
        self.assertEqual(os.path.exists(tmpdir), False)
        self.assertEqual(
            os.path.exists(os.path.join(tmpdir, 'fileA.txt')), False)
        self.assertEqual(
            os.path.exists(os.path.join(tmpdir, 'fileB.txt')), False)

        tmpnames = a.extractall()
        for name in tmpnames:
            self.assertEqual(os.path.exists(name), True)
        names = [a.normalize_name(name).replace(
            a.normalize_name(a._workdir) + '/', '') for name in tmpnames]
        self.assertEqual(
            sorted(names),
            sorted(['directory', posixpath.join('directory', 'fileA.txt'),
                    posixpath.join('directory', 'fileB.txt')]))
        a.clear_extractions()
        for name in tmpnames:
            self.assertEqual(os.path.exists(name), False)

        self.assertEqual(
            sorted(a.getnames()),
            sorted(['directory', posixpath.join('directory', 'fileA.txt'),
                    posixpath.join('directory', 'fileB.txt')]))
        f = a.open(posixpath.join('directory', 'fileA.txt'))
        try:
            self.assertEqual(f.read().strip().decode(), 'this is fileA')
        finally:
            f.close()
        f = a.open(posixpath.join('directory', 'fileB.txt'))
        try:
            self.assertEqual(f.read().strip().decode(), 'this is fileB')
        finally:
            f.close()
        a.close()

    def test_subdir_maxdepth0(self):
        a = self._a = self.archive_class(
            os.path.join(testdatadir, self.archive_name),
            subdir='directory',
            maxdepth=0,
            **self.archive_class_kwds)
        tmpnames = a.extractall()
        for name in tmpnames:
            self.assertEqual(os.path.exists(name), True)
        names = [a.normalize_name(name).replace(
            posixpath.join(a.normalize_name(a._workdir), a._subdir), '')
                 for name in tmpnames]
        self.assertEqual(sorted(names), sorted(['fileA.txt', 'fileB.txt']))
        a.clear_extractions()
        for name in tmpnames:
            self.assertEqual(os.path.exists(name), False)
        a.close()
        a = self._a = self.archive_class(
            os.path.join(testdatadir, self.archive_name),
            subdir='directory',
            maxdepth=0,
            **self.archive_class_kwds)
        self.assertEqual(
            sorted(a.getnames()), sorted(['fileA.txt', 'fileB.txt']))
        f = a.open('fileA.txt')
        try:
            self.assertEqual(f.read().strip().decode(), 'this is fileA')
        finally:
            f.close()
        f = a.open('fileB.txt')
        try:
            self.assertEqual(f.read().strip().decode(), 'this is fileB')
        finally:
            f.close()
        a.close()

    def test_subdir_maxdepth1(self):
        a = self._a = self.archive_class(
            os.path.join(testdatadir, self.archive_name),
            subdir='directory',
            maxdepth=1,
            **self.archive_class_kwds)
        tmpnames = a.extractall()
        for name in tmpnames:
            self.assertEqual(os.path.exists(name), True)
        names = [a.normalize_name(name).replace(
            posixpath.join(a.normalize_name(a._workdir), a._subdir), '')
                 for name in tmpnames]
        self.assertEqual(sorted(names), sorted(['fileA.txt', 'fileB.txt']))
        a.clear_extractions()
        for name in tmpnames:
            self.assertEqual(os.path.exists(name), False)

        self.assertEqual(
            sorted(a.getnames()), sorted(['fileA.txt', 'fileB.txt']))
        f = a.open('fileA.txt')
        try:
            self.assertEqual(f.read().strip().decode(), 'this is fileA')
        finally:
            f.close()
        f = a.open('fileB.txt')
        try:
            self.assertEqual(f.read().strip().decode(), 'this is fileB')
        finally:
            f.close()
        a.close()


def dir_svn_junk_filter(x):
    return (fnmatch.fnmatch(x,"*.junk") or \
            fnmatch.fnmatch(x,"*.svn*"))


class TestDirArchiveReader(_TestArchiveReaderBaseNested, unittest.TestCase):

    archive_class = DirArchiveReader
    archive_name = 'archive_directory'
    archive_class_kwds = {'filter': dir_svn_junk_filter}


class TestDirArchiveReaderWin(_TestArchiveReaderBaseNested, unittest.TestCase):

    archive_class = DirArchiveReader
    archive_name = 'win_archive_directory'
    archive_class_kwds = {'filter': dir_svn_junk_filter}


@unittest.skipUnless(tarfile_available, "tarfile support is disabled")
class TestTarArchiveReader1(_TestArchiveReaderBaseNested, unittest.TestCase):

    archive_class = TarArchiveReader
    archive_name = 'archive_directory.tgz'


@unittest.skipUnless(tarfile_available, "tarfile support is disabled")
class TestTarArchiveReader2(_TestArchiveReaderBaseNested, unittest.TestCase):

    archive_class = TarArchiveReader
    archive_name = 'archive_directory.tar.gz'


@unittest.skipUnless(tarfile_available, "tarfile support is disabled")
class TestTarArchiveReader3(_TestArchiveReaderBaseNested, unittest.TestCase):

    archive_class = TarArchiveReader
    archive_name = 'archive_directory.tar'


@unittest.skipUnless(zipfile_available, "zipfile support is disabled")
class TestZipArchiveReader(_TestArchiveReaderBaseNested, unittest.TestCase):

    archive_class = ZipArchiveReader
    archive_name = 'archive_directory.zip'


@unittest.skipUnless(zipfile_available, "zipfile support is disabled")
class TestZipArchiveReaderWin(_TestArchiveReaderBaseNested, unittest.TestCase):

    archive_class = ZipArchiveReader
    archive_name = 'win_archive_directory.zip'


class _TestFileArchiveReaderBase(object):

    archive_class = None
    archive_name = None

    def setUp(self):
        self._a = None

    def tearDown(self):
        if self._a is not None:
            self._a.close()

    def test1(self):
        a = self._a = self.archive_class(
            os.path.join(testdatadir, self.archive_name))
        f = a.open('fileC.txt')
        try:
            self.assertEqual(f.read().strip().decode(), 'this is fileC')
        finally:
            f.close()
        f = a.open()
        try:
            self.assertEqual(f.read().strip().decode(), 'this is fileC')
        finally:
            f.close()
        dst = a.extract()
        self.assertEqual(os.path.exists(dst), True)
        with open(dst, 'rb') as f:
            self.assertEqual(f.read().strip().decode(), 'this is fileC')
        a.clear_extractions()
        self.assertEqual(os.path.exists(dst), False)
        dst = a.extract('fileC.txt')
        self.assertEqual(os.path.exists(dst), True)
        with open(dst, 'rb') as f:
            self.assertEqual(f.read().strip().decode(), 'this is fileC')
        a.clear_extractions()
        self.assertEqual(os.path.exists(dst), False)
        a.close()


@unittest.skipUnless(gzip_available, "gzip support is disabled")
class TestGzipFileArchiveReader(_TestFileArchiveReaderBase, unittest.TestCase):

    archive_class = GzipFileArchiveReader
    archive_name = 'fileC.txt.gz'


@unittest.skipUnless(bz2_available, "bz2 support is disabled")
class TestBZ2FileArchiveReader(_TestFileArchiveReaderBase, unittest.TestCase):

    archive_class = BZ2FileArchiveReader
    archive_name = 'fileC.txt.bz2'


class TestFileArchiveReader(_TestFileArchiveReaderBase, unittest.TestCase):

    archive_class = FileArchiveReader
    archive_name = 'fileC.txt'


if __name__ == "__main__":
    unittest.main()
