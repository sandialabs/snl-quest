import os
import sys
import pyutilib.component.app

currdir = sys.argv[-1] + os.sep

app = pyutilib.component.app.SimpleApplication("foo")
app.config.load(currdir + "log1.ini")
#print type(app.logger.log_dir)
app.logger.log_dir = currdir
#print type(app.logger.log_dir)
app.config.save(currdir + "tmp2.ini")
