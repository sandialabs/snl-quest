"""This module defines a nose plugin to terminate a test after a
specified number of seconds.

Use the following command-line option with nosetests ::

    nosetests --test-timeout=###

"""

__all__ = ['Timeout', 'TestTimeout']

import os
import signal
from nose.plugins.base import Plugin
try:
    from psutil import Process
    _psutil_avail = True
except ImportError:
    _psutil_avail = False
except NotImplementedError:
    _psutil_avail = False


class Timeout(Exception):
    pass


class TestTimeout(Plugin):
    """Kill tests if they exceed the specified timeout."""
    name = 'timeout'
    score = 5000  # Run early

    def options(self, parser, env):
        """Register command-line options."""
        parser.add_option(
            "--test-timeout",
            action="store",
            default=env.get('NOSE_TEST_TIMEOUT', 0),
            dest="test_timeout",
            metavar="SECONDS",
            help="A per-test timeout (in seconds). "
            "[NOSE_TEST_TIMEOUT]")

    def configure(self, options, config):
        self.timeout = int(options.test_timeout)
        self.enabled = self.timeout > 0
        if self.enabled and not _psutil_avail:
            self.enabled = False
            raise ImportError(
                "The nose Timeout plugin requires the psutil package.")

    def startTest(self, test):
        signal.signal(signal.SIGALRM, self._killTest)
        signal.alarm(self.timeout)

    def stopTest(self, test):
        signal.alarm(0)

    def _all_children(self, p):
        ans = p.get_children()
        i = 0
        while i < len(ans):
            ans.extend(self._all_children(ans[i]))
            i += 1
        return ans

    def _killTest(self, signum, frame):
        for p in self._all_children(Process(os.getpid())):
            try:
                p.kill()
            except:
                pass
        hour = int(self.timeout / 3600)
        min = int(self.timeout / 60) - hour * 60
        sec = self.timeout % 60
        txt = ""
        if hour:
            txt = "%d hour%s" % (hour, hour > 1 and "s" or "")
        if min:
            if txt:
                txt += ", "
            txt += "%d minute%s" % (min, min > 1 and "s" or "")
        if sec:
            if txt:
                txt += ", "
            txt += "%d second%s" % (sec, sec > 1 and "s" or "")
        raise Timeout("Test exceeded timeout (%s)" % txt)
