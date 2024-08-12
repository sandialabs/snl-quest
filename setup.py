from setuptools import setup, find_packages

DISTNAME = "Quest"
VERSION = "2.0"
PYTHON_REQUIRES = ">=3.6"
DESCRIPTION = "Sandia National Laboratories Energy Storage Application Platform"
LONG_DESCRIPTION = open("README.md").read()
AUTHOR = "Sandia National Laboratories"
MAINTAINER_EMAIL = "tunguy@sandia.gov"
LICENSE = "BSD 3-clause"
URL = "https://github.com/sandialabs/snl-quest.git"

setuptools_kwargs = {
    "scripts": [],
    "include_package_data": True,
    "install_requires": [
        "PySide6==6.5.2",
        "pandas==2.2.1",
        "streamlit==1.37.0",
        "openai==0.28.1",
        "configparser==6.0.1",
        "matplotlib==3.8.3",
        "geopandas==0.14.3",
        "psutil==5.9.0",
        'NodeGraphQt @ git+https://github.com/C3RV1/NodeGraphQt-PySide6'
    ]
}

setup(
    name=DISTNAME,
    version=VERSION,
    packages=find_packages(),
    python_requires=PYTHON_REQUIRES,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    author=AUTHOR,
    maintainer_email=MAINTAINER_EMAIL,
    license=LICENSE,
    url=URL,
    **setuptools_kwargs
)
