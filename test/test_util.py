import unittest

from permissions.util import invertMapping

class TestInvertMapping(unittest.TestCase):
	def test_simple(self):
		d = invertMapping({1: [2], 'foo': [5]})
		self.assertEqual(d, {2: {1}, 5: {'foo'}})
