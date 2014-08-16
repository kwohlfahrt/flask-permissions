import unittest

from permissions import RuleSet, StaticRule, IterableRule, ObjectRule, QueryRule

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import Session, relationship
from sqlalchemy.orm.query import Query

Base = declarative_base()

rule_types = [StaticRule, QueryRule, IterableRule, ObjectRule]

def big_thing() -> Query:
	return (Thing.number > 10)

def b_name() -> Query:
	return (Thing.name.like('b%'))

def f_name(objects):
	yield from (o.name[0] == 'f' for o in objects)

class Thing(Base):
	__tablename__ = 'thing'

	number = Column(Integer, primary_key=True)
	name = Column(String)

	def __init__(self, name, number=None):
		self.name = name
		if number:
			self.number = number

	def __eq__(self, other):
		return self.number == other.number and self.name == other.name
	
	def __repr__(self):
		return "Thing(#{}: {})".format(self.number, self.name)

class TestQueryRuleInference(unittest.TestCase):
	def test_rule_inference(self):
		rs = RuleSet(rule_types)
		rs.add_rule(('foo',), big_thing)
		self.assertEqual(set(*rs.rules.values())
		                ,{QueryRule(big_thing)})

class TestQueryRule(unittest.TestCase):
	def setUp(self):
		self.engine = create_engine('sqlite://', echo=False)
		Base.metadata.create_all(self.engine)
		self.session = Session(self.engine)
	
	def test_engine(self):
		pass
	
	def test_simple(self):
		rs = RuleSet(rule_types)
		rs.add_rule(('is', 'big'), big_thing)

		objects = [Thing('foo'), Thing('bar'), Thing('big', number=20)]
		self.session.add_all(objects)
		self.session.commit()
		objects = self.session.query(Thing)

		for o, (big,) in rs.with_permissions(objects, ('is', 'big')):
			self.assertEqual(o.number > 10, big)
	
	def test_multiple(self):
		rs = RuleSet(rule_types)
		rs.add_rule(('is', 'big'), big_thing)
		rs.add_rule(('is', 'b'), b_name)

		objects = [Thing('foo'), Thing('bar'), Thing('big', number=20)]
		self.session.add_all(objects)
		self.session.commit()
		objects = self.session.query(Thing)

		for o, (big, b) in rs.with_permissions(objects, ('is', 'big'), ('is', 'b')):
			self.assertEqual(o.number > 10, big)
			self.assertEqual(o.name[0] == 'b', b)
	
	def test_other_types(self):
		rs = RuleSet(rule_types)
		rs.add_rule(('is', 'big'), big_thing)
		rs.add_rule(('is', 'b'), b_name)
		rs.add_rule(('is', 'f'), f_name)

		objects = [Thing('foo'), Thing('bar'), Thing('big', number=20)]
		self.session.add_all(objects)
		self.session.commit()
		objects = self.session.query(Thing)

		for o, (big, b, f) in rs.with_permissions(objects, ('is', 'big'), ('is', 'b'), ('is', 'f')):
			self.assertEqual(o.number > 10, big)
			self.assertEqual(o.name[0] == 'b', b)
			self.assertEqual(o.name[0] == 'f', f)
