import sys
import time
# Write ERR first so that the output is deterministic
sys.stderr.write("Tee Script: ERR\n")
sys.stdout.write("Tee Script: OUT\n")
# sleep just enough so that the STDERR thread should finish flushing its
# buffer before the process terminates (at which point the order in
# which the buffers are flushed is somewhat random).
time.sleep(0.5)
