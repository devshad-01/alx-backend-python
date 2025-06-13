#!/usr/bin/env python3
"""Unit tests for client module.
This module tests the functionality of the client.py file.
"""
import unittest
from unittest.mock import patch
from parameterized import parameterized
from client import GithubOrgClient


class TestGithubOrgClient(unittest.TestCase):
    """Test class for GithubOrgClient class."""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch('client.get_json')
    def test_org(self, org_name, mock_get_json):
        """Test that GithubOrgClient.org returns the correct value.

        Args:
            org_name (str): The organization name to test with
            mock_get_json: Mocked get_json function
        """
        # Expected URL format
        expected_url = f"https://api.github.com/orgs/{org_name}"

        # Mock return value
        expected_result = {"login": org_name, "id": 12345}
        mock_get_json.return_value = expected_result

        # Create client instance and call org method
        client = GithubOrgClient(org_name)
        result = client.org

        # Verify get_json was called once with correct URL
        mock_get_json.assert_called_once_with(expected_url)

        # Verify the result matches expected
        self.assertEqual(result, expected_result)


if __name__ == '__main__':
    unittest.main()
