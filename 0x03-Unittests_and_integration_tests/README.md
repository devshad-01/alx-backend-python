# 0x03. Unittests and Integration Tests

This project focuses on understanding and implementing unit tests and integration tests in Python using the `unittest` framework and parameterized testing.

## Learning Objectives

At the end of this project, you should be able to explain to anyone, without the help of Google:

- The difference between unit and integration tests
- Common testing patterns such as mocking, parametrizations and fixtures
- How to write unit tests for functions that make external API calls
- How to write integration tests
- How to use the `unittest` framework
- How to use the `parameterized` library for parameterized testing

## Requirements

- All your files will be interpreted/compiled on Ubuntu 18.04 LTS using python3 (version 3.7)
- All your files should end with a new line
- The first line of all your files should be exactly `#!/usr/bin/env python3`
- Your code should use the pycodestyle style (version 2.5)
- All your files must be executable
- All your modules should have a documentation
- All your classes should have a documentation
- All your functions (inside and outside a class) should have a documentation
- All your functions and coroutines must be type-annotated

## Files

### `utils.py`

Contains utility functions for the GitHub organization client:

- `access_nested_map`: Access nested map with key path
- `get_json`: Get JSON from remote URL
- `memoize`: Decorator to memoize a method

### `test_utils.py`

Contains unit tests for the utility functions:

- `TestAccessNestedMap`: Test cases for the `access_nested_map` function

## Usage

To run the tests:

```bash
python -m unittest test_utils.py
```

To run specific test class:

```bash
python -m unittest test_utils.TestAccessNestedMap
```

## Dependencies

- `unittest` (built-in)
- `parameterized` (external library)
- `requests` (for HTTP requests)

Install external dependencies:

```bash
pip install parameterized requests
```

## Author

ALX Backend Python - Unittests and Integration Tests Project
