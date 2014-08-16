from collections import defaultdict

def invertMapping(m):
	r = defaultdict(set)
	for k, vs in m.items():
		for v in vs:
			r[v].add(k)
	return r
