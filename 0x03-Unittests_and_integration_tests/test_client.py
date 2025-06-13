#!/usr/bin/env python3
"""Unit tests for client module.
This module tests the functionality of the client.py file.
"""
import unittest
from unittest.mock import patch, PropertyMock
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

    def test_public_repos_url(self):
        """Test that _public_repos_url returns the expected URL.

        This method tests that the _public_repos_url property correctly
        returns the repos_url from the org property's payload.
        """
        with patch('client.GithubOrgClient.org',
                   new_callable=PropertyMock) as mock_org:
            # Known payload with repos_url
            test_payload = {
                "repos_url": "https://api.github.com/orgs/google/repos"
            }
            mock_org.return_value = test_payload

            # Create client instance
            client = GithubOrgClient("google")

            # Test that _public_repos_url returns the expected URL
            result = client._public_repos_url
            self.assertEqual(result, test_payload["repos_url"])


if __name__ == '__main__':
    unittest.main()
