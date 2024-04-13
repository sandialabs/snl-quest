
"""The following code is required to make the dependency binaries available to
kivy when it imports this package.
"""

import sys
import os
from os.path import join, isdir, dirname
import site

__all__ = ('dep_bins', )

__version__ = '0.3.3'



dep_bins = []
"""A list of paths that contain the binaries of this distribution.
Can be used e.g. with pyinstaller to ensure it copies all the binaries.
"""

for d in [sys.prefix, site.USER_BASE]:
    p = join(d, 'share', 'angle', 'bin')
    if isdir(p):
        os.environ["PATH"] = p + os.pathsep + os.environ["PATH"]
        if hasattr(os, 'add_dll_directory'):
            os.add_dll_directory(p)
        dep_bins.append(p)


