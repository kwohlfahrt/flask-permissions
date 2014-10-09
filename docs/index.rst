.. Flask-Permissions documentation master file, created by
   sphinx-quickstart on Mon Sep 29 10:40:21 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


Flask-Permissions
=================

Flask-Permissions provides a simple way to define rules to grant permissions.

Installation
============

Installation via ``pip`` is supported.

Requirements
------------

There are no requirements for this module, but ``SQLAlchemy`` queries are supported.

Usage
=====

.. currentmodule:: permissions

Rule Sets
---------

A RuleSet is a class which mapps permission labels to individual rules. The
labels must be iterable and hashable, tuples of strings are recommended (e.g.
``('blog', 'post', 'create')``). The ``'*'`` character is supported as a
wildcard, so a rule that grants ``('blog', '*')`` implicitly grants ``('blog',
'post')``, ``(blog', 'post', 'edit')`` and so on.

The types of rule that may be contained are specified at creation time by
passing a list of rule types to the initialization function. This also defines
the order in which the rules are applied - care should be taken to ensure that
the output of one rule type is compatible with the input of the next.

.. testsetup::

   from permissions import *

First, we set up a ``Thing`` and some rules to apply to it.

.. testcode::

   class Thing:
      def __init__(self, name, editable=False):
         self.editable = editable
         self.name = name
      def __repr__(self):
         return "Thing({})".format(self.name)

   things = [Thing('foo'), Thing('bar', True), Thing('baz')]

   rs = RuleSet()
   rs.add_rule(('thing', 'edit'), lambda object: object.editable, ObjectRuleSet)
   
   @rs.rule('thing', '*', group=StaticRuleSet)
   def sometimes_true():
      return user_is_admin

Now, we see what permissions a normal user has:

.. testcode::

   user_is_admin = False
   for i, (edit, delete) in rs.with_permissions(things, ('thing', 'edit')
                                                      , ('thing', 'delete')):
      print(i, edit, delete, sep=', ')

.. testoutput::

   Thing(foo), False, False
   Thing(bar), True, False
   Thing(baz), False, False

An admin user on the other hand has more permissions:

.. testcode::

   user_is_admin = True
   for i, (edit, delete) in rs.with_permissions(things, ('thing', 'edit')
                                                      , ('thing', 'delete')):
      print(i, edit, delete, sep=', ')

.. testoutput::

   Thing(foo), True, True
   Thing(bar), True, True
   Thing(baz), True, True

Rule Types
----------

A specific :py:class:`RuleTypeSet` is created for each rule type. This class
must define :py:meth:`permissions.Rule.inspect` and
:py:meth:`permissions.Rule.apply`, and is responsible for containing and
applying rules of a specific type. A set of defaults is included that should
cover most use-cases that do not involve external libraries. For more details,
see `API`_.

API
===

.. autoclass:: RuleSet
   :members:
.. autoclass:: RuleTypeSet
   :members:
.. autoclass:: StaticRuleSet
   :members:
.. autoclass:: IterableRuleSet
   :members:
.. autoclass:: ObjectRuleSet
   :members:

Contents:

.. toctree::
   :maxdepth: 2

Indices and tables
==================

* :ref:`genindex`
* :ref:`search`

