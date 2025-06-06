import unittest
import practice

class TestCalculator(unittest.TestCase):
    def test_add(self):
        """Test the add function."""
        result = practice.add(2, 3)
        self.assertEqual(result, 5)
if __name__ == '__main__':
    unittest.main()  # Run the tests when this script is executed directly