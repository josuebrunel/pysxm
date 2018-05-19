Simple XML Python Marshaller
============================

.. image:: https://travis-ci.org/josuebrunel/pysxm.svg?branch=master
    :target: https://travis-ci.org/josuebrunel/pysxm
.. image:: https://coveralls.io/repos/github/josuebrunel/pysxm/badge.svg?branch=master
    :target: https://coveralls.io/github/josuebrunel/pysxm?branch=master
.. image:: http://pepy.tech/badge/pysxm
    :target: http://pepy.tech/count/pysxm


**pysxm** is a simple and extensible xml python marshaller.
It comes with two simple and basic types:

- SimpleType
- ComplexType

It supports py2 and py3 and uses *lxml.objectify* under the hood.


Installation
------------

.. code:: python

    pip install pysxm


Quickstart
----------

.. code:: python

    In [1]: from pysxm import ComplexType
    In [2]: class Person(ComplexType):
    ...:     attrib = {'description': 'a random person'}
    ...:     def __init__(self, fname, lname):
    ...:         self.fname = fname
    ...:         self.lname = lname
    ...:
    In [3]: person = Person('token', 'black')
    In [4]: print(person)
    <person xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" description="a random person">
        <lname>black</lname>
        <fname>token</fname>
    </person>

Let's say, we want a different **tag** for our object.
An attribute **tagname** or **_tagname** can be set to define the **xml tag name** of the object.

.. code:: python

    In [5]: class Person(ComplexType):
    ...:     attrib = {'description': 'a random person'}
    ...:     tagname = 'student'
    ...:     def __init__(self, fname, lname):
    ...:         self.fname = fname
    ...:         self.lname = lname
    ...:
    In [6]: person = Person('token', 'black')
    In [7]: print(person)
    <student xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" description="a random person">
        <lname>black</lname>
        <fname>token</fname>
    </student>

A **sequence** or **_sequence** (tuple or list) attribute can be set to decide of the **order** or the **presence** of an subelement in the xml.

.. code:: python

    In [8]: class Person(ComplexType):
    ...:     attrib = {'description': 'a random person'}
    ...:     tagname = 'student'
    ...:     _sequence = ('city', 'fname')
    ...:
    ...:     def __init__(self, fname, lname, city):
    ...:         self.fname = fname
    ...:         self.lname = lname
    ...:         self.city = city
    ...:
    In [9]: person = Person('token', 'black', 'south park')
    In [10]: print(person)
    <student xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" description="a random person">
        <city>south park</city>
        <fname>token</fname>
    </student>

Let's add a **namespace** to our object.

.. code:: python

    In [11]: class Person(ComplexType):
    ...:     attrib = {'description': 'a random south park character'}
    ...:     nsmap = {'sp': 'http://southpark/xml/'}
    ...:
    ...:     def __init__(self, fname, lname, city):
    ...:         self.fname = fname
    ...:         self.lname = lname
    ...:         self.city = city
    ...:
    In [12]: person = Person('token', 'black', 'south park')
    In [13]: print(person)
    <sp:person xmlns:sp="http://southpark/xml/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" description="a random south park character">
        <sp:lname>black</sp:lname>
        <sp:city>south park</sp:city>
        <sp:fname>token</sp:fname>
    </sp:person>

Let's make sure that a *person*'s group is either *coon* or *goth*.
To do so, we can inherit from **SimpleType** object and define a restriction by overriding **check_restriction(self, value)** method.

.. code:: python

    In [7]: from pysxm import ComplexType, SimpleType
    In [8]: class Group(SimpleType):
    ...:     allowed_groups = ('coon', 'goth')
    ...:     def check_restriction(self, value):
    ...:         if value not in self.allowed_groups:
    ...:             raise ValueError('<%s> value %s not in %s' % (self.tagname, value, self.allowed_groups))
    ...:
    In [9]: class Person(ComplexType):
    ...:     def __init__(self, fname, lname, group):
    ...:         self.fname = fname
    ...:         self.lname = lname
    ...:         self.group = Group(group)
    ...:
    In [10]: Person('token', 'black', 'boys')
    ...
    <ipython-input-8-116b49042116> in check_restriction(self, value)
    3     def check_restriction(self, value):
    4         if value not in self.allowed_groups:
    ----> 5             raise ValueError('<%s> value %s not in %s' % (self.tagname, value, self.allowed_groups))
    6
    ValueError: <group> value boys not in ('coon', 'goth')

    In [11]: print(Person('token', 'black', 'goth'))
    <person xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
        <lname>black</lname>
        <group>goth</group>
        <fname>token</fname>
    </person>

**Note**: *ComplexType* can have *ComplexType* and *SimpleType* as attribute

