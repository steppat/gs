import gs
import unittest


class CommitStatsTest(unittest.TestCase):

	def test_true(self):
		self.assertEqual(1,1)

	def test_non_integer(self):                                        
        	"""toRoman should fail with non-integer input"""             
        	self.assertRaises(None)


if __name__ == "__main__":
    unittest.main() 
