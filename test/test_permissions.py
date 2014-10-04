import unittest

from permissions import RuleSet, StaticRule, IterableRule, ObjectRule

def static_true():
	return True

def static_false():
	return False

def obj_even(o):
	return o % 2 == 0

def iter_odd(objects):
	yield from ((x % 2) != 0 for x in objects)

class TestRuleSet(unittest.TestCase):
	def test_repr(self):
		r = repr(RuleSet())
		self.assertIn('RuleSet', r)

	def test_add_rule(self):
		rs = RuleSet()
		rs.add_rule(('some', 'label'), static_true, rule_type=StaticRule)
		self.assertEqual(rs['some', 'label'], {StaticRule(static_true)})

	def test_len(self):
		rs = RuleSet()
		self.assertEqual(len(rs), 0)
		rs.add_rule(('some', 'label'), static_true)
		self.assertEqual(len(rs), 1)

	def test_iter(self):
		rs = RuleSet()
		rs.add_rule(('some', 'label'), static_true)
		
		for key in iter(rs):
			pass

	def test_values(self):
		rs = RuleSet()
		rs.add_rule(('some', 'label'), static_true)
		
		for value in rs.values():
			pass

	def test_items(self):
		rs = RuleSet()
		rs.add_rule(('some', 'label'), static_true)
		
		for key, value in rs.items():
			pass
	
	def test_wildcard(self):
		rs = RuleSet()
		rs.add_rule(('some', 'label'), static_true, rule_type=StaticRule)
		rs.add_rule(('some', '*'), obj_even, rule_type=StaticRule)
		rs.add_rule(('*',), static_false, rule_type=StaticRule)
		self.assertEqual( rs['some', 'label']
		                , { StaticRule(static_true)
						  , StaticRule(static_false)
						  , StaticRule(obj_even)})
	
	def test_wildcard_fail(self):
		rs = RuleSet()
		self.assertRaises(KeyError, rs.__getitem__, '*')
	
	def test_rule_inference(self):
		rs = RuleSet()
		rs.add_rule(('some', 'label'), static_true)
		rs.add_rule(('some', 'label'), obj_even)
		rs.add_rule(('some', 'label'), iter_odd)
		self.assertEqual(set(*rs.rules.values())
		                ,{StaticRule(static_true)
		                 ,ObjectRule(obj_even)
		                 ,IterableRule(iter_odd)})
	
	def test_missing_rule(self):
		rs = RuleSet()
		objects = range(10)
		for o, (foo,) in rs.with_permissions(objects, ('foo',)):
			self.assertFalse(foo)
	
	def test_some_missing(self):
		rs = RuleSet()
		objects = range(10)
		rs.add_rule(('is', 'even'), obj_even)
		for o, (foo, bar) in rs.with_permissions(objects, ('foo',), ('is', 'even')):
			self.assertFalse(foo)
			self.assertEqual(bar, o % 2 == 0)

class TestPermissions(unittest.TestCase):
	def test_static(self):
		rs = RuleSet()
		rs.add_rule(('can', 'not'), static_false)
		rs.add_rule(('can', 'too'), static_true)
		objects = range(10)
		for o, perms in rs.with_permissions(objects, ('can', 'not'), ('can', 'too')):
			self.assertIn(o, objects)
			self.assertFalse(perms[0])
			self.assertTrue(perms[1])
	
	def test_object(self):
		rs = RuleSet()
		rs.add_rule(('is', 'even'), obj_even)
		objects = range(10)
		for o, (is_even,) in rs.with_permissions(objects, ('is', 'even')):
			self.assertIn(o, range(10))
			self.assertEqual(is_even, o % 2 == 0)
	
	def test_iter(self):
		rs = RuleSet()
		rs.add_rule(('is', 'odd'), iter_odd)
		objects = range(10)
		for o, (is_odd,) in rs.with_permissions(objects, ('is', 'odd')):
			self.assertIn(o, range(10))
			self.assertEqual(is_odd, o % 2 != 0)

	def test_multiple_types(self):
		rs = RuleSet()
		rs.add_rule(('can', 'not'), static_false)
		rs.add_rule(('is', 'even'), obj_even)
		rs.add_rule(('is', 'odd'), iter_odd)
		objects = range(10)
		for o, (f, even, odd) in rs.with_permissions(objects, ('can', 'not'), ('is', 'even'), ('is', 'odd')):
			self.assertIn(o, range(10))
			self.assertFalse(f)
			self.assertEqual(even, o % 2 == 0)
			self.assertEqual(odd, o % 2 != 0)
	
	def test_multiple_rules(self):
		rs = RuleSet()
		rs.add_rule(('even-or-odd',), obj_even)
		rs.add_rule(('even-or-odd',), iter_odd)
		objects = range(10)
		for o, (eoo,) in rs.with_permissions(objects, ('even-or-odd',)):
			self.assertTrue(eoo)