.. code:: python

    from pysxm import ComplexType, SimpleType


    class AdultAge(SimpleType):

        tagname = 'age'
        attrib = {'minvalue': '18', 'maxvalue': '100'}

        def check_restriction(self, value):
            if int(value) < 18:
                raise ValueError("<%s> '%d' < 18" % (self.tagname, value))


    class Credentials(ComplexType):

        def __init__(self, login, password):
            self.login = login
            self.password = password


    class Person(ComplexType):

        def __init__(self, fname, lname, credentials, age):
            self.fname = fname
            self.lname = lname
            self.credentials = Credentials(credentials['login'], credentials['password'])
            self.age = AdultAge(age)

    In [3]: data = {
    ...:     'fname': 'token', 'lname': 'black',
    ...:     'credentials': {'login': 't0ken', 'password': 'l33tolite'},
    ...:     'age': '30'}
    In [4]: person = Person(**data)
    In [5]: print(person)
    <person xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
        <lname>black</lname>
        <credentials>
            <login>t0ken</login>
            <password>l33tolite</password>
        </credentials>
        <age maxvalue="100" minvalue="18">30</age>
        <fname>token</fname>
    </person>
    In [6]: person.save('token.xml')

The **save** method (*object.save(<filename>)*) allows you to save the xml result into a file.

.. code:: python

    In [7]: cat token.xml
    <person xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
        <lname>black</lname>
        <credentials>
            <login>t0ken</login>
            <password>l33tolite</password>
        </credentials>
        <age maxvalue="100" minvalue="18">30</age>
        <fname>token</fname>
    </person>


The ext module
^^^^^^^^^^^^^^

Pysxm comes with a couple of extended types. Those types are defined in *pysxm.ext* module.

DataComplexType
"""""""""""""""

This is a simple *DataClass* of *ComplexType*. Here is how you can set one up:

.. code:: python

    from pysxm.ext import DataComplexType, XSimpleType


    class Game(DataComplexType):
         platform = XSimpleType('platform', ['xboxone', 'xboxx'], lambda v, av: v in av)

    >>> game = (name='state of decay 2', editor='undead labs', platform='xboxone')
    >>> print(game)
    <game>
        <name>state of decay 2</name>
        <platform>xboxone</platform>
        <editor>undead labs</editor>
    </game>

XSimpleType
"""""""""""

It gets tiresome to subclass a *SimpleType* everytime you want to check a value. To overcome that, **pysxm** provides a **descriptor** called **XSimpleType**:

.. code:: python

    class XSimpleType(name=None, restriction=None, checker=None, error_msg=None)
        '''name: it's the name of the attribute.
        restriction: self explanatory
        checker: the fucntion that checks the input value
        error_msg: message returned when checking fails
        '''

Here is an example:


.. code:: python

    class XboxGamer(ComplexType):
        platform = XSimpleType('platform', ('xone', 'xbox360', 'xbox'), lambda v, av: v in av)
        score = XSimpleType('score', (4000, 1000000), lambda v, av: int(av[0]) <= int(v) < int(av[1]))
        lastlogin = XDateTimeType('lastlogin')

        def __init__(self, gamertag, platform, score, lastlogin):
            self.gamertag = gamertag
            self.platform = platform
            self.score = score
            self.lastlogin = lastlogin

    In [1]: print(gamer_data)
    {'gamertag': 'LokingHD', 'platform': 'ps4', 'score': '22526', 'lastlogin': '2018-03-21'}
    In [2]: XboxGamer(**gamer_data)
    ---------------------------------------------------------------------------
    ValueError                                Traceback (most recent call last)
    <ipython-input-2-61f95466da46> in <module>()
    ----> 1 XboxGamer(**gamer_data)
    /home/josue/workspace/dev/pysxdb/pysxm/ext.pyc in check(self, instance, value)
    77         if not self.checker(value, self.restriction_values):
    78             raise ValueError('tagname <%s> value %s is invalid: expected (%s)'
    ---> 79                              % (instance.tagname, value, self.restriction_values))
        80
    81     def check_restriction(self, instance, value):
    ValueError: tagname <xboxgamer> value ps4 is invalid: expected (('xone', 'xbox360', 'xbox'))
    In [3]: gamer_data['platform'] = 'xone'
    In [4]: gamer = XboxGamer(**gamer_data)
    In [5]: print(gamer)
    <xboxgamer xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
        <gamertag>LokingHD</gamertag>
        <platform>xone</platform>
        <score>22526</score>
        <lastlogin>2018-03-21T00:00:00</lastlogin>
    </xboxgamer>


Most of the types defined in *pysxm.ext* are descriptors and they're subclassable.


Voila :wink:
