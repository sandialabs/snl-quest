from setuptools import setup, find_packages

from quest import __version__

DISTNAME = "Quest"
VERSION = __version__
PYTHON_REQUIRES = ">=3.9, <3.14"
DESCRIPTION = "Sandia National Laboratories Energy Storage Application Platform"
LONG_DESCRIPTION = open("README.md").read()
AUTHOR = "Sandia National Laboratories"
MAINTAINER_EMAIL = "tunguy@sandia.gov"
LICENSE = "BSD 3-clause"
URL = "https://github.com/sandialabs/snl-quest.git"


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
    install_requires=[
        "PySide6==6.8.1",
        "pandas==2.2.1",
        "streamlit==1.55.0",
        "openai==1.86.0",
        "psutil==5.9.0",
        "GitPython==3.1.43",
        'NodeGraphQt @ git+https://github.com/cancom84/NodeGraphQt-PySide6.git',
        "notebook==7.5.5",
        "nbformat==5.10.4"
    ],

    package_data={
        '': ['*.txt', '*.rst', '*.json', '*.jpg', '*.qss', '*.sh', '*.svg', '*.png', '*.kv', '*.bat', '*.csv', '*.md', '*.yml', '*.dll', '*.idf', '*.doctree', '.*info', '*.html', '*.js', '*.inv', '*.gif', '*.css', '*.eps', '*.pickle', '*.xlsx', '*.ttf', '*.pdf', '**/license*', '*.yml', '*.ui', '*.eot', '*.woff', '*.woff2', 'LICENSE', '*.mplstyle', '*.ini' ],
    },

    entry_points={
        'console_scripts': [
            'quest = quest.__main__:main'
        ]
    }
)
