import pytest

from pysxm import (SimpleType, DateTimeType, DateType,
                   TimeType, ComplexType)


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
    assert xml.user == 'token'
    assert xml.description == 'this is t0k3n'


def test_simple_type():
    with pytest.raises(ValueError) as exc:
        LightColor('pink')
    assert exc.value.message == "<lightcolor> value (pink) not in ['green', 'orange', 'red']"

    light_color = LightColor('green')
    xml = light_color.xml
    assert xml.tag == 'lightcolor'
    assert xml.text == 'green'


def test_datetime_type():
    with pytest.raises(ValueError) as exc:
        BirthDate('that was when i logged in')
    assert exc.value.message == "Unknown string format"

    event_dt = LastLogin('2016-06-18 9:34')
    xml = event_dt.xml
    xml.tag == 'lastlogin'
    xml.text == '2016-06-18T09:34'


def test_date_type():
    with pytest.raises(ValueError) as exc:
        BirthDate('this is my brithday')
    assert exc.value.message == "Unknown string format"

    birth_date = BirthDate('1990-07-21')
    xml = birth_date.xml
    xml.tag == 'dateNaissance'
    xml.text == '1990-07-21'


def test_time_type():
    with pytest.raises(ValueError) as exc:
        NextCycle('10:34 will be the next cycle')
    assert exc.value.message == "Unknown string format"

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
