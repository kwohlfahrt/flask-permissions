from itertools import repeat, tee, chain
from collections import defaultdict

from .util import invertMapping

class Rule:
	def __init__(self, rule):
		self.rule = rule
	
	def __hash__(self):
		return hash(self.rule)
	
	def __eq__(self, other):
		return type(self) == type(other) and self.rule == other.rule
	
	def __repr__(self):
		return "{}({})".format(type(self).__name__, self.rule)
	
	def __call__(self, *args, **kwargs):
		return self.rule(*args, **kwargs)

class StaticRule(Rule):
	@staticmethod
	def inspect(sig):
		return ( len(sig.parameters) == 0
		       and ( sig.return_annotation == sig.empty
			       or sig.return_annotation == bool))

	@staticmethod
	def apply(objects, rules):
		# TODO: Return True and enable short-circuiting in RuleSet
		return objects, zip(*(repeat(any(r() for r in perm_rules))
		                      for perm_rules in rules.values()))

class IterableRule(Rule):
	@staticmethod
	def inspect(sig):
		if len(sig.parameters) != 1:
			return False
		p = next(iter(sig.parameters.values()))
		return ( ( p.annotation == iter
		         or p.name == 'objects') 
			   and ( sig.return_annotation == sig.empty
			       or sig.return_annotation == iter))

	@staticmethod
	def apply(objects, rules):
		rule_idxs = defaultdict(list)
		for i, rs in enumerate(rules.values()):
			for r in rs:
				rule_idxs[r].append(i)

		objects, *ts = tee(objects, len(rule_idxs)+1)
		ts = {r(t): idxs for (r, idxs), t in zip(rule_idxs.items(), ts)}

		def g():
			while True:
				trues = set(chain.from_iterable(idxs for t, idxs in ts.items() if next(t)))
				yield [i in trues for i in range(len(rules))]

		return objects, g()

class ObjectRule(Rule):
	@staticmethod
	def inspect(sig):
		return ( len(sig.parameters) == 1
		       and ( sig.return_annotation == sig.empty
			       or sig.return_annotation == bool ))

	@staticmethod
	def apply(objects, rules):
		objects, t = tee(objects, 2)
		return objects, ([any(r(o) for r in perm_rules)
		                  for perm_rules in rules.values()]
		                 for o in t)
