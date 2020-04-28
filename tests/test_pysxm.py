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
import os
from lxml import objectify

import pytest

from pysxm import ComplexType, SimpleType
from pysxm.ext import (DateTimeType, DateType, TimeType, XSimpleType,
                       XDateTimeType, XDateType, XTimeType, DataComplexType)
from pysxm.pysxm import BaseType


class ListSimpleType(SimpleType):

    allowed_values = []

    def check_restriction(self, value):
        if value not in self.allowed_values:
            raise ValueError('<%s> value (%s) not in %s' % (self.tagname, value,
                                                            self.allowed_values))


class ListXSimpleType(XSimpleType):
    name = 'platform'

    def check_restriction(self, instance, value):
        if value not in self.restriction_values:
            raise ValueError('<%s> value (%s) not in %s' % (instance.tagname, value,
                                                            self.restriction_values))


class LightColor(ListSimpleType):
    allowed_values = ['green', 'orange', 'red']


class BirthDate(DateType):
    _tagname = 'dateNaissance'


class LastLogin(DateTimeType):
    pass


class NextCycle(TimeType):
    pass


class BirthInfo(ComplexType):

    _sequence = ('city', 'country', 'date')

    def __init__(self, data):
        self.city = data['birth_city']
        self.country = data['birth_country']
        self.date = BirthDate(data['birth_date'])


class Identity(ComplexType):

    sequence = ('first_name', 'last_name', 'birth_info')

    def __init__(self, data):
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.birth_info = BirthInfo(data)


class User(ComplexType):

    sequence = ('username', 'identity', 'last_login')

    def __init__(self, data):
        self.username = data['username']
        self.identity = Identity(data)
        self.last_login = LastLogin(data['last_login'])


def test_empty_node():

    class Whatever(ComplexType):

        sequence = ('user', 'description')

        def __init__(self, user, description=''):
            self.user = user
            self.description = description

    whatever = Whatever('token')
    xml = whatever.xml
    assert xml.tag == 'whatever'
    assert len(xml.getchildren()) == 1
    assert xml.user.text == 'token'

    whatever = Whatever('token', 'this is t0k3n')
    xml = whatever.xml
    assert xml.tag == 'whatever'
    assert len(xml.getchildren()) == 2
    assert xml.user.text == 'token'
    assert xml.description == 'this is t0k3n'


def test_simple_type():

    class TmpFile(SimpleType):
        pass

    with pytest.raises(NotImplementedError) as exc:
        TmpFile('whaever')
    assert exc.value.args[0] == "<TmpFile> does not implement <check_restriction> method"

    with pytest.raises(ValueError) as exc:
        LightColor('pink')
    assert exc.value.args[0] == "<lightcolor> value (pink) not in %s" % LightColor.allowed_values

    light_color = LightColor('green')
    assert light_color.__repr__() == '<lightcolor>'
    xml = light_color.xml
    assert xml.tag == 'lightcolor'
    assert xml.text == 'green'
    print(light_color)


def test_datetime_type():
    with pytest.raises(ValueError) as exc:
        BirthDate('that was when i logged in')
    assert exc.value.args[0] == "Unknown string format: %s"

    event_dt = LastLogin('2016-06-18 9:34')
    xml = event_dt.xml
    xml.tag == 'lastlogin'
    xml.text == '2016-06-18T09:34'


def test_date_type():
    with pytest.raises(ValueError) as exc:
        BirthDate('this is my brithday')
    assert exc.value.args[0] == "Unknown string format: %s"

    birth_date = BirthDate('1990-07-21')
    xml = birth_date.xml
    xml.tag == 'dateNaissance'
    xml.text == '1990-07-21'


def test_time_type():
    with pytest.raises(ValueError) as exc:
        NextCycle('10:34 will be the next cycle')
    assert exc.value.args[0] == "Unknown string format: %s"

    ncycle = NextCycle('10:34')
    xml = ncycle.xml
    xml.tag == 'nextcycle'
    xml.text == '10:34'


