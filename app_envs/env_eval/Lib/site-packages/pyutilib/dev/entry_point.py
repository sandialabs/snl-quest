#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________

import sys
from pyutilib.subprocess import run

def run_entry_point(package, script, args=[], **kwds):
    """Run the named entry point script from the specified package

    Args:
        package (str): The name of the Python package
        script (str): The name of the entry point script to run
        args (list): The list of command line arguments to pass the script
        **kwds: Any additional arguments to pass to pyutilib.subprocess.run
    """
    package = str(package)
    script = str(script)
    assert type(args) is list
    cmdLine \
        = "import pkg_resources,sys; "\
        "sys.argv=%r; "\
        "sys.exit(pkg_resources.load_entry_point(%r,'console_scripts',%r)())" \
        % ( [script]+args, package, script ) 
    run([sys.executable, '-c', cmdLine], **kwds)
