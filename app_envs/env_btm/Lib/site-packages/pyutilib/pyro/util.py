#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________

__all__ = ('get_nameserver', 'get_dispatchers', 'shutdown_pyro_components')

import os
import sys
import time
import random
import socket

# For now, default to using Pyro3 if available
# otherwise, check for Pyro4
Pyro = None
using_pyro3 = False
using_pyro4 = False
try:
    import Pyro
    import Pyro.core
    import Pyro.naming
    using_pyro3 = True
    using_pyro4 = False
except:
    try:
        import Pyro4
        import Pyro4.naming
        #Pyro4.config.SERIALIZERS_ACCEPTED.add('pickle')
        #Pyro4.config.SERIALIZER = 'pickle'
        Pyro = Pyro4
        using_pyro3 = False
        using_pyro4 = True
    except:
        Pyro = None
        using_pyro3 = False
        using_pyro4 = False

_pyro = Pyro

if sys.version_info >= (3, 0):
    xrange = range
    import queue as Queue
else:
    import Queue

_connection_problem = None
if using_pyro3:
    _connection_problem = _pyro.errors.ProtocolError
elif using_pyro4:
    _connection_problem = _pyro.errors.TimeoutError


def get_nameserver(host=None, port=None, num_retries=30, caller_name="Unknown"):

    if _pyro is None:
        raise ImportError("Pyro or Pyro4 is not available")

    timeout_upper_bound = 5.0

    if not host is None:
        os.environ['PYRO_NS_HOSTNAME'] = host
    elif 'PYRO_NS_HOSTNAME' in os.environ:
        host = os.environ['PYRO_NS_HOSTNAME']

    # Deprecated in Pyro3
    # Removed in Pyro4
    if using_pyro3:
        _pyro.core.initServer()

    ns = None

    for i in xrange(0, num_retries + 1):
        try:
            if using_pyro3:
                ns = _pyro.naming.NameServerLocator().getNS(
                    host=host, port=port)
            else:
                ns = _pyro.locateNS(host=host, port=port)
            break
        except _pyro.errors.NamingError:
            pass
        except _connection_problem:
            # this can occur if the server is too busy.
            pass

        # we originally had a single sleep timeout value, hardcoded to 1 second.
        # the problem with this approach is that if a large number of concurrent
        # processes fail, then they will all re-attempt at roughly the same
        # time. causing more contention than is necessary / desirable. by randomizing
        # the sleep interval, we are hoping to distribute the number of clients
        # attempting to connect to the name server at any given time.
        # TBD: we should eventually read the timeout upper bound from an enviornment
        #      variable - to support cases with a very large (hundreds to thousands)
        #      number of clients.
        if i < num_retries:
            sleep_interval = random.uniform(1.0, timeout_upper_bound)
            print("%s failed to locate name server after %d attempts - "
                  "trying again in %5.2f seconds." %
                  (caller_name, i + 1, sleep_interval))
            time.sleep(sleep_interval)

    if ns is None:
        print("%s could not locate nameserver (attempts=%d)" %
              (caller_name, num_retries + 1))
        raise SystemExit

    return ns


def get_dispatchers(group=":PyUtilibServer",
                    host=None,
                    port=None,
                    num_dispatcher_tries=30,
                    min_dispatchers=1,
                    caller_name=None,
                    ns=None):

    if ns is None:
        ns = get_nameserver(host=host, port=port, caller_name=caller_name)
    else:
        assert caller_name is None
        assert host is None
        assert port is None

    if ns is None:
        raise RuntimeError("Failed to locate Pyro name "
                           "server on the network!")

    cumulative_sleep_time = 0.0
    dispatchers = []
    for i in xrange(0, num_dispatcher_tries):
        ns_entries = None
        if using_pyro3:
            for (name, uri) in ns.flatlist():
                if name.startswith(":PyUtilibServer.dispatcher."):
                    if (name, uri) not in dispatchers:
                        dispatchers.append((name, uri))
        elif using_pyro4:
            for name in ns.list(prefix=":PyUtilibServer.dispatcher."):
                uri = ns.lookup(name)
                if (name, uri) not in dispatchers:
                    dispatchers.append((name, uri))
        if len(dispatchers) >= min_dispatchers:
            break
    return dispatchers

#
# a utility for shutting down Pyro-related components, which at the
# moment is restricted to the name server and any dispatchers. the
# mip servers will come down once their dispatcher is shut down.
# NOTE: this is a utility that should eventually become part of
#       pyutilib.pyro, but because is prototype, I'm keeping it
#       here for now.
#


def shutdown_pyro_components(host=None,
                             port=None,
                             num_retries=30,
                             ns=None,
                             caller_name="Unknown"):

    if _pyro is None:
        raise ImportError("Pyro or Pyro4 is not available")

    if ns is None:
        ns = get_nameserver(host=host,
                            port=port,
                            num_retries=num_retries,
                            caller_name=caller_name)
    if ns is None:
        print("***WARNING - Could not locate name server "
              "- Pyro components will not be shut down")
        return

    if using_pyro3:
        ns_entries = ns.flatlist()
        for (name, uri) in ns_entries:
            if name.startswith(":PyUtilibServer.dispatcher."):
                try:
                    ns.unregister(name)
                    proxy = _pyro.core.getProxyForURI(uri)
                    proxy.shutdown()
                except:
                    pass
        for (name, uri) in ns_entries:
            if name == ":Pyro.NameServer":
                try:
                    proxy = _pyro.core.getProxyForURI(uri)
                    proxy._shutdown()
                    proxy._release()
                except:
                    pass
    elif using_pyro4:
        for name in ns.list(prefix=":PyUtilibServer.dispatcher."):
            try:
                uri = ns.lookup(name)
                ns.remove(name)
                proxy = _pyro.Proxy(uri)
                proxy.shutdown()
                proxy._pyroRelease()
            except:
                pass
        print("")
        print("*** NameServer must be shutdown manually when using Pyro4 ***")
        print("")