def test_complex_type():
    data = {
        'username': 't0k3n',
        'first_name': 'Token',
        'last_name': 'BLACK',
        'birth_city': 'South Park',
        'birth_country': 'U.S',
        'birth_date': '2007-06-20',
        'last_login': '2017-12-25 8:30:12'
    }

    token = User(data)
    xml = token.xml

    assert xml.username.text == 't0k3n'
    assert xml.identity.first_name.text == 'Token'
    assert xml.identity.last_name.text == 'BLACK'
    assert xml.identity.birthinfo.city.text == 'South Park'
    assert xml.identity.birthinfo.country.text == 'U.S'
    assert xml.identity.birthinfo.dateNaissance.text == '2007-06-20'
    assert xml.lastlogin.text == '2017-12-25T08:30:12'


def test_complex_type_without_sequence():

    class Person(ComplexType):

        def __init__(self, fname, lname):
            self.fname = fname
            self.lname = lname

    person = Person('token', 'black')
    xml = person.xml
    assert xml.fname == 'token'
    assert xml.lname == 'black'


def test_save_to_file(tmpdir):

    class Person(ComplexType):

        def __init__(self, fname, lname):
            self.fname = fname
            self.lname = lname

    token = Person('token', 'black')
    filename = os.path.join(tmpdir.strpath, 'person.xml')
    assert os.path.isfile(filename) is False
    token.save(filename)
    assert os.path.isfile(filename) is True
    content = io.open(filename, 'rb').read()
    root = objectify.XML(content)
    assert root.fname == 'token'
    assert root.lname == 'black'


def test_descriptor_attribute():

    class TmpFile(ComplexType):

        path = XSimpleType('path', '/tmp')

        def __init__(self, path):
            self.path = path

    with pytest.raises(NotImplementedError) as exc:
        TmpFile('/home/whatever.txt')
    assert exc.value.args[0] == "<TmpFile> does not implement <check_restriction> method"

    class Player(ComplexType):

        platform = ListXSimpleType(restriction=['pc'])
        lastlogin = XDateTimeType('lastlogin')
        birthdate = XDateType('birthdate')
        timeplayed = XTimeType('timeplayed')

        def __init__(self, gamertag, platform, brithdate):
            self.gamertag = gamertag
            self.platform = platform
            self.birthdate = brithdate

    assert Player.platform.name == 'platform'
    assert Player.lastlogin.name == 'lastlogin'

    with pytest.raises(ValueError) as exc:
        Player('lokinghd', 'xone', '1990-10-10')
    assert exc.value.args[0] == "<player> value (xone) not in %s" % ['pc']

    josh = Player('lokinghd', 'pc', '1990-10-10')
    josh.lastlogin = '2018-03-20T00:27'
    josh.timeplayed = '04:42'
    xml = josh.xml
    assert xml.gamertag == 'lokinghd'
    assert xml.platform == 'pc'
    assert xml.birthdate == '1990-10-10'
    assert xml.lastlogin == '2018-03-20T00:27:00'
    assert xml.timeplayed == '04:42:00'


def test_descriptor_with_checker():

    class PyDeveloper(ComplexType):
        tagname = 'dev'
        language = XSimpleType('language', ['c', 'c++', 'python'], lambda v, av: v in av)

        def __init__(self, name, country, language):
            self.name = name
            self.country = country
            self.language = language

    with pytest.raises(ValueError) as exc:
        PyDeveloper('josh', 'congo', 'java')
    assert exc.value.args[0] == "tagname <dev> value java is invalid: expected (%s)" % ['c', 'c++', 'python']

    josh = PyDeveloper('josh', 'congo', 'python')
    xml = josh.xml
    assert xml.name == 'josh'
    assert xml.country == 'congo'
    assert xml.language == 'python'


def test_descriptor_with_custom_error_msg():

    custom_error_msg = "<%(value)s> seriously!"

    class PyDeveloper(ComplexType):
        tagname = 'dev'
        language = XSimpleType('language', ['c', 'c++', 'python'], lambda v, av: v in av, custom_error_msg)

        def __init__(self, name, country, language):
            self.name = name
            self.country = country
            self.language = language

    with pytest.raises(ValueError) as exc:
        PyDeveloper('josh', 'congo', 'java')
    assert exc.value.args[0] == "<java> seriously!"

    josh = PyDeveloper('josh', 'congo', 'python')
    xml = josh.xml
    assert xml.name == 'josh'
    assert xml.country == 'congo'
    assert xml.language == 'python'


