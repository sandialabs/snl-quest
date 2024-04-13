
"""The following code is required to make the dependency binaries available to
kivy when it imports this package.
"""

import sys
import os
from os.path import join, isdir, dirname

__all__ = ('dep_bins', )

__version__ = '0.3.1'



dep_bins = []
"""A list of paths that contain the binaries of this distribution.
Can be used e.g. with pyinstaller to ensure it copies all the binaries.
"""

_root = sys.prefix
dep_bins = [join(_root, 'share', 'sdl2', 'bin')]
if isdir(dep_bins[0]):
    os.environ["PATH"] = dep_bins[0] + os.pathsep + os.environ["PATH"]
    if hasattr(os, 'add_dll_directory'):
        os.add_dll_directory(dep_bins[0])
else:
    dep_bins = []


