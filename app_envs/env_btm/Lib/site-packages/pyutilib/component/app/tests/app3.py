import pyutilib.component.app
import os
import sys

currdir = sys.argv[-1] + os.sep

app = pyutilib.component.app.SimpleApplication("foo")
app.config.load(currdir + "log1.ini")
app.logger.log_dir = currdir
app.logger.log_file = "app3.log"
app.logger.reset_after_updates()
app.env.load_services()
app.log("test_app3 message")
app.flush()
