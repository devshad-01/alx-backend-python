#!/usr/bin/env python3
"""Unit tests for utils module.
This module tests the functionality of the utils.py file.
"""
import unittest  # Import Python's built-in testing framework
from unittest.mock import patch  # Import patch for mocking
from parameterized import parameterized  # Import parameterized testing library
from utils import access_nested_map  # Import the function being tested
from utils import get_json  # Import another function to be tested


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

class TestGetJson(unittest.TestCase):
    """Test cases for get_json function.
    
    This class contains test methods to verify the correct behavior
    of the get_json function with mocked HTTP calls.
    """

    @parameterized.expand([
        # Test cases in format: (test_url, test_payload)
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False}),
    ])
    def test_get_json(self, test_url, test_payload):
        """Test that get_json returns expected result with mocked requests.
        
        Args:
            test_url (str): The URL to test with
            test_payload (dict): The expected payload to be returned
        """
        # Mock the requests.get method to return a fake response
        with patch('requests.get') as mock_get:
            # Configure the mock to return our test payload
            mock_get.return_value.json.return_value = test_payload
            
            # Call the function being tested
            result = get_json(test_url)
            print(mock_get)
            print(test_payload)
            # Verify the mock was called exactly once with the correct URL
            mock_get.assert_called_once_with(test_url)
            
            # Verify the function returns the expected payload
            self.assertEqual(result, test_payload)
            
if __name__ == '__main__':
    unittest.main()  # Run all tests when this file is executed directly
