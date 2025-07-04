#!/usr/bin/env python3
"""Unit tests for client module.
This module tests the functionality of the client.py file.
"""
import unittest
from unittest.mock import patch, PropertyMock
from parameterized import parameterized, parameterized_class
from client import GithubOrgClient
from fixtures import TEST_PAYLOAD


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

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json):
        """Test that public_repos returns expected repo names.

        This method tests that the public_repos method correctly returns
        a list of repository names from the mocked JSON payload.
        """
        # Test payload with repo data
        test_repos_payload = [
            {"name": "repo1", "license": {"key": "mit"}},
            {"name": "repo2", "license": {"key": "apache-2.0"}},
            {"name": "repo3", "license": None}
        ]
        mock_get_json.return_value = test_repos_payload

        with patch('client.GithubOrgClient._public_repos_url',
                   new_callable=PropertyMock) as mock_repos_url:
            test_url = "https://api.github.com/orgs/testorg/repos"
            mock_repos_url.return_value = test_url

            # Create client instance
            client = GithubOrgClient("testorg")

            # Call public_repos method
            result = client.public_repos()

            # Expected repo names
            expected_repos = ["repo1", "repo2", "repo3"]

            # Test that the result matches expected repo names
            self.assertEqual(result, expected_repos)

            # Test that _public_repos_url property was called once
            mock_repos_url.assert_called_once()

            # Test that get_json was called once with the expected URL
            mock_get_json.assert_called_once_with(test_url)

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected):
        """Test that has_license returns expected boolean value.

        This method tests that the has_license static method correctly
        determines if a repository has a specific license.

        Args:
            repo (dict): Repository data with license information
            license_key (str): License key to check for
            expected (bool): Expected return value
        """
        # Call the static method
        result = GithubOrgClient.has_license(repo, license_key)

        # Test that the result matches expected value
        self.assertEqual(result, expected)


@parameterized_class(
    ("org_payload", "repos_payload", "expected_repos", "apache2_repos"),
    TEST_PAYLOAD
)
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration test class for GithubOrgClient."""

    @classmethod
    def setUpClass(cls):
        """Set up class fixtures before running tests.

        This method mocks requests.get to return example payloads
        found in the fixtures, avoiding external HTTP requests.
        """
        # Define the side effect function for requests.get
        def side_effect(url):
            # Create a mock response object
            mock_response = unittest.mock.Mock()

            # Return org_payload for organization URL
            if url == "https://api.github.com/orgs/google":
                mock_response.json.return_value = cls.org_payload
            # Return repos_payload for repos URL
            elif url == cls.org_payload["repos_url"]:
                mock_response.json.return_value = cls.repos_payload
            else:
                mock_response.json.return_value = {}

            return mock_response

        # Start the patcher for requests.get
        cls.get_patcher = patch('requests.get', side_effect=side_effect)
        cls.get_patcher.start()

    @classmethod
    def tearDownClass(cls):
        """Tear down class fixtures after running tests.

        This method stops the patcher to clean up mocked requests.
        """
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Test that public_repos returns expected repositories.

        This integration test verifies that the public_repos method
        returns the expected list of repository names from the fixtures.
        """
        # Create client instance
        client = GithubOrgClient("google")

        # Call public_repos method (no license filter)
        result = client.public_repos()

        # Test that the result matches the expected repos from fixtures
        self.assertEqual(result, self.expected_repos)

    def test_public_repos_with_license(self):
        """Test that public_repos with license filter returns expected repos.

        This integration test verifies that the public_repos method
        correctly filters repositories by license and returns the
        expected apache-2.0 licensed repositories from the fixtures.
        """
        # Create client instance
        client = GithubOrgClient("google")

        # Call public_repos method with apache-2.0 license filter
        result = client.public_repos(license="apache-2.0")

        # Test that the result matches the expected apache2_repos from fixtures
        self.assertEqual(result, self.apache2_repos)


if __name__ == '__main__':
    unittest.main()