def set_maxconnections(max_allowed_connections=None):

    #
    # **NOTE: For some reason with Pyro3 we need to add 1 to this
    #         option in order to to get behavior that makes sense
    #         and matches behavior with Pyro4. For instance,
    #         running a dispatcher with a single client and a single
    #         server requires PYRO_MAXCONNECTIONS=3 with Pyro3 and
    #         requires THREADPOOL_SIZE=2 with Pyro4.
    #
    if max_allowed_connections is None:
        max_pyro_connections_envname = "PYUTILIB_PYRO_MAXCONNECTIONS"
        if max_pyro_connections_envname in os.environ:
            new_val = int(os.environ[max_pyro_connections_envname])
            print("Overriding %s default for maximum number of proxy "
                  "connections to %s, based on specification provided by "
                  "%s environment variable." %
                  ("Pyro" if using_pyro3 else "Pyro4", new_val,
                   max_pyro_connections_envname))
            if using_pyro3:
                _pyro.config.PYRO_MAXCONNECTIONS = new_val + 1
            else:
                _pyro.config.THREADPOOL_SIZE = new_val
    else:
        print("Overriding %s default for maximum number of proxy "
              "connections to %s, based on specification provided by "
              "max_allowed_connections keyword" %
              ("Pyro" if using_pyro3 else "Pyro4", max_allowed_connections))
        if using_pyro3:
            _pyro.config.PYRO_MAXCONNECTIONS = max_allowed_connections + 1
        else:
            _pyro.config.THREADPOOL_SIZE = max_allowed_connections


def bind_port(sock, host="127.0.0.1"):
    """Bind the socket to a free port and return the port number.
    Relies on ephemeral ports in order to ensure we are using an
    unbound port.  This is important as many tests may be running
    simultaneously, especially in a buildbot environment.  This method
    raises an exception if the sock.family is AF_INET and sock.type is
    SOCK_STREAM, *and* the socket has SO_REUSEADDR or SO_REUSEPORT set
    on it.  Tests should *never* set these socket options for TCP/IP
    sockets.  The only case for setting these options is testing
    multicasting via multiple UDP sockets.

    Additionally, if the SO_EXCLUSIVEADDRUSE socket option is
    available (i.e.  on Windows), it will be set on the socket.  This
    will prevent anyone else from bind()'ing to our host/port for the
    duration of the test.

    This code is copied from the stdlib's test.test_support module.
    """
    if sock.family in (socket.AF_INET, socket.AF_INET6
                      ) and sock.type == socket.SOCK_STREAM:
        if hasattr(socket, "SO_EXCLUSIVEADDRUSE"):
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
    if sock.family == socket.AF_INET:
        if host == 'localhost':
            sock.bind(('127.0.0.1', 0))
        else:
            sock.bind((host, 0))
    elif sock.family == socket.AF_INET6:
        if host == 'localhost':
            sock.bind(('::1', 0, 0, 0))
        else:
            sock.bind((host, 0, 0, 0))
    else:
        raise CommunicationError("unsupported socket family: " + sock.family)
    return sock.getsockname()[1]


"""
    if sock.family == socket.AF_INET and sock.type == socket.SOCK_STREAM:
        if hasattr(socket, 'SO_REUSEADDR'):
            if sock.getsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR) == 1:
                raise TestFailed("tests should never set the SO_REUSEADDR "
                                 "socket option on TCP/IP sockets!")
        if hasattr(socket, 'SO_REUSEPORT'):
            try:
                if sock.getsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT) == 1:
                    raise TestFailed("tests should never set the SO_REUSEPORT "
                                     "socket option on TCP/IP sockets!")
            except OSError:
                # Python's socket module was compiled using modern
                # headers thus defining SO_REUSEPORT but this process
                # is running under an older kernel that does not
                # support SO_REUSEPORT.
                pass
        if hasattr(socket, 'SO_EXCLUSIVEADDRUSE'):
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)

    sock.bind((host, 0))
    port = sock.getsockname()[1]
    return port
"""


def find_unused_port(family=socket.AF_INET, socktype=socket.SOCK_STREAM):
    """Returns an unused port that should be suitable for binding.
    This is achieved by creating a temporary socket with the same
    family and type as the 'sock' parameter (default is AF_INET,
    SOCK_STREAM), and binding it to the specified host address
    (defaults to 0.0.0.0) with the port set to 0, eliciting an unused
    ephemeral port from the OS.  The temporary socket is then closed
    and deleted, and the ephemeral port is returned.

    This code is copied from the stdlib's test.test_support module.
    """

    tempsock = socket.socket(family, socktype)
    port = bind_port(tempsock)
    tempsock.close()
    del tempsock
    return port
