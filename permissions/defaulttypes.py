from itertools import repeat, tee, count
from collections import defaultdict, MutableMapping

from inspect import Signature

class RuleTypeSet(MutableMapping):
	'''A class containing rules of a single type.

	Rules contained in an instance of this class will be applied together,
	using the class's :py:meth:`apply` method.

	Sub-classes must define the :py:meth:`inspect` and :py:meth:`apply`
	methods.
	'''

	def __init__(self):
		self.rules = defaultdict(set)

	def __len__(self):
		return len(self.rules)

	def __iter__(self):
		return iter(self.rules)

	def __delitem__(self, key, value):
		del self.rules[key]

	def __setitem__(self, key, value):
		self.rules[key] = {value}

	def __getitem__(self, key):
		if '*' in key:
			raise KeyError("Key contains '*'")
		partial_key = []
		item = set()
		for k in key:
			item |= self.rules.get(tuple(partial_key + ['*']), set())
			partial_key.append(k)
		item |= self.rules.get(tuple(key), set())
		return item

	def update(self, other):
		for key, rules in other.items():
			self.rules[key] |= rules
	
	def __eq__(self, other):
		return type(self) == type(other) and self.rules == other.rules
	
	def __repr__(self):
		return "<{} {}>".format(type(self).__name__, self.rules)

	def by_rule(self, *keys):
		'''Returns a dictionary of rules for a number of keys, along
		with which keys each rule satisfies. Useful to prevent
		executing a rule more often than necessary.
		'''

		rules = {}
		for key in keys:
			for r in self[key]:
				rules.setdefault(r, set()).add(key)
		return rules

	@staticmethod
	def inspect(sig: Signature) -> bool:
		'''Checks whether a rule fits into this rule type.
		
		:param inspect.Signature sig: The signature of the rule.
		:return: Whether the rule is of this type.
		:rtype: bool
		'''
		raise NotImplementedError

	def apply(self, objects, *keys):
		'''Apply the rules matching ``*keys`` to ``objects``

		:param objects: The objects to apply the rules to.
		:param keys: They keys to search for in this set.
		:return: This function returns the objects (though they are not
			 guaranteed to be unchanged) and an iterable that
			 yields for each object a tuple contianing  whether
		         each rule has passed.
		'''
		raise NotImplementedError

class StaticRuleSet(RuleTypeSet):
	'''A set containing rules independent of the object they are applied to.'''

	@staticmethod
	def inspect(sig):
		'''A rule is assumed to be static if it takes no parameters,
		and it's return-type annotation is :py:class:`bool` if present.
		'''
		return ( len(sig.parameters) == 0
		       and ( sig.return_annotation == sig.empty
		           or sig.return_annotation == bool))

	def apply(self, objects, *keys):
		'''Returns ``objects`` untouched, and an *infinitely* repeating
		generator of tuples
		'''
		# TODO: Return True and enable short-circuiting in RuleSet?

		rules = self.by_rule(*keys)

		# set.union fails if passed no arguments, so add set()
		granted = set.union(set(), *(v for k,v in rules.items() if k()))
		return objects, repeat(tuple(key in granted for key in keys))

class IterableRuleSet(RuleTypeSet):
	'''A set for rules applied to an iterable of objects.

	This type makes heavy use of :py:func:`itertools.tee` so the rules
        should consume objects one at a time.
	'''

	@staticmethod
	def inspect(sig):
		'''A rule is assumed to apply to iterables if it takes one
                parameter with the name `objects` or the annotation
		:py:class:`iter`, and it's return-type annotation is
                :py:class:`iter` if present.
		'''
		if len(sig.parameters) != 1:
			return False
		p = next(iter(sig.parameters.values()))
		return ( ( p.annotation == iter
		         or p.name == 'objects') 
			   and ( sig.return_annotation == sig.empty
			       or sig.return_annotation == iter))

	def apply(self, objects, *keys):
		''':rtype: :py:func:`itertools.tee`, :py:class:`generator`'''

		rules = self.by_rule(*keys)
		objects, *ts = tee(objects, len(rules)+1)

		rules = {r(t): ks for (r, ks), t in zip(rules.items(), ts)}

		return objects, ((k in trues for k in keys) for trues in (set.union(set(), *(v for r,v in rules.items() if next(r))) for _ in count()))

class ObjectRuleSet(RuleTypeSet):
	'''A set of rules that are applied to individual objects.'''

	@staticmethod
	def inspect(sig):
		'''A rule is assumed to apply to individual objects if it takes
		one parameter and it's return-type annotation is
                :py:class:`bool` if present.
		'''
		return ( len(sig.parameters) == 1
		       and ( sig.return_annotation == sig.empty
		           or sig.return_annotation == bool ))

	def apply(self, objects, *keys):
		''':rtype: :py:func:`itertools.tee`, :py:class:`generator`'''

		rules = self.by_rule(*keys)
		objects, t = tee(objects, 2)

		return objects, ((k in trues for k in keys) for trues in (set.union(set(), *(v for r,v in rules.items() if r(o))) for o in t))
