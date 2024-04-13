#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________

__all__ = ['get_xml_text', 'escape', 'compare_xml_files']

from xml.dom import Node
import sys


def get_xml_text(node):
    nodetext = ""
    for child in node.childNodes:
        if child.nodeType == Node.TEXT_NODE:
            nodetext = nodetext + child.nodeValue
    nodetext = str(nodetext)
    return nodetext.strip()


if sys.version_info < (3, 0):
    _identitymap = "".join([chr(n) for n in range(256)])
    _delchars = _identitymap[:9] + chr(11) + chr(12) + _identitymap[
        14:31] + chr(124)

    def escape(s):
        """Replace special characters '&', "'", '<', '>' and '"' by XML entities."""
        s = s.replace("&", "&amp;")  # Must be done first!
        s = s.replace("<", "&lt;")
        s = s.replace(">", "&gt;")
        s = s.translate(_identitymap, _delchars)
        return s

else:

    _tmap = {}
    for n in range(256):
        if n < 9 or (n >= 14 and n < 31) or n in (11, 12, 124):
            _tmap[chr(n)] = None

    def escape(s):
        """Replace special characters '&', "'", '<', '>' and '"' by XML entities."""
        s = s.replace("&", "&amp;")  # Must be done first!
        s = s.replace("<", "&lt;")
        s = s.replace(">", "&gt;")
        s = s.translate(_tmap)
        return s


def compare_xml_files(baseline_fname,
                      output_fname,
                      tolerance=0.0,
                      baseline_begin='',
                      baseline_end='',
                      output_begin='',
                      output_end=None,
                      exact=True):
    from pyutilib.misc.pyyaml_util import extract_subtext, compare_repn
    from pyutilib.misc.xmltodict import parse
    #
    INPUT = open(baseline_fname, 'r')
    baseline = extract_subtext(
        INPUT, begin_str=baseline_begin, end_str=baseline_end)
    INPUT.close()
    #
    INPUT = open(output_fname, 'r')
    output = extract_subtext(INPUT, begin_str=output_begin, end_str=output_end)
    INPUT.close()
    #
    baseline_repn = parse(baseline)
    output_repn = parse(output)
    return compare_repn(
        baseline_repn, output_repn, tolerance=tolerance, exact=exact)
