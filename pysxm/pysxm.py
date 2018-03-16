# Copyright (c) 2017 Josue Kouka
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
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

from dateutil.parser import parse as dateutil_parse
from lxml import etree, objectify as xobject


def is_clean(element):
    if not element.getchildren() and element.text is None:
        return False
    return all(is_clean(child) for child in element.iterchildren())


def is_text_type(value):
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

    def __repr__(self):
        return '<%s>' % self.tagname

    @classmethod
    def make_element(cls, tagname, value=None, namespace=None, nsmap=None):
        M = xobject.ElementMaker(annotate=False, namespace=namespace,
                                 nsmap=nsmap)
        return M(tagname, value)

    @property
    def tagname(self):
        if self._tagname:
            return self._tagname
        return self.__class__.__name__.lower()

    @property
    def xml(self):
        if not isinstance(self, (ComplexType,)):
            return self.make_element(self.tagname, self.value, namespace=self.namespace)
        tag = self.make_element(self.tagname, namespace=self.namespace, nsmap=self.nsmap)
        for subelt in self.sequence:
            attr = getattr(self, subelt, None)
            if not attr:
                continue
            if is_text_type(attr):
                tag.append(self.make_element(subelt, attr, namespace=self.namespace))
            else:
                xml = attr.xml
                if not is_clean(xml):
                    continue
                tag.append(xml)
        xobject.deannotate(tag, xsi_nil=True)
        return tag

    def __str__(self):
        return etree.tostring(self.xml, pretty_print=True)

    def save(self, filename):
        with io.open(filename, 'wb') as fp:
            content = etree.tostring(self.xml, pretty_print=True)
            fp.write(content)


class SimpleType(BaseType):
    """Data binding class for SimpleType
    """
    allowed_values = None

    def __init__(self, value):
        if value not in self.allowed_values:
            raise ValueError('<%s> value (%s) not in %s' % (self.tagname, value,
                                                            self.allowed_values))
        self.value = value


class GenericDateTime(BaseType):

    def __init__(self, value, part=None):
        parsed_date = dateutil_parse(value)
        self.value = parsed_date.isoformat()
        if part:
            self.value = getattr(parsed_date, part)().isoformat()


class DateTimeType(GenericDateTime):

    def __init__(self, value):
        super(DateTimeType, self).__init__(value)


class DateType(GenericDateTime):

    def __init__(self, value):
        super(DateType, self).__init__(value, 'date')


class TimeType(GenericDateTime):

    def __init__(self, value):
        super(TimeType, self).__init__(value, 'time')


class ComplexType(BaseType):
    """Data binding class for ComplexType
    """
    _sequence = None

    @property
    def sequence(self):
        if self._sequence:
            return self._sequence
        return self.__dict__.keys()

# DESCRIPTORS


class XSimpleType(object):

    def __init__(self, allowed_values, name=None):
        self.allowed_values = allowed_values
        if name:
            self.name = name

    def __set__(self, instance, value):
        if instance is None:
            return self
        if value not in self.allowed_values:
            raise ValueError('<%s> value (%s) not in %s' % (
                instance.tagname, value, self.allowed_values))
        instance.__dict__[self.name] = value

    def __get__(self, instance, klass):
        return instance.__dict__[self.name]


class XDateTimeType(object):

    dtype = None

    def __init__(self, name, value=None):
        self.name = name
        self.value = value

    def __set__(self, instance, value):
        if instance is None:
            return self
        parsed_date = dateutil_parse(value)
        if self.dtype:
            instance.__dict__[self.name] = getattr(parsed_date, self.dtype)().isoformat()
        else:
            instance.__dict__[self.name] = parsed_date.isoformat()

    def __get__(self, instance, klass):
        return instance.__dict__[self.name]


class XDateType(XDateTimeType):

    dtype = 'date'


class XTimeType(XDateTimeType):

    dtype = 'time'


__all__ = ["SimpleType", "DateTimeType", "DateType", "TimeType", "ComplexType",
           "XSimpleType", "XDateTimeType", "XDateType", "XTimeType"]
