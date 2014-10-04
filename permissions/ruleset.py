from inspect import signature
from collections import defaultdict, MutableMapping, OrderedDict
from itertools import chain

from .defaulttypes import StaticRule, IterableRule, ObjectRule
default_rule_types = [StaticRule, IterableRule, ObjectRule]

class RuleSet(MutableMapping):
	'''A mapping of permissions to the rules which grant the permissions.

	   Respects ``'*'`` as a wildcard in permissions granted.
	   A rule denoted for multiple permissions will only be evaluated once.'''
	   
	def __init__(self, rule_types=default_rule_types):
		self.rule_types = rule_types
		self.rules = defaultdict(set)
	
	def __delitem__(self, key):
		del self.rules[key]
	
	def add_rule(self, key, rule, rule_type=None):
		'''Add ``rule`` for the permission ``key``'''
		if len(key) < 1:
			raise ValueError("Label must have at least one element")
		if rule_type is None:
			sig = signature(rule)
			for t in self.rule_types:
				if t.inspect(sig):
					rule_type = t
					break
			else:
				raise ValueError("Rule signature has not been recognized.")
		self.rules[key].add(rule_type(rule))
	
	def rule(self, *key, rule_type=None):
		'''A decorator applying :py:meth:`permissions.RuleSet.add_rule`'''
		def decorator(rule):
			self.add_rule(key, rule, rule_type)
			return rule
		return decorator
	
	def __iter__(self):
		return iter(self.rules)

	def __len__(self, key):
		return len(self.rules)

	def __setitem__(self, key, *args):
		key = tuple(key)
		self.rules[key] = set(args)

	def __getitem__(self, key):
		if '*' in key:
			raise KeyError("Cannot match {} (contains '*')".format(key))
		item = set()
		acc = []
		for k in key:
			item.update(self.rules[tuple(acc + ['*'])])
			acc.append(k)
		item.update(self.rules[tuple(acc)])
		return item
	
	def __repr__(self):
		r = ', '.join(getattr(r, 'name', repr(r))
		                      for r in self.rule_types)
		return "RuleSet({})".format(r)
	
	def with_permissions(self, objects, *permissions):
		# Sort permissions by type (change internal arrangement to match this?)
		rules = OrderedDict((rule_type, defaultdict(list)) for rule_type in self.rule_types)
		perm_idxs = OrderedDict((p, []) for p in permissions)

		for perm in permissions:
			for r in self[perm]:
				rules[type(r)][perm].append(r)
		for k, v in rules.items():
			if not v:
				del rules[k]

		unsatisfied_perms = set(permissions) ^ set(chain.from_iterable(v.keys() for v in rules.values()))
		if unsatisfied_perms:
			raise KeyError("No rules for: {}".format(unsatisfied_perms))

		results = []
		for i, (rule_type, perms) in enumerate(rules.items()):
			if not perms:
				continue
			objects, result = rule_type.apply(objects, perms)
			results.append(result)
			for j, perm in enumerate(perms):
				perm_idxs[perm].append((i, j))

		for o in objects:
			perms = [next(r) for r in results]
			yield o, [any(perms[i][j] for i, j in perm_idxs[perm]) for perm in permissions]
