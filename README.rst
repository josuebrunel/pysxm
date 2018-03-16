Simple XML Python Marsheller
============================

.. image:: https://travis-ci.org/josuebrunel/pysxm.svg?branch=master
    :target: https://travis-ci.org/josuebrunel/pysxm
.. image:: https://coveralls.io/repos/github/josuebrunel/pysxm/badge.svg?branch=master
    :target: https://coveralls.io/github/josuebrunel/pysxm?branch=master


**pysxm** is a simple and extensible xml python marsheller.
It comes with the following pre-defined types:

- DateTimeType
- DateType
- TimeType
- SimpleType
- ComplexType


Installation
------------

.. code:: python

    pip install pysxm


Couple things to know
---------------------

- For all types, the default **tagname** is the lowercased name of the class e.g for **class Color(SimpleType)**  we will have **<color>**. You can customize it by setting the attribute **_tagame** in your subclass.
- For **ComplexType** you can decide of the **order**  and the **presence** of attributes to serialize by setting the **_sequence** attribute (tuple, list) in your subclass.
- **pysxm** uses *lxml objectify* under the hood. To manipulate the **xml object** of your class:

.. code:: python

    In [16]: class Person(ComplexType):
    ...:     _tagname = 'personne'
    ...:     _sequence = ('lname', 'fname')
    ...:     def __init__(self, fname, lname):
    ...:         self.fname = fname
    ...:         self.lname = lname
    ...:
    In [17]: token = Person('token', 'black')
    In [18]: token.xml
    Out[18]: <Element personne at 0x7f85c0df2e60>
    In [26]: print(token)
    <personne xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
        <lname>black</lname>
        <fname>token</fname>
    </personne>

Note that the *tag name* is not the expected one, because of:

.. code:: python

    _tagname = 'personne'


Examples
--------

.. code:: python

    In [1]: from pysxm import SimpleType, ComplexType, DateType
    In [2]: class BirthDate(DateType):
    ...:     pass
    ...:
    In [3]: class Profile(SimpleType):
    ...:     allowed_values = ('teacher', 'student')
    ...:
    In [6]: class User(ComplexType):
    ...:
    ...:     _sequence = ('username', 'profile', 'birthdate')
    ...:     def __init__(self, data):
    ...:         self.username = data['username']
    ...:         self.profile = Profile(data['profile'])
    ...:         self.birthdate = BirthDate(data['birthdate'])
    ...:
    In [8]: data = {
    ...: 'username': 't0k3n',
    ...: 'profile': 'student',
    ...: 'birthdate': '2007-06-20'}
    In [11]: token = User(data)
    In [12]: print(token)
    <user xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
        <username>t0k3n</username>
        <profile>student</profile>
        <birthdate>2007-06-20</birthdate>
    </user>
    # SAVING ELEMENT INTO FILE
    In [1]: p = Person('token', 'black')

    In [2]: p.save('person.xml')

    In [3]: cat person.xml
    <person xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
      <lname>black</lname>
      <fname>token</fname>
    </person>
    In [4]:
    # SETTING NAMESPACE
    In [5]: class Person(ComplexType):
    ...:     namespace = 'http://tempuri.org/XMLSchema.xsd'
    ...:     nsmap = {'xs': 'http://tempuri.org/XMLSchema.xsd'}
    ...:     def __init__(self, fname, lname):
    ...:         self.fname = fname
    ...:         self.lname = lname
    ...:
    In [6]: p = Person('token', 'black')
    In [7]: print(p)
    <xs:person xmlns:xs="http://tempuri.org/XMLSchema.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
        <xs:lname>black</xs:lname>
        <xs:fname>token</xs:fname>
    </xs:person>


Descriptors
-----------

Instead of defining useless class for **none complex type**, you can use some descriptors

.. code:: python

    In [1]: from pysxm import ComplexType, XDateTimeType, XSimpleType, XDateType, XTimeType
    In [2]: class Player(ComplexType):
    ...:
    ...:         platform = XSimpleType(['pc'], 'platform')
    ...:         lastlogin = XDateTimeType('lastlogin')
    ...:         birthdate = XDateType('birthdate')
    ...:         timeplayed = XTimeType('timeplayed')
    ...:
    ...:         def __init__(self, gamertag, platform, brithdate):
    ...:             self.gamertag = gamertag
    ...:             self.platform = platform
    ...:             self.birthdate = brithdate
    ...:
    In [3]: player = Player('lokinghd', 'pc', '1990-10-10')
    In [4]: print(player)
    <player xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
        <gamertag>lokinghd</gamertag>
        <platform>pc</platform>
        <birthdate>1990-10-10</birthdate>
    </player>
    In [5]: player.lastlogin = '2018-03-20T00:27'
    In [6]: player.timeplayed = '04:42'
    In [7]: print(player)
    <player xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
        <gamertag>lokinghd</gamertag>
        <platform>pc</platform>
        <timeplayed>04:42:00</timeplayed>
        <lastlogin>2018-03-20T00:27:00</lastlogin>
        <birthdate>1990-10-10</birthdate>
    </player>

Voila :wink:
