from pathlib import Path

from setuptools import find_packages, setup


ROOT = Path(__file__).parent
from quest import __version__

DISTNAME = "Quest"
VERSION = __version__
PYTHON_REQUIRES = ">=3.9, <3.14"
DESCRIPTION = "Sandia National Laboratories Energy Storage Application Platform"
LONG_DESCRIPTION = open("README.md").read()
LONG_DESCRIPTION_CONTENT_TYPE = "text/markdown"
AUTHOR = "Sandia National Laboratories"
MAINTAINER_EMAIL = "tunguy@sandia.gov"
LICENSE = "BSD 3-clause"
URL = "https://github.com/sandialabs/snl-quest.git"


setup(
    name=DISTNAME,
    version=VERSION,
    packages=[
        "quest",
        "quest.app",
        "quest.app.ui",
        "quest.app.tools",
        "quest.app.home_page",
        "quest.app.updates",
        "quest.app.splash_screen",
        "quest.app.about_pages",
        "quest.app.data_vis",
        "quest.app.ui_tools",
        "quest.app.tools.reqs",
        "quest.app.tools.script_files",
        "quest.app.tools.env_delete",
        "quest.app.home_page.ui",
        "quest.app.splash_screen.ui",
        "quest.app.about_pages.ui",
        "quest.app.data_vis.ui",
        "quest.app.ui_tools.ui",
        "quest.themes",
        "quest.licenses",
        "quest.snl_libraries",
        "quest.snl_libraries.gpt",
        "quest.snl_libraries.gpt.data",
        "quest.snl_libraries.gpt.data.graphs",
        "quest.snl_libraries.workspace",
        "quest.snl_libraries.workspace.nodes",
        "quest.snl_libraries.workspace.flow",
    ],
    package_data={
        "quest": [
            "version.txt",
            "images/**/*",
            ".streamlit/config.toml",
        ],
        "quest.app.home_page": ["*.json"],
        "quest.themes": ["*.qss", "empty"],
        "quest.app.tools": ["*", "**/*"],
        "quest.app.tools.script_files": ["*"],
        "quest.app.tools.reqs": ["*"],
    },
    include_package_data=False,
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
    long_description_content_type=LONG_DESCRIPTION_CONTENT_TYPE,
    author=AUTHOR,
    maintainer_email=MAINTAINER_EMAIL,
    license=LICENSE,
    url=URL,
    install_requires=[
        "PySide6==6.8.1",
        "pandas>=2.2.3,<2.3",
        "streamlit==1.55.0",
        "openai==1.86.0",
        "psutil==5.9.0",
        "GitPython==3.1.43",
        # 'NodeGraphQt @ git+https://github.com/cancom84/NodeGraphQt-PySide6.git',
        "notebook==7.5.5",
        "nbformat==5.10.4",
    ],
    # package_data={
    #     "": [
    #         "*.txt",
    #         "*.rst",
    #         "*.json",
    #         "*.jpg",
    #         "*.qss",
    #         "*.sh",
    #         "*.svg",
    #         "*.png",
    #         "*.kv",
    #         "*.bat",
    #         "*.csv",
    #         "*.md",
    #         "*.yml",
    #         "*.dll",
    #         "*.idf",
    #         "*.doctree",
    #         ".*info",
    #         "*.html",
    #         "*.js",
    #         "*.inv",
    #         "*.gif",
    #         "*.css",
    #         "*.eps",
    #         "*.pickle",
    #         "*.xlsx",
    #         "*.ttf",
    #         "*.pdf",
    #         "**/license*",
    #         "*.yml",
    #         "*.ui",
    #         "*.eot",
    #         "*.woff",
    #         "*.woff2",
    #         "LICENSE",
    #         "*.mplstyle",
    #         "*.ini",
    #     ],
    # },
    entry_points={"console_scripts": ["quest = quest.__main__:main"]},
)
