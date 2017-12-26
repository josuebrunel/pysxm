Simple XML Python Marsheller
============================

.. image:: https://travis-ci.org/josuebrunel/pysxm.svg?branch=master
    :target: https://travis-ci.org/josuebrunel/pysxm

**pysxm** is a simple and extensible xml python marsheller.
It comes with the following pre-defined types:

- DateTimeType
- DateType
- TimeType
- SimpleType
- ComplexType


Installation
============

.. code:: python

    pip install pysxm


Things to know
==============

For all types, the default **tagname** is the lowercased name of the class e.g for **class Color(SimpleType)**  we will have **<color>**.
You can set the attribute **_tagame** to customize the xml elemnt *tagname*.
For **ComplexType** you can decide of the *order* of attribute to serialize and which one should be serialized by setting the **_sequence** attribute.

**pysxm** uses *lxml objectify* under the hood. To manipulate the **xml object** of your class:

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


Example
-------

.. code:: python

    In [1]: from pysxm import SimpleType, ComplexType, DateType
    In [2]: class BirthDate(DateType):
    ...:     pass
    ...:
    In [3]: class Profile(SimpleType):
    ...:     allowed_values = ('teacher', 'student')
    ...:
    In [4]: class User(ComplexType):
    ...:
    ...:     sequence = ('username', 'profile', 'birtdate')
    ...:
    In [5]: class User(ComplexType):
    ...:
    ...:     sequence = ('username', 'profile', 'birtdate')
    ...:
    In [6]: class User(ComplexType):
    ...:
    ...:     sequence = ('username', 'profile', 'birthdate')
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



