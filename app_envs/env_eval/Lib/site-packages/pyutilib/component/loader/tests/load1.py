import pyutilib.misc
import pyutilib.component.core
import os
import sys
import logging

currdir = sys.argv[-2] + os.sep

logging.basicConfig(level=logging.DEBUG)
pyutilib.component.core.PluginGlobals.get_env().load_services(
    path=currdir + "plugins1")
pyutilib.misc.setup_redirect(currdir + "load1.out")
if sys.argv[-1] == "json":
    pyutilib.component.core.PluginGlobals.pprint(json=True)
else:
    pyutilib.component.core.PluginGlobals.pprint()
pyutilib.misc.reset_redirect()
