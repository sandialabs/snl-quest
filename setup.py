from setuptools import setup, find_packages
from distutils.core import Extension

DISTNAME = 'QuESt'
VERSION = '1.1'
EXTENSIONS = []
PYTHON_REQUIRES='>=36'
DESCRIPTION = 'Sandia National Laboratories application suite for energy storage analysis and evaluation tools.'
LONG_DESCRIPTION = open('README.md').read()
AUTHOR = 'Sandia National Laboratories'
MAINTAINER_EMAIL = 'rconcep@sandia.gov'
LICENSE = 'BSD 3-clause'
URL = 'https://www.github.com/rconcep/snl-quest'

setuptools_kwargs = {
    'scripts': [],
    'include_package_data': True,
    'install_requires' : ['numpy', 'scipy', 'pandas>=0.23.4',
                          'pyomo>=5.3', 'matplotlib',
                          'kivy>=1.10.1', 'kivy-garden',
                          'xlrd', 'six',
                          'jinja2',
                          'bs4', 'requests', 'urllib3']
}

setup(name=DISTNAME,
      version=VERSION,
      packages=find_packages(),
      ext_modules=EXTENSIONS,
      python_requires=PYTHON_REQUIRES,
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      author=AUTHOR,
      maintainer_email=MAINTAINER_EMAIL,
      license=LICENSE,
      url=URL,
      **setuptools_kwargs)