from setuptools import setup, find_packages
from cx_Freeze import setup, Executable

DISTNAME = "Quest"
VERSION = "2.0"
PYTHON_REQUIRES = ">=3.6"
DESCRIPTION = "Sandia National Laboratories Energy Storage Application Platform"
LONG_DESCRIPTION = open("README.md").read()
AUTHOR = "Sandia National Laboratories"
MAINTAINER_EMAIL = "tunguy@sandia.gov"
LICENSE = "BSD 3-clause"
URL = "https://github.com/sandialabs/snl-quest.git"

options = {
    'build_exe': {
        'packages': [
            "PySide6",
            "pandas",
            "streamlit",
            "openai",
            "configparser",
            "matplotlib",
            "geopandas",
            "psutil",
            "NodeGraphQt"
        ],
        'include_files': [
            ("README.md", "README.md"),
            ("LICENSE", "LICENSE"),
            ("quest", "quest")
        ],
    },
}

base = None
executables = [Executable("quest/__main__.py", base=base)]

setup(
    name=DISTNAME,
    version=VERSION,
    packages=find_packages(),
    include_package_data=True,
    python_requires=PYTHON_REQUIRES,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    author=AUTHOR,
    maintainer_email=MAINTAINER_EMAIL,
    license=LICENSE,
    url=URL,
    executables=executables,
    options=options
)
