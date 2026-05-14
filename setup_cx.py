from setuptools import setup, find_packages
from cx_Freeze import setup, Executable

DISTNAME = "Quest"
VERSION = "2.1.0"
PYTHON_REQUIRES = ">=3.9, <3.14"
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
            "psutil",
            "NodeGraphQt",
            "notebook",
            "nbformat"
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
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    author=AUTHOR,
    maintainer_email=MAINTAINER_EMAIL,
    license=LICENSE,
    url=URL,
    executables=executables,
    options=options
)
