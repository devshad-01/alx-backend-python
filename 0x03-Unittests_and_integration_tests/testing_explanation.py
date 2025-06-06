#!/usr/bin/env python3
"""
UNIT TESTING EXPLANATION - Step by Step Guide
==============================================

This file explains unit testing concepts in simple terms with examples.
"""

# 1. WHAT IS UNIT TESTING?
# Unit testing means testing small pieces (units) of your code to make sure they work correctly.

# 2. BASIC EXAMPLE - Testing a simple function
def add_numbers(a, b):
    """Simple function that adds two numbers."""
    return a + b

# To test this function manually, you would do:
# result = add_numbers(2, 3)
# if result == 5:
#     print("Test passed!")
# else:
#     print("Test failed!")

# 3. USING UNITTEST FRAMEWORK
import unittest

class TestAddNumbers(unittest.TestCase):
    """Test class for add_numbers function."""
    
    def test_add_positive_numbers(self):
        """Test adding positive numbers."""
        # Given these inputs
        a = 2
        b = 3
        expected_result = 5
        
        # When we call the function
        actual_result = add_numbers(a, b)
        
        # Then we check if the result is what we expected
        self.assertEqual(actual_result, expected_result)
        # assertEqual means: "check if these two values are equal"

# 4. UNDERSTANDING THE access_nested_map FUNCTION
from utils import access_nested_map

# Let's understand what this function does:
def explain_access_nested_map():
    """Demonstrate how access_nested_map works."""
    
    # Example 1: Simple dictionary
    simple_dict = {"a": 1}
    path = ("a",)  # This is a tuple with one element
    result = access_nested_map(simple_dict, path)
    print(f"Simple case: {simple_dict} with path {path} = {result}")
    
    # Example 2: Nested dictionary - get the inner dictionary
    nested_dict = {"a": {"b": 2}}
    path = ("a",)  # Get what's inside key "a"
    result = access_nested_map(nested_dict, path)
    print(f"Nested case 1: {nested_dict} with path {path} = {result}")
    
    # Example 3: Nested dictionary - get the deepest value
    nested_dict = {"a": {"b": 2}}
    path = ("a", "b")  # First go to "a", then go to "b"
    result = access_nested_map(nested_dict, path)
    print(f"Nested case 2: {nested_dict} with path {path} = {result}")

# 5. UNDERSTANDING PARAMETERIZED TESTS
# Instead of writing 3 separate test methods, we can use @parameterized.expand
# to test multiple cases with the same logic

# WITHOUT parameterized (the long way):
class TestAccessNestedMapLongWay(unittest.TestCase):
    """Example of testing without parameterized - more verbose."""
    
    def test_simple_case(self):
        nested_map = {"a": 1}
        path = ("a",)
        expected = 1
        self.assertEqual(access_nested_map(nested_map, path), expected)
    
    def test_nested_case_1(self):
        nested_map = {"a": {"b": 2}}
        path = ("a",)
        expected = {"b": 2}
        self.assertEqual(access_nested_map(nested_map, path), expected)
    
    def test_nested_case_2(self):
        nested_map = {"a": {"b": 2}}
        path = ("a", "b")
        expected = 2
        self.assertEqual(access_nested_map(nested_map, path), expected)

# WITH parameterized (the short way - what we used in test_utils.py):
from parameterized import parameterized

class TestAccessNestedMapShortWay(unittest.TestCase):
    """Example of testing with parameterized - more concise."""
    
    @parameterized.expand([
        # Each tuple contains: (input1, input2, expected_output)
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2),
    ])
    def test_access_nested_map(self, nested_map, path, expected):
        """One test method that runs multiple test cases."""
        self.assertEqual(access_nested_map(nested_map, path), expected)

# 6. BREAKING DOWN THE SYNTAX

# @parameterized.expand([...])
# This is a DECORATOR - it modifies the function below it
# It tells Python: "run this test function multiple times with different inputs"

# The list contains tuples:
# ({"a": 1}, ("a",), 1)
#  ↑         ↑       ↑
#  input1    input2  expected output

# def test_access_nested_map(self, nested_map, path, expected):
#                             ↑          ↑     ↑
#                             these parameters get the values from each tuple

# self.assertEqual(actual, expected)
# This checks if two values are the same
# If they're different, the test fails

if __name__ == '__main__':
    print("Understanding access_nested_map:")
    explain_access_nested_map()
    print("\nRunning tests...")
    unittest.main()
