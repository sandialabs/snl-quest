"""
Copyright (C) 2012 Martin Blech and individual contributors.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from xml.parsers import expat
from xml.sax.saxutils import XMLGenerator
from xml.sax.xmlreader import AttributesImpl
try:  # pragma no cover
    from cStringIO import StringIO
except ImportError:  # pragma no cover
    try:
        from StringIO import StringIO
    except ImportError:
        from io import StringIO
try:  # pragma no cover
    #OrderedDict = dict
    from collections import OrderedDict
except ImportError:  # pragma no cover
    from ordereddict import OrderedDict

try:  # pragma no cover
    _basestring = basestring
except NameError:  # pragma no cover
    _basestring = str
try:  # pragma no cover
    _unicode = unicode
except NameError:  # pragma no cover
    _unicode = str

from pyutilib.misc.pyyaml_util import yaml_eval

__author__ = 'Martin Blech'
__version__ = '0.2'
__license__ = 'MIT'


class ParsingInterrupted(Exception):
    pass


class _DictSAXHandler:

    def __init__(self,
                 item_depth=0,
                 item_callback=lambda *args: True,
                 xml_attribs=True,
                 attr_prefix='@',
                 cdata_key='#text',
                 force_cdata=False,
                 cdata_separator=''):
        self.path = []
        self.stack = []
        self.data = None
        self.item = None
        self.item_depth = item_depth
        self.xml_attribs = xml_attribs
        self.item_callback = item_callback
        self.attr_prefix = attr_prefix
        self.cdata_key = cdata_key
        self.force_cdata = force_cdata
        self.cdata_separator = cdata_separator

    def startElement(self, name, attrs):
        self.path.append((name, attrs or None))
        if len(self.path) > self.item_depth:
            self.stack.append((self.item, self.data))
            attrs = OrderedDict((self.attr_prefix + key, yaml_eval(value))
                                for (key, value) in attrs.items())
            self.item = self.xml_attribs and attrs or None
            self.data = None

    def endElement(self, name):
        if len(self.path) == self.item_depth:
            item = self.item
            if item is None:
                item = self.data
            should_continue = self.item_callback(self.path, item)
            if not should_continue:
                raise ParsingInterrupted()
        if len(self.stack):
            item, data = self.item, self.data
            self.item, self.data = self.stack.pop()
            if data and self.force_cdata and item is None:
                item = OrderedDict()
            if item is not None:
                if data:
                    item[self.cdata_key] = data
                self.push_data(name, item)
            else:
                self.push_data(name, data)
        else:
            self.item = self.data = None
        self.path.pop()

    def characters(self, data):
        if data.strip():
            if not self.data:
                self.data = data
            else:
                self.data += self.cdata_separator + data

    def push_data(self, key, data):
        if self.item is None:
            self.item = OrderedDict()
        try:
            value = self.item[key]
            if isinstance(value, list):
                value.append(data)
            else:
                self.item[key] = [value, yaml_eval(data)]
        except KeyError:
            self.item[key] = yaml_eval(data)


def parse(xml_input, *args, **kwargs):
    """Parse the given XML input and convert it into a dictionary.

    `xml_input` can either be a `string` or a file-like object.

    If `xml_attribs` is `True`, element attributes are put in the dictionary
    among regular child elements, using `@` as a prefix to avoid collisions. If
    set to `False`, they are just ignored.

    Simple example::

        >>> doc = xmltodict.parse(\"\"\"
        ... <a prop="x">
        ...   <b>1</b>
        ...   <b>2</b>
        ... </a>
        ... \"\"\")
        >>> doc['a']['@prop']
        u'x'
        >>> doc['a']['b']
        [u'1', u'2']

    If `item_depth` is `0`, the function returns a dictionary for the root
    element (default behavior). Otherwise, it calls `item_callback` every time
    an item at the specified depth is found and returns `None` in the end
    (streaming mode).

    The callback function receives two parameters: the `path` from the document
    root to the item (name-attribs pairs), and the `item` (dict). If the
    callback's return value is false-ish, parsing will be stopped with the
    :class:`ParsingInterrupted` exception.

    Streaming example::

        >>> def handle(path, item):
        ...     print 'path:%s item:%s' % (path, item)
        ...     return True
        ... 
        >>> xmltodict.parse(\"\"\"
        ... <a prop="x">
        ...   <b>1</b>
        ...   <b>2</b>
        ... </a>\"\"\", item_depth=2, item_callback=handle)
        path:[(u'a', {u'prop': u'x'}), (u'b', None)] item:1
        path:[(u'a', {u'prop': u'x'}), (u'b', None)] item:2

    """
    handler = _DictSAXHandler(*args, **kwargs)
    parser = expat.ParserCreate()
    parser.StartElementHandler = handler.startElement
    parser.EndElementHandler = handler.endElement
    parser.CharacterDataHandler = handler.characters
    if hasattr(xml_input, 'read'):
        parser.ParseFile(xml_input)
    else:
        parser.Parse(xml_input, True)
    return handler.item
