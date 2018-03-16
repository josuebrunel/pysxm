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

from pysxm import (SimpleType, DateTimeType, DateType, TimeType, ComplexType,
                   XSimpleType, XDateTimeType, XDateType, XTimeType)


class LightColor(SimpleType):
    allowed_values = ['green', 'orange', 'red']


class BirthDate(DateType):
    _tagname = 'dateNaissance'


class LastLogin(DateTimeType):
    pass


class NextCycle(TimeType):
    pass


class BirthInfo(ComplexType):

    sequence = ('city', 'country', 'date')

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
    with pytest.raises(ValueError) as exc:
        LightColor('pink')
    assert exc.value.args[0] == "<lightcolor> value (pink) not in %s" % LightColor.allowed_values

    light_color = LightColor('green')
    xml = light_color.xml
    assert xml.tag == 'lightcolor'
    assert xml.text == 'green'


def test_datetime_type():
    with pytest.raises(ValueError) as exc:
        BirthDate('that was when i logged in')
    assert exc.value.args[0] == "Unknown string format:"

    event_dt = LastLogin('2016-06-18 9:34')
    xml = event_dt.xml
    xml.tag == 'lastlogin'
    xml.text == '2016-06-18T09:34'


def test_date_type():
    with pytest.raises(ValueError) as exc:
        BirthDate('this is my brithday')
    assert exc.value.args[0] == "Unknown string format:"

    birth_date = BirthDate('1990-07-21')
    xml = birth_date.xml
    xml.tag == 'dateNaissance'
    xml.text == '1990-07-21'


def test_time_type():
    with pytest.raises(ValueError) as exc:
        NextCycle('10:34 will be the next cycle')
    assert exc.value.args[0] == "Unknown string format:"

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

    class Player(ComplexType):

        platform = XSimpleType(['pc'], 'platform')
        lastlogin = XDateTimeType('lastlogin')
        birthdate = XDateType('birthdate')
        timeplayed = XTimeType('timeplayed')

        def __init__(self, gamertag, platform, brithdate):
            self.gamertag = gamertag
            self.platform = platform
            self.birthdate = brithdate

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


def test_xsimple_type_subclass():

    class Platform(XSimpleType):
        name = 'platform'

    class XboxGamer(ComplexType):

        platform = Platform(['xone', 'xbox360', 'xbox'])

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
