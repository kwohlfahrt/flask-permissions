from itertools import repeat, tee, chain
from collections import defaultdict

from .util import invertMapping

from inspect import Signature

class Rule:
	'''A base class for different rule types.

	Sub-classes must define the :py:meth:`inspect` and :py:meth:`apply`
	methods. They may also define the class attribute ``name`` to provide a
	human-readable name that will be used when displaying
	:py:class:`RuleSet` objects.
	'''

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

	@staticmethod
	def inspect(sig: Signature) -> bool:
		'''Checks whether a rule fits into the rule type.
		
		:param inspect.Signature sig: The signature of the rule.
		:return: Whether the rule is of this type.
		:rtype: bool
		'''
		raise NotImplementedError

	@staticmethod
	def apply(objects, rules):
		'''Apply rules (of this type) to objects.

		:param objects: The objects to apply the rules to. The type of
				this group depends on what rules of this type
                                expect.
		:param rules: A group of rules of this type.
		:return: This function returns the objects (though they are not
			 guaranteed to be unchanged) and an iterable that
			 yields for each object whether each rule has passed.
		'''

		raise NotImplementedError

class StaticRule(Rule):
	'''A rule that is independent of the object it is being applied to.'''
	
	name = 'Static Rule'

	@staticmethod
	def inspect(sig):
		'''A rule is assumed to be static if it takes no parameters,
		and it's return-type annotation is :py:class:`bool` if present.
		'''
		return ( len(sig.parameters) == 0
		       and ( sig.return_annotation == sig.empty
		           or sig.return_annotation == bool))

	@staticmethod
	def apply(objects, rules):
		''':rtype: ``type(objects)``, :py:class:`generator`'''
		# TODO: Return True and enable short-circuiting in RuleSet
		return objects, zip(*(repeat(any(r() for r in perm_rules))
		                      for perm_rules in rules.values()))

class IterableRule(Rule):
	'''A rule that is applied to an iterable of objects.

	This type makes heavy use of :py:func:`itertools.tee` so the rules
        should consume objects one at a time.
	'''
	
	name = 'Iterable Rule'

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

	@staticmethod
	def apply(objects, rules):
		''':rtype: :py:func:`itertools.tee`, :py:class:`generator`'''

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
	'''A rule type for rules apply to individual objects.'''

	name = 'Object Rule'

	@staticmethod
	def inspect(sig):
		'''A rule is assumed to apply to individual objects if it takes
		one parameter and it's return-type annotation is
                :py:class:`bool` if present.
		'''
		return ( len(sig.parameters) == 1
		       and ( sig.return_annotation == sig.empty
		           or sig.return_annotation == bool ))

	@staticmethod
	def apply(objects, rules):
		''':rtype: :py:func:`itertools.tee`, :py:class:`generator`'''
		objects, t = tee(objects, 2)
		return objects, ([any(r(o) for r in perm_rules)
		                  for perm_rules in rules.values()]
		                 for o in t)
