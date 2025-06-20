#!/usr/bin/env python3
"""Unit tests for utils module.
This module tests the functionality of the utils.py file.
"""
import unittest  # Import Python's built-in testing framework
from unittest.mock import patch  # Import patch for mocking
from parameterized import parameterized  # Import parameterized testing library
from utils import access_nested_map  # Import the function being tested
from utils import get_json  # Import another function to be tested
from utils import memoize  # Import the memoize decorator to be tested


class TestAccessNestedMap(unittest.TestCase):
    """Test class for access_nested_map function."""

    @parameterized.expand([
        # Test cases in format: (nested_map, path, expected_result)
        ({"a": 1}, ("a",), 1),  # Simple case: get value of key "a"
        ({"a": {"b": 2}}, ("a",), {"b": 2}),  # Get nested dict at "a"
        ({"a": {"b": 2}}, ("a", "b"), 2),  # Get value at nested path
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

    @parameterized.expand([
        # Test cases in format: (nested_map, path, expected_key_error)
        ({}, ("a",), "a"),  # Empty dict, trying to access key "a"
        ({"a": 1}, ("a", "b"), "b"),  # Nested access where "b" doesn't exist
    ])
    def test_access_nested_map_exception(self, nested_map, path, expected_key):
        """Test that access_nested_map raises KeyError for invalid paths.

        Args:
            nested_map (dict): The dictionary to extract values from
            path (tuple): Sequence of keys to access nested values
            expected_key: The key that should be in the KeyError message
        """
        # Use assertRaises context manager to check KeyError is raised
        with self.assertRaises(KeyError) as context:
            access_nested_map(nested_map, path)

        # Verify the exception message contains the expected key
        self.assertEqual(str(context.exception), f"'{expected_key}'")


class TestGetJson(unittest.TestCase):
    """Test class for testing get_json function with mocked HTTP requests."""

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

            # Verify the mock was called exactly once with the correct URL
            mock_get.assert_called_once_with(test_url)

            # Verify the function returns the expected payload
            self.assertEqual(result, test_payload)


class TestMemoize(unittest.TestCase):
    """Test class for memoize decorator functionality."""

    def test_memoize(self):
        """Test that memoize decorator caches method results correctly."""

        class TestClass:
            def a_method(self):
                return 42

            @memoize
            def a_property(self):
                return self.a_method()

        # Create an instance of TestClass
        test_obj = TestClass()

        # Mock the a_method to track its calls
        with patch.object(test_obj, 'a_method',
                          return_value=42) as mock_method:
            # Call a_property twice
            result1 = test_obj.a_property
            result2 = test_obj.a_property

            # Verify both calls return the correct result
            self.assertEqual(result1, 42)
            self.assertEqual(result2, 42)

            # Verify a_method was called only once due to memoization
            mock_method.assert_called_once()


if __name__ == '__main__':
    unittest.main()  # Run all tests when this file is executed directly
