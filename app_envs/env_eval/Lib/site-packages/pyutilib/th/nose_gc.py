"""This module defines a nose plugin to forceably run the Python garbage collector before and after every test.

Use the following command-line option with nosetests ::

    nosetests --with-forced-gc

"""

from gc import collect
from nose.plugins.base import Plugin


class ForcedGC(Plugin):
    """Force calls to the Python garbage collector before and after each test."""
    name = 'forced-gc'
    score = 5000  # Run early

    def beforeTest(self, test):
        collect()

    def afterTest(self, test):
        collect()
