from inspect import signature
from collections import OrderedDict

from .defaulttypes import StaticRuleSet, IterableRuleSet, ObjectRuleSet
default_rule_types = [StaticRuleSet, IterableRuleSet, ObjectRuleSet]

class RuleSet:
	'''A mapping of permissions to the rules which grant the permissions.

	   Respects ``'*'`` as a wildcard in permissions granted.
	   A rule denoted for multiple permissions will only be evaluated once.'''
	   
	def __init__(self, *rule_types):
		self.rules = OrderedDict((t, t()) for t in rule_types or default_rule_types)
	
	def __len__(self):
		return sum(len(rules) for rules in self.rules.values())

	def __contains__(self, key):
		return any(key in rules for rules in self.rules.values())

	def __getitem__(self, key):
		return set.union(*(rule_type[key] for rule_type in self.rules.values()))

	def update(self, other):
		for rule_type, rules in self.rules.items():
			rules.update(other.rules.get(rule_type, {}))
	
	def __repr__(self):
		r = ', '.join(repr(r) for r in self.rules)
		return "RuleSet({})".format(r)

	def add_rule(self, key, rule, group=None):
		'''Add ``rule`` for the permission ``key``'''
		if len(key) < 1:
			raise ValueError("Label must have at least one element")
		if group is None:
			sig = signature(rule)
			for t in self.rules:
				if t.inspect(sig):
					group = t
					break
			else:
				raise ValueError("Rule signature has not been recognized.")
		self.rules[group].rules[key].add(rule)
	
	def rule(self, *key, group=None):
		'''A decorator applying :py:meth:`permissions.RuleSet.add_rule`'''
		def decorator(rule):
			self.add_rule(key, rule, group)
			return rule
		return decorator
	
	def with_permissions(self, objects, *permissions):
		'''Tests whether permissions are granted for an iterable of
		objects

		:param objects: The objects to test. They may be of any type
				compatible with the :py:class:`RuleTypeSet`
		                contained in this object.
		:param permissions: The permissions to test for.
		:returns: An iterable of tuples containing the objects tested
			  and whether each permission has been granted for the
		          object.
		:rtype: ``[(object, (permission, permission, ...))]``
		'''

		results = []
		for rule_type_set in self.rules.values():
			objects, r = rule_type_set.apply(objects, *permissions)
			results.append(r)

		results = (zip(*result) for result in zip(*results))
		for o in objects:
			yield o, [any(r) for r in next(results)]
