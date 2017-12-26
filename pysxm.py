from dateutil.parser import parse as dateutil_parse
from lxml import etree, objectify as xobject


def is_clean(element):
    if not element.getchildren() and element.text is None:
        return False
    return all(is_clean(child) for child in element.iterchildren())


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
            if isinstance(attr, (str, unicode)):
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
