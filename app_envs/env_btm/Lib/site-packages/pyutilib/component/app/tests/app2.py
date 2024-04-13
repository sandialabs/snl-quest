import pyutilib.component.app
import pyutilib.misc
import os
import sys

currdir = sys.argv[-1] + os.sep

app = pyutilib.component.app.SimpleApplication("foo")
pyutilib.misc.setup_redirect(currdir + "summary.out")
app.config.summarize()
pyutilib.misc.reset_redirect()
