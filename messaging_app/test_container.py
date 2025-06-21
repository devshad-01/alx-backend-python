#!/usr/bin/env python3
"""
Test script to verify the containerized Django messaging app is working correctly.
"""

import requests
import sys


def test_django_container():
    """Test various endpoints of the containerized Django app."""
    base_url = "http://localhost:8000"
    
    tests = [
        {
            "name": "Root URL (should return 404)",
            "url": f"{base_url}/",
            "expected_status": 404
        },
        {
            "name": "Admin interface (should redirect to login)",
            "url": f"{base_url}/admin/",
            "expected_status": 302
        },
        {
            "name": "API endpoint (should require authentication)",
            "url": f"{base_url}/api/",
            "expected_status": 401
        }
    ]
    
    print("Testing containerized Django messaging app...")
    print("=" * 50)
    
    all_passed = True
    
    for test in tests:
        try:
            response = requests.get(test["url"], timeout=10)
            if response.status_code == test["expected_status"]:
                print(f"✅ {test['name']}: PASSED (Status: {response.status_code})")
            else:
                print(f"❌ {test['name']}: FAILED (Expected: {test['expected_status']}, Got: {response.status_code})")
                all_passed = False
        except requests.exceptions.RequestException as e:
            print(f"❌ {test['name']}: FAILED (Error: {e})")
            all_passed = False
    
    print("=" * 50)
    
    if all_passed:
        print("🎉 All tests passed! The containerized Django app is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the container and Django configuration.")
        return 1


if __name__ == "__main__":
    sys.exit(test_django_container())
