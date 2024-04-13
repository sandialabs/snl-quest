#!/usr/bin/env python

import sys
from optparse import OptionParser
import socket

import pyutilib.pyro
from pyutilib.pyro import Pyro as _pyro


def main():
    parser = OptionParser()
    parser.add_option(
        "--verbose",
        dest="verbose",
        help="Activate verbose output.",
        action="store_true",
        default=False)
    parser.add_option(
        "--max-allowed-connections",
        dest="max_allowed_connections",
        help=("Set the maximum number of proxy connections allowed to "
              "be made to this dispatcher. By default, the environment "
              "variable PYUTILIB_PYRO_MAXCONNECTIONS is used if present; "
              "otherwise, the default settings for Pyro or Pyro4 are used."),
        type="int",
        default=None)
    parser.add_option(
        "--worker-limit",
        dest="worker_limit",
        help=(
            "Set the maximum number of workers allowed to register "
            "with this dispatcher. By default, no limit is enforced. Note that "
            "whether or not this option is set, the maximum number of possible "
            "worker connections might be limited by other default Pyro settings "
            "(see --max-allowed-connections)."),
        type="int",
        default=None)
    parser.add_option(
        "--daemon-host",
        dest="daemon_host",
        metavar="HOST",
        help=("Hostname that the dispatcher daemon should bind on. "
              "The default is the current hostname."),
        default=socket.gethostname())
    parser.add_option(
        "--daemon-port",
        dest="daemon_port",
        metavar="PORT",
        help="Port that the dispatcher daemon should bind on",
        type="int",
        default=0)
    parser.add_option(
        "-n",
        "--host",
        dest="nameserver_host",
        metavar="HOST",
        help="Hostname that the nameserver is bound on",
        default=None)
    parser.add_option(
        "-p",
        "--port",
        dest="nameserver_port",
        metavar="PORT",
        help="Port that the nameserver is bound on",
        type="int",
        default=None)
    parser.add_option(
        "--allow-multiple-dispatchers",
        dest="allow_multiple_dispatchers",
        help="Allow multiple dispatchers to run under the default nameserver group",
        default=False,
        action="store_true")

    options, args = parser.parse_args()
    # Handle the old syntax which was purly argument driven
    # e.g., <nameserver-host> <verbose flag>
    verbose = False
    if len(args) == 2:
        nameserver_host = sys.argv[1]
        if nameserver_host == "None":
            nameserver_host = None
        verbose = bool(sys.argv[2])
        print(
            "DEPRECATION WARNING: dispatch_srvr is now option driven (see dispatch_srvr --help)")
    elif len(args) == 1:
        nameserver_host = sys.argv[1]
        if nameserver_host == "None":
            nameserver_host = None
        print(
            "DEPRECATION WARNING: dispatch_srvr is now option driven (see dispatch_srvr --help)")
    else:
        nameserver_host = options.nameserver_host
        verbose = options.verbose

    if _pyro is None:
        raise ImportError("Pyro or Pyro4 is not available")
    return pyutilib.pyro.DispatcherServer(
        daemon_host=options.daemon_host,
        daemon_port=options.daemon_port,
        nameserver_host=nameserver_host,
        nameserver_port=options.nameserver_port,
        verbose=verbose,
        max_allowed_connections=options.max_allowed_connections,
        worker_limit=options.worker_limit,
        clear_group=not options.allow_multiple_dispatchers)


if __name__ == '__main__':
    main()
