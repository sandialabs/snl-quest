import pyutilib.misc
import pyutilib.component.core
import os
import sys

currdir = sys.argv[-2] + os.sep

pyutilib.component.core.PluginGlobals.get_env().load_services(
    path=[currdir + "plugins1", currdir + "plugins2"], auto_disable=True)
pyutilib.misc.setup_redirect(currdir + "load2a.out")
if sys.argv[-1] == "json":
    pyutilib.component.core.PluginGlobals.pprint(json=True)
else:
    pyutilib.component.core.PluginGlobals.pprint()
pyutilib.misc.reset_redirect()
