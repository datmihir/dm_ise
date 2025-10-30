from django.test import TestCase

from . import processing_logic


class ProcessingLogicTests(TestCase):
	def test_apriori_basic(self):
		dataset = [
			{'A': 'x', 'B': 'u'},
			{'A': 'x', 'B': 'v'},
			{'A': 'y', 'B': 'u'},
			{'A': 'x', 'B': 'u'},
		]
		res = processing_logic.apriori(dataset, ['A', 'B'], min_support=0.25, min_confidence=0.5, max_len=2)
		self.assertIn('frequent_itemsets', res)
		self.assertIn('rules', res)

	def test_pagerank_small(self):
		dataset = [
			{'src': '1', 'dst': '2'},
			{'src': '2', 'dst': '3'},
			{'src': '3', 'dst': '1'},
		]
		res = processing_logic.pagerank_from_edges(dataset, 'src', 'dst', damping=0.85)
		self.assertIn('scores', res)
