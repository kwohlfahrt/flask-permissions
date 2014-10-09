from sqlalchemy.sql.expression import bindparam
from sqlalchemy.orm.query import Query
from sqlalchemy import or_

from itertools import tee

from .defaulttypes import RuleTypeSet

false_rule = lambda: bindparam('false', False)

class QueryRuleSet(RuleTypeSet):
	@staticmethod
	def inspect(sig):
		return ( len(sig.parameters) == 0
		       and ( sig.return_annotation == sig.empty
		           or sig.return_annotation == Query ))
			       
	def apply(self, objects, *keys):
		ncols = len(objects.column_descriptions)
		objects = objects.add_columns(*(or_(r() for r in self[key] or [false_rule])
						for key in keys))

		objects, permissions = tee(objects, 2)
		if ncols > 1:
			return ((o[:ncols] for o in objects),
			        (p[ncols:] for p in permissions))
		elif ncols == 1:
			return ((o[0] for o in objects),
			        (p[ncols:] for p in permissions))
