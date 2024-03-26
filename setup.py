# -*- coding: utf-8 -*-
from cx_Freeze import setup, Executable

with open('requirements.txt') as f:
    required_packages = f.read().splitlines()
    
include_dirs = [
    'app_envs',
    'data',
    'docs',
    'images',
    'licenses',
    'plots',
    'snl_libraries',
    'themes'
]

setup(
      name="Quest",
      version='2.0',
      description="An Energy Storage Application Platform",

      options={
          'build_exe':{
#              'packages': required_packages,
              'packages': ['PySide6', 'langchain', 'lida', 'llmx', 'pandas', 'numpy', 'tabulate'],
              'include_files': [(directory, directory) for directory in include_dirs],

              },
          },
      executables=[Executable("main.py", base="Console")],
      )