# This file is imported from __init__.py and exec'd from setup.py

MAJOR = 2
MINOR = 1
MICRO = 0
RELEASE = True

__version__ = '%d.%d.%d' % (MAJOR, MINOR, MICRO)

if not RELEASE:
    # if it's a rcx release, it's not proceeded by a period. If it is a
    # devx release, it must start with a period
    __version__ += ''


_kivy_git_hash = '023bd79b90f9831b45bb8eb449346648aa5fe5f8'
_kivy_build_date = '20220306'

