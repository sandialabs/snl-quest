#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________
"""A plugin that supports global configuration of logging options for pyutilib.component.core."""

import sys
import os.path
import logging
import logging.handlers as handlers

from pyutilib.component.core import Plugin, implements, ExtensionPoint, PluginGlobals
from pyutilib.component.config.env_config import IEnvironmentConfig
from pyutilib.component.config.options import IUpdatedOptionsAction, declare_option


class LoggingConfig(Plugin):
    """A plugin that supports global configuration of logging options."""

    implements(IUpdatedOptionsAction)

    def __init__(self, namespace):
        """Initialize logging information for a specified namespace"""
        self._hdlr = None
        self.namespace = namespace
        self.env_plugins = ExtensionPoint(IEnvironmentConfig)
        if self.namespace == "":
            section = "logging"
            section_re = None
        else:
            section = "logging." + namespace
            section_re = "^logging$"
        #
        declare_option(
            "timestamp",
            section=section,
            section_re=section_re,
            default=False,
            doc="""Add timestamp to logging information.""")
        #
        declare_option(
            "log_dir",
            section=section,
            section_re=section_re,
            default=None,
            doc="""The logging directory.

        The default directory is the application directory plus 'log'.""")
        #
        declare_option(
            "log_type",
            section=section,
            section_re=section_re,
            default='none',
            doc="""Logging facility to use.

        Should be one of (`none`, `file`, `stderr`, `syslog`, `winlog`).""")
        #
        declare_option(
            "log_file",
            section=section,
            section_re=section_re,
            default=namespace + '.log',
            doc="""If `log_type` is `file`, this should be a path to the log-file.""")
        #
        declare_option(
            "log_level",
            section=section,
            section_re=section_re,
            default='WARN',
            doc="""Level of verbosity in log.

        Should be one of (`CRITICAL`, `ERROR`, `WARN`, `INFO`, `DEBUG`).""")
        #
        declare_option(
            "log_format",
            section=section,
            section_re=section_re,
            default=None,
            doc="""Custom logging format.

        If nothing is set, the following will be used:

        $(project)[$(env) $(module)] $(levelname): $(message)

        In addition to regular key names supported by the Python logger library
        library (see http://docs.python.org/lib/node422.html), one could use:
         - $(path)s     the path for the current environment
         - $(basename)s the last path component of the current environment
         - $(app)s      the name of the current application

        Note the usage of `$(...)s` instead of `%(...)s` as the latter form
        would be interpreted by the ConfigParser itself.
        """)

    def reset_after_updates(self):
        """
        Configure the pyutilib.component logging facility.  This will
        implicitly configure all of the environment-specific logging
        objects.
        """
        sys.stdout.flush()
        logger = logging.getLogger('pyutilib.component.core.' + self.namespace)
        if not self._hdlr is None:
            logger.removeHandler(self._hdlr)
        #
        # Set logging level
        #
        level = self.log_level
        level = level.upper()
        if level in ('DEBUG', 'ALL'):
            logger.setLevel(logging.DEBUG)
        elif level == 'INFO':
            logger.setLevel(logging.INFO)
        elif level == 'ERROR':
            logger.setLevel(logging.ERROR)
        elif level == 'CRITICAL':
            logger.setLevel(logging.CRITICAL)
        else:
            logger.setLevel(logging.WARNING)
        #
        # Initialize the current path.  Is there a rule to use for whic
        # environment will be used???  In practice, there is likely to be
        # only one environment.
        #
        if self.log_dir is None:
            path = None
            for plugin in self.env_plugins:
                (flag, count) = plugin.matches(self.namespace)
                tmp = plugin.get_option("path")
                if flag and not tmp is None:
                    path = tmp
                    break
            if path is None:
                path = os.getcwd()
        else:
            path = self.log_dir
        #
        # Setup the logging file
        #
        logtype = self.log_type.lower()
        if self.log_file is None:
            logfile = os.path.join(path, 'log')
        else:
            logfile = self.log_file
            if not os.path.isabs(logfile):
                logfile = os.path.join(path, logfile)
        #
        # Define the format
        #
        format = self.log_format
        if format is None:
            format = '[env=%(env)s where=%(module)s] %(levelname)s - %(message)s'
            if self.timestamp and logtype in ('file', 'stderr'):
                format = '%(asctime)s ' + format
            format = format.replace('$(', '%(') \
                    .replace('%(env)s', PluginGlobals.get_env().name)
        datefmt = ''
        if self.timestamp and self.log_type == 'stderr':
            datefmt = '%X'
        formatter = logging.Formatter(format, datefmt)
        #
        #  Define the handler
        #
        if logtype == 'file':
            hdlr = logging.FileHandler(logfile)
        elif logtype in ('winlog', 'eventlog', 'nteventlog'):
            # Requires win32 extensions
            hdlr = handlers.NTEventLogHandler(logid, logtype='Application')
        elif logtype in ('syslog', 'unix'):
            hdlr = handlers.SysLogHandler('/dev/log')
        elif logtype in ('stderr'):
            hdlr = logging.StreamHandler(sys.stderr)
        else:
            hdlr = handlers.BufferingHandler(0)
            # Note: this _really_ throws away log events, as a `MemoryHandler`
            # would keep _all_ records in case there's no target handler (a bug?)
        self._hdlr = hdlr
        self._logtype = logtype
        self._logfile = logfile
        hdlr.setFormatter(formatter)
        logger.addHandler(hdlr)
        self._log = logger

    def flush(self):
        """Flush logging I/O"""
        self._hdlr.flush()

    def shutdown(self):
        #
        # Q: should this shutdown _all_ logging?
        #
        logging.shutdown()

    def log(self, message):
        self._log.info(message)
