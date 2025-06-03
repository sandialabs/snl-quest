from setuptools import setup, find_packages

DISTNAME = "QuESt Data Manager"
VERSION = "1.6"
EXTENSIONS = []
PYTHON_REQUIRES = ">=3.6"
DESCRIPTION = "Sandia National Laboratories application suite for energy storage analysis and evaluation tools."
LONG_DESCRIPTION = open("README.md").read()
AUTHOR = "Sandia National Laboratories"
MAINTAINER_EMAIL = "tunguy@sandia.gov"
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
        "kivy==2.1.0",
        "scipy==1.12.0",
        "pandas==2.2.1",
        "pyomo==6.7.1",
        "matplotlib==3.7.4",
        "kivy-garden==0.1.5",
        "xlrd==2.0.1",
        "six==1.16.0",
        "jinja2==3.1.3",
        "bs4==0.0.2",
        "requests==2.31.0",
        "urllib3==2.2.1",
        "seaborn==0.13.2",
        "eppy==0.5.63",
        "openpyxl==3.1.2",
        "pyutilib==6.0.0",
        "holidays==0.43",
        "scikit-glpk==0.5.0",
    ],

    package_data={
        '': ['*.txt', '*.rst', '*.json', '*.jpg', '*.qss', '*.svg', '*.png', '*.kv', '*.bat', '*.csv', '*.md', '*.yml', '*.idf', '*.doctree', '.*info', '*.html', '*.js', '*.inv', '*.gif', '*.css', '*.eps', '*.pickle', '*.xlsx', '*.ttf', '*.pdf', '**/license*', '*.yml', '*.ui', '*.eot', '*.woff', '*.woff2', 'LICENSE', '*.mplstyle', '*.ini' ],
    },
    
    entry_points={
        'console_scripts': [
            'data_manager = data_manager.__main__:main'
        ]
    }
)