def test_xsimple_type_subclass():

    class Platform(ListXSimpleType):
        name = 'platform'

    class XboxGamer(ComplexType):

        platform = Platform(restriction=['xone', 'xbox360', 'xbox'])

        def __init__(self, gamertag, platform):
            self.gamertag = gamertag
            self.platform = platform

    with pytest.raises(ValueError) as exc:
        XboxGamer('l33t', 'ps4')
    assert exc.value.args[0] == "<xboxgamer> value (ps4) not in %s" % ['xone', 'xbox360', 'xbox']

    xgamer = XboxGamer('l33t', 'xone')
    xml = xgamer.xml
    assert xml.gamertag == 'l33t'
    assert xml.platform == 'xone'


def test_type_attribute():
    class LimitedNoneNegativeValue(BaseType):
        attrib = {'min_value': '0', 'max_value': '100'}
        tagname = 'value'

        def __init__(self, value):
            if not (int(self.attrib['min_value']) <= value < int(self.attrib['max_value'])):
                raise ValueError('Value not within range')
            self.value = str(value)

    someval = LimitedNoneNegativeValue(20)
    assert someval.xml.text == '20'
    assert someval.xml.attrib['min_value'] == '0'
    assert someval.xml.attrib['max_value'] == '100'


def test_complext_type_data_class():

    class Game(DataComplexType):

        platform = XSimpleType('platform', ['xboxone', 'xboxx'], lambda v, av: v in av)

    with pytest.raises(ValueError) as exc:
        game = Game(name='state of decay 2', platform='sp4', editor='undead labs')
    assert exc.value.args[0] == 'tagname <game> value sp4 is invalid: expected (%s)' % ['xboxone', 'xboxx']

    game = Game(name='state of decay 2', platform='xboxone', editor='undead labs')
    xml = game.xml
    assert xml.name == 'state of decay 2'
    assert xml.editor == 'undead labs'
    assert xml.platform == 'xboxone'


def test_simple_namesapce_definition():

    class NsMixin(object):
        nsmap = {'wht': 'https://whatever/xsd'}

    class NsAge(NsMixin, SimpleType):
        tagname = 'age'

        def check_restriction(self, *args, **kwargs):
            pass

    class NsPerson(NsMixin, ComplexType):

        def __init__(self, fname, lname, age):
            self.fname = fname
            self.lname = lname
            self.age = NsAge(age)

    person = NsPerson('eric', 'cartman', '10')
    xml = person.xml
    assert xml.fname.nsmap == NsPerson.nsmap
    assert xml.lname.nsmap == NsPerson.nsmap
    assert xml.age.nsmap == NsAge.nsmap


def test_xsimple_type_as_real_simpletype():

    class Hero(DataComplexType):

        nsmap = {'wht': 'https://whatever/xsd'}
        faction = XSimpleType('faction', ['red talion', 'black zero'], lambda v, av: v in av,
                              tagname='group', nsmap={'wht': 'https://whatever/xsd'},
                              attrib={'list': 'red talion, the hippies'})

    hero = Hero(nickname='Nick', faction='red talion')
    xml = hero.xml
    assert xml.group == 'red talion'
    assert xml.group.attrib == {'list': 'red talion, the hippies'}
    assert xml.group.nsmap == hero.nsmap


def test_numeric_type():

    class Whatever(DataComplexType):
        pass

    limit = Whatever(min_value=10, max_value=20, avg='15', product='orange')
    xml = limit.xml
    assert xml.product == 'orange'
    assert xml.min_value == 10
    assert xml.max_value == 20
    assert xml.avg == 15


def test_element_with_attr_value_0():

    class Whatever(ComplexType):

        def __init__(self, user, points):
            self.user = user
            self.points = points

    wh = Whatever('token', 0)
    xml = wh.xml
    assert xml.user == 'token'
    assert xml.points == 0
