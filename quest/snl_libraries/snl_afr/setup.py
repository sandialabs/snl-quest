from setuptools import setup, find_packages

DISTNAME = "QuESt Analysis for Regulators"
VERSION = "1.0"
EXTENSIONS = []
PYTHON_REQUIRES = ">=3.6"
DESCRIPTION = "Sandia National Laboratories analysis for regulators tool."
LONG_DESCRIPTION = open("README.md").read()
AUTHOR = "Sandia National Laboratories"
MAINTAINER_EMAIL = "wolis@sandia.gov"
LICENSE = "BSD 3-clause"
URL = "https://www.github.com/snl-quest/snl-quest"

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
    install_requires=[
        "contourpy==1.2.1",
        "cycler==0.12.1",
        "fonttools==4.53.1",
        "importlib_resources==6.4.1",
        "kiwisolver==1.4.5",
        "nose==1.3.7",
        "numpy==1.26.4",
        "packaging==24.1",
        "pandas==2.2.2",
        "pillow==10.4.0",
        "plotly==5.22.0",
        "ply==3.11",
        "Pyomo==6.7.2",
        "pyparsing==3.1.2",
        "PySide6==6.5.2",
        "PySide6-Addons==6.5.2",
        "PySide6-Essentials==6.5.2",
        "python-dateutil==2.9.0.post0",
        "pytz==2024.1",
        "PyUtilib==6.0.0",
        "shiboken6==6.5.2",
        "six==1.16.0",
        "tenacity==9.0.0",
        "tzdata==2024.1",
        "zipp==3.19.2",

    ],

    package_data={
        '': ['*.txt', '*.rst', '*.json', '*.jpg', '*.qss', '*.sh', '*.svg', '*.png', '*.kv', '*.bat', '*.csv', '*.md', '*.yml', '*.idf', '*.doctree', '.*info', '*.html', '*.js', '*.inv', '*.gif', '*.css', '*.eps', '*.pickle', '*.xlsx', '*.ttf', '*.pdf', '**/license*', '*.yml', '*.ui', '*.eot', '*.woff', '*.woff2', 'LICENSE', '*.mplstyle', '*.ini' ],
    },
    
    entry_points={
        'console_scripts': [
            'afr = afr.__main__:main'
        ]
    }
)
