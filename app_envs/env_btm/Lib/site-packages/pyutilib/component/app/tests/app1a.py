import pyutilib.component.app
import os
import sys

currdir = sys.argv[-1] + os.sep

app = pyutilib.component.app.SimpleApplication("foo")
app._env_config.options.path = "DEFAULT PATH HERE"
app.config.save(currdir + "config1.out")
