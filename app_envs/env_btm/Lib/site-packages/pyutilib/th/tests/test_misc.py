import os
from os.path import abspath, dirname
currdir = dirname(abspath(__file__)) + os.sep

import pyutilib.th as unittest


class Tester(unittest.TestCase):

    def test1(self):
        self.assertFileEqualsBaseline(
            currdir + 'file1.txt', currdir + 'file1.txt', delete=False)
        self.assertFileEqualsBaseline(
            currdir + 'file2.txt', currdir + 'file2.txt', delete=False)

    @unittest.expectedFailure
    def test2(self):
        self.assertFileEqualsBaseline(
            currdir + 'file1.txt', currdir + 'file2.txt', delete=False)

    def test3(self):
        self.assertFileEqualsBaseline(
            currdir + 'file1.txt', currdir + 'file1.zip', delete=False)
        self.assertFileEqualsBaseline(
            currdir + 'file1.zip', currdir + 'file1.txt', delete=False)
        self.assertFileEqualsBaseline(
            currdir + 'file1.zip', currdir + 'file1.zip', delete=False)
        self.assertFileEqualsBaseline(
            currdir + 'file2.txt', currdir + 'file2.zip', delete=False)
        self.assertFileEqualsBaseline(
            currdir + 'file2.zip', currdir + 'file2.txt', delete=False)
        self.assertFileEqualsBaseline(
            currdir + 'file2.zip', currdir + 'file2.zip', delete=False)

    def test3gz(self):
        self.assertFileEqualsBaseline(
            currdir + 'file1.txt', currdir + 'file1.txt.gz', delete=False)
        self.assertFileEqualsBaseline(
            currdir + 'file1.txt.gz', currdir + 'file1.txt', delete=False)
        self.assertFileEqualsBaseline(
            currdir + 'file1.txt.gz', currdir + 'file1.txt.gz', delete=False)
        self.assertFileEqualsBaseline(
            currdir + 'file2.txt', currdir + 'file2.txt.gz', delete=False)
        self.assertFileEqualsBaseline(
            currdir + 'file2.txt.gz', currdir + 'file2.txt', delete=False)
        self.assertFileEqualsBaseline(
            currdir + 'file2.txt.gz', currdir + 'file2.txt.gz', delete=False)

    @unittest.expectedFailure
    def test4(self):
        self.assertFileEqualsBaseline(
            currdir + 'file1.txt', currdir + 'file3.zip', delete=False)

    @unittest.expectedFailure
    def test5(self):
        self.assertFileEqualsBaseline(
            currdir + 'file3.zip', currdir + 'file1.txt', delete=False)

    @unittest.expectedFailure
    def test6(self):
        self.assertFileEqualsBaseline(
            currdir + 'file1.zip', currdir + 'file3.txt', delete=False)

    @unittest.expectedFailure
    def test7(self):
        self.assertFileEqualsBaseline(
            currdir + 'file3.zip', currdir + 'file3.zip', delete=False)

    @unittest.expectedFailure
    def test8(self):
        self.assertFileEqualsBaseline(
            currdir + 'file1.zip', currdir + 'file2.zip', delete=False)

    @unittest.expectedFailure
    def test8gz(self):
        self.assertFileEqualsBaseline(
            currdir + 'file1.txt.gz', currdir + 'file2.txt.gz', delete=False)



class TesterL(unittest.TestCase):

    def test1(self):
        self.assertFileEqualsLargeBaseline(
            currdir + 'file1.txt', currdir + 'file1.txt', delete=False)
        self.assertFileEqualsLargeBaseline(
            currdir + 'file2.txt', currdir + 'file2.txt', delete=False)

    @unittest.expectedFailure
    def test2(self):
        self.assertFileEqualsLargeBaseline(
            currdir + 'file1.txt', currdir + 'file2.txt', delete=False)

    def test3(self):
        self.assertFileEqualsLargeBaseline(
            currdir + 'file1.txt', currdir + 'file1.zip', delete=False)
        self.assertFileEqualsLargeBaseline(
            currdir + 'file1.zip', currdir + 'file1.txt', delete=False)
        self.assertFileEqualsLargeBaseline(
            currdir + 'file1.zip', currdir + 'file1.zip', delete=False)
        self.assertFileEqualsLargeBaseline(
            currdir + 'file2.txt', currdir + 'file2.zip', delete=False)
        self.assertFileEqualsLargeBaseline(
            currdir + 'file2.zip', currdir + 'file2.txt', delete=False)
        self.assertFileEqualsLargeBaseline(
            currdir + 'file2.zip', currdir + 'file2.zip', delete=False)

    def test3gz(self):
        self.assertFileEqualsLargeBaseline(
            currdir + 'file1.txt', currdir + 'file1.txt.gz', delete=False)
        self.assertFileEqualsLargeBaseline(
            currdir + 'file1.txt.gz', currdir + 'file1.txt', delete=False)
        self.assertFileEqualsLargeBaseline(
            currdir + 'file1.txt.gz', currdir + 'file1.txt.gz', delete=False)
        self.assertFileEqualsLargeBaseline(
            currdir + 'file2.txt', currdir + 'file2.txt.gz', delete=False)
        self.assertFileEqualsLargeBaseline(
            currdir + 'file2.txt.gz', currdir + 'file2.txt', delete=False)
        self.assertFileEqualsLargeBaseline(
            currdir + 'file2.txt.gz', currdir + 'file2.txt.gz', delete=False)

    @unittest.expectedFailure
    def test4(self):
        self.assertFileEqualsLargeBaseline(
            currdir + 'file1.txt', currdir + 'file3.zip', delete=False)

    @unittest.expectedFailure
    def test5(self):
        self.assertFileEqualsLargeBaseline(
            currdir + 'file3.zip', currdir + 'file1.txt', delete=False)

    @unittest.expectedFailure
    def test6(self):
        self.assertFileEqualsLargeBaseline(
            currdir + 'file1.zip', currdir + 'file3.txt', delete=False)

    @unittest.expectedFailure
    def test7(self):
        self.assertFileEqualsLargeBaseline(
            currdir + 'file3.zip', currdir + 'file3.zip', delete=False)

    @unittest.expectedFailure
    def test8(self):
        self.assertFileEqualsLargeBaseline(
            currdir + 'file1.zip', currdir + 'file2.zip', delete=False)

    @unittest.expectedFailure
    def test8gz(self):
        self.assertFileEqualsLargeBaseline(
            currdir + 'file1.txt.gz', currdir + 'file2.txt.gz', delete=False)


if __name__ == "__main__":
    unittest.main()
