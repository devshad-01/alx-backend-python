#!/usr/bin/env python3
"""Unit tests for utils module.
This module tests the functionality of the utils.py file.
"""
import unittest  # Import Python's built-in testing framework
from parameterized import parameterized  # Import parameterized testing library
from utils import access_nested_map  # Import the function being tested


class TestAccessNestedMap(unittest.TestCase):
    """Test cases for access_nested_map function.
    
    This class contains test methods to verify the correct behavior
    of the access_nested_map function with different inputs.
    """

    @parameterized.expand([
        # Test cases in format: (nested_map, path, expected_result)
        ({"a": 1}, ("a",), 1),  # Simple case: get value of key "a"
        ({"a": {"b": 2}}, ("a",), {"b": 2}),  # Get nested dictionary at key "a"
        ({"a": {"b": 2}}, ("a", "b"), 2),  # Get value at nested path "a" -> "b"
    ])
    def test_access_nested_map(self, nested_map, path, expected):
        """Test that access_nested_map returns expected result.
        
        Args:
            nested_map (dict): The dictionary to extract values from
            path (tuple): Sequence of keys to access nested values
            expected: Expected return value from the function
        """
        # Verify function returns the correct value for the given inputs
        self.assertEqual(access_nested_map(nested_map, path), expected)


if __name__ == '__main__':
    unittest.main()  # Run all tests when this file is executed directly
