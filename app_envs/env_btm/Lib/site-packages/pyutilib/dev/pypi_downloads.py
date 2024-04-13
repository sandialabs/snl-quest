#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Calculates the total number of downloads that a particular PyPI package has
received across all versions tracked by PyPI
"""

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict
from datetime import datetime
import locale
import re
import sys
import re
try:
    import xmlrpc.client as xmlrpc
except ImportError:
    import xmlrpc
import math
from optparse import OptionParser

total_packages = 0
total_downloads = 0
total_releases = 0

starttime = None

locale.setlocale(locale.LC_ALL, '')


def total_seconds(td):
    return (td.microseconds +
            (td.seconds + td.days * 24 * 3600) * 10**6) / (1.0 * 10**6)


class PyPIDownloadAggregator(object):

    def __init__(self, package_name, include_hidden=True, exact=False):
        self.package_name = package_name
        self.include_hidden = include_hidden
        self.proxy = xmlrpc.Server('http://pypi.python.org/pypi')
        self._downloads = {}
        self._first_upload = {}
        self._last_upload = {}
        self._exact = exact

        self.first_upload = None
        self.first_upload_rel = None
        self.last_upload = None
        self.last_upload_rel = None

    def packages(self):
        result = self.proxy.package_releases(self.package_name,
                                             self.include_hidden)
        # no matching package--search for possibles
        results = self.proxy.search({
            'name': self.package_name,
            'description': self.package_name
        }, 'or')

        # make sure we only get unique package names
        matches = []
        for match in results:
            if self._exact:
                name = match['name']
                if name not in matches:
                    matches.append(name)
            elif match['name'].startswith(self.package_name):
                matches.append(match)
        return matches

    def downloads(self, release, force=False):
        """Calculate the total number of downloads for the package"""

        urls = self.proxy.release_urls(release['name'], release['version'])
        if not release['name'] in self._downloads:
            self._downloads[release['name']] = OrderedDict()
        if not release['name'] in self._first_upload:
            self._first_upload[release['name']] = OrderedDict()
        if not release['name'] in self._last_upload:
            self._last_upload[release['name']] = OrderedDict()
        self._downloads[release['name']][release['version']] = 0

        for url in urls:
            # upload times
            uptime = datetime.strptime(url['upload_time'].value,
                                       "%Y%m%dT%H:%M:%S")
            #if not starttime is None and uptime <= starttime:
            #    continue

            if self._first_upload[release['name']].get(
                    release['version'],
                    None) is None or uptime < self._first_upload[release[
                        'name']][release['version']]:
                self._first_upload[release['name']][release['version']] = uptime
            if self._last_upload[release['name']].get(
                    release['version'],
                    None) is None or uptime > self._last_upload[release[
                        'name']][release['version']]:
                self._last_upload[release['name']][release['version']] = uptime

            self._downloads[release['name']][release['version']] += url[
                'downloads']

    def stats(self):
        """Prints a nicely formatted list of statistics about the package"""

        print("")
        for release in self.packages():
            print("Processing ... %s %s" %
                  (release['name'], release['version']))
            self.downloads(release)

        for pkg in sorted(self._downloads.keys()):
            global total_packages
            global total_downloads
            global total_releases

            print("")

            ndownloads = 0
            npackages = 0
            keys = self._downloads[pkg].keys()

            def keygen(x):
                ans = []
                for v in x.split('.'):
                    m = re.match('([0-9]+)(.*)', v)
                    ans.append(m.groups())
                return ans
            #keys = [k for k in self._downloads[pkg].keys() if not 'rc' in k]
            #keys.sort(key=lambda x: [int(y) for y in x.split('.')])
            keys.sort(key=keygen)
            for i in range(len(keys)):
                key = keys[i]
                if key in self._first_upload[pkg]:
                    if starttime is not None:
                        if i + 1 < len(keys) and self._first_upload[pkg][keys[
                                i + 1]] <= starttime:
                            continue
                        if i + 1 < len(keys) and self._first_upload[pkg][
                                key] <= starttime:
                            ntimediff = self._first_upload[pkg][keys[
                                i + 1]] - starttime
                            dtimediff = self._first_upload[pkg][keys[
                                i + 1]] - self._first_upload[pkg][keys[i]]
                            downloads = int(
                                math.floor(self._downloads[pkg][
                                    key] * total_seconds(ntimediff) /
                                           total_seconds(dtimediff)))
                        else:
                            downloads = self._downloads[pkg][key]
                    else:
                        downloads = self._downloads[pkg][key]
                    #print downloads, self._downloads[pkg][key]
                    ndownloads += downloads
                    npackages += 1
                    print(
                        "Package %s  Release %10s  Downloads %10d  First Upload %25s  Last Upload %25s"
                        % (pkg, key, downloads, self._first_upload[pkg][key],
                           self._last_upload[pkg][key]))
            print("""Totals:  Package %35s  Downloads: %15s  Releases: %15s""" %
                  (pkg, str(ndownloads), str(npackages)))

            total_packages += 1
            total_downloads += ndownloads
            total_releases += npackages


def _main(argv, exact):
    if len(argv) < 2:
        print(
            "Usage: pypi_downloads.py [--start=yyyy-mm-dd] [--exact] package ...")
        sys.exit('Please specify at least one package name')

    for pkg in argv[1:]:
        PyPIDownloadAggregator(pkg, exact=exact).stats()

    print("")
    print("Total Packages %d" % total_packages)
    print("Total Downloads %d" % total_downloads)
    print("Total Releases %d" % total_releases)


def main():
    global starttime

    parser = OptionParser()
    parser.add_option('--start', action="store", dest="date", default=None)
    parser.add_option(
        '--exact', action="store_false", dest="exact", default=False)
    (options, args) = parser.parse_args(sys.argv)
    if not options.date is None:
        starttime = datetime.strptime(options.date, "%Y-%m-%d")
    else:
        starttime = None
    _main(args, options.exact)


if __name__ == '__main__':
    main()
