from setuptools import setup, find_packages

DISTNAME = "Quest"
VERSION = "2.0"
PYTHON_REQUIRES = ">=3.6, <3.11"
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
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    author=AUTHOR,
    maintainer_email=MAINTAINER_EMAIL,
    license=LICENSE,
    url=URL,
    install_requires=[
        "PySide6==6.5.2",
        "pandas==2.2.1",
        "streamlit==1.32.0",
        "openai==1.86.0",
        "configparser==6.0.1",
        "matplotlib==3.8.3",
        "geopandas==0.14.3",
        "psutil==5.9.0",
        "GitPython==3.1.43",
        'NodeGraphQt @ git+https://github.com/cancom84/NodeGraphQt-PySide6.git'
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
