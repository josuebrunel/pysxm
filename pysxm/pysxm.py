# Copyright (c) 2017 Josue Kouka
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (Pysxm), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
from __future__ import unicode_literals

import io
import sys

from lxml import etree, objectify as xobject


def is_clean(element):
    """Checks if an element has at least a child
    """
    if not element.getchildren() and element.text is None:
        return False
    return all(is_clean(child) for child in element.iterchildren())


def is_text_type(value):
    """Returns True if <value> is text type
    """
    if sys.version_info.major == 3:
        text_types = (bytes, str)
    else:
        text_types = (str, unicode)
    return isinstance(value, text_types)


class BaseType(object):
    """Base data binding object
    """
    _tagname = None
    namespace = None
    nsmap = None
    attrib = {}

    def __repr__(self):
        return '<%s>' % self.tagname

    @classmethod
    def make_element(cls, tagname, value=None, namespace=None, nsmap=None):
        if nsmap:
            namespace = list(nsmap.values())[0]
        M = xobject.ElementMaker(annotate=False, namespace=namespace,
                                 nsmap=nsmap)
        return M(tagname, value)

    @property
    def tagname(self):
        if self._tagname:
            return self._tagname
        return self.__class__.__name__.lower()

    @property
    def klass(self):
        return self.__class__

    @property
    def xml(self):
        if not isinstance(self, (ComplexType,)):
            element = self.make_element(self.tagname, self.value, nsmap=self.klass.nsmap)
        else:
            element = self.make_element(self.tagname, nsmap=self.klass.nsmap)
            for subelt in self.sequence:
                attr = getattr(self, subelt, None)
                if not attr:
                    continue
                if is_text_type(attr):
                    element.append(self.make_element(subelt, attr, nsmap=self.klass.nsmap))
                else:
                    xml = attr.xml
                    if not is_clean(xml):
                        continue
                    element.append(xml)
        xobject.deannotate(element, xsi_nil=True, cleanup_namespaces=True)
        # set element attributes
        for key, value in self.attrib.items():
            element.set(key, value)
        return element

    def __str__(self):
        return '{}'.format(etree.tostring(self.xml, pretty_print=True))

    def save(self, filename):
        with io.open(filename, 'wb') as fp:
            content = etree.tostring(self.xml, pretty_print=True)
            fp.write(content)


class SimpleType(BaseType):
    """Data binding class for SimpleType
    """

    def __init__(self, value):
        self.check_restriction(value)
        self.value = value

    def check_restriction(self, value):
        raise NotImplementedError(
            '<%s> does not implement <check_restriction> method' % self.__class__.__name__)


class ComplexType(BaseType):
    """Data binding class for ComplexType
    """
    _sequence = None

    @property
    def sequence(self):
        if self._sequence:
            return self._sequence
        return self.__dict__.keys()


__all__ = ["BaseType", "ComplexType", "SimpleType"]
