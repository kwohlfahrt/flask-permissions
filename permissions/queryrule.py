import sqlalchemy.sql.expression as expr
from sqlalchemy.orm.query import Query
from sqlalchemy import or_

from itertools import tee

from .defaulttypes import Rule

class QueryRule(Rule):
	@staticmethod
	def inspect(sig):
		return ( len(sig.parameters) == 0
			   and ( sig.return_annotation == sig.empty
			       or sig.return_annotation == Query ))
			       
	@staticmethod
	def apply(objects, rules):
		try:
			ncols = len(objects.column_descriptions)
			objects = objects.add_columns(*(or_(r() for r in perm_rules)
			                                for perm_rules in rules.values()))
		except AttributeError:
			return objects, [repeat(False)] * len(rules)
		else:
			objects, permissions = tee(objects, 2)
			if ncols > 1:
				return (o[:ncols] for o in objects), (p[ncols:] for p in permissions)
			elif ncols == 1:
				return (o[0] for o in objects), (p[ncols:] for p in permissions)
