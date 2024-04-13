# This file is imported from __init__.py and exec'd from setup.py

MAJOR = 2
MINOR = 0
MICRO = 0
RELEASE = True

__version__ = '%d.%d.%d' % (MAJOR, MINOR, MICRO)

if not RELEASE:
    # if it's a rcx release, it's not proceeded by a period. If it is a
    # devx release, it must start with a period
    __version__ += 'rc4'


_kivy_git_hash = 'dedcb6bcabe3d8d6758dcee607e8c33b174d782b'
_kivy_build_date = '20201209'

