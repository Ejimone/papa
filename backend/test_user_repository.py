#!/usr/bin/env python3
"""
Test script for User Repository endpoints
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:9000"

def test_endpoint(endpoint, method="GET", data=None, description=""):
    """Test an endpoint and return the result"""
    url = f"{BASE_URL}{endpoint}"
    
    print(f"\n{'='*60}")
    print(f"Testing: {description}")
    print(f"Method: {method}")
    print(f"URL: {url}")
    
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        elif method == "PUT":
            response = requests.put(url, json=data)
        else:
            print(f"Unsupported method: {method}")
            return
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print("Response:")
                print(json.dumps(result, indent=2, default=str))
            except json.JSONDecodeError:
                print("Response (text):")
                print(response.text)
        else:
            print("Error Response:")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to server. Make sure the server is running on port 9000.")
    except Exception as e:
        print(f"ERROR: {str(e)}")

def main():
    print("User Repository API Testing")
    print("=" * 60)
    
    # Test basic endpoints (these should work without authentication)
    test_endpoint("/", description="Root endpoint")
    test_endpoint("/docs", description="API documentation")
    
    # Test user endpoints that require authentication
    # Note: These will likely return 401 Unauthorized without proper authentication
    print("\n" + "="*60)
    print("Testing User Repository Endpoints")
    print("(Note: These may require authentication)")
    
    # Test repository testing endpoint
    test_endpoint("/api/v1/users/test/repository-methods", 
                 description="Repository methods test (requires superuser)")
    
    # Test leaderboard (should work without auth if public)
    test_endpoint("/api/v1/users/leaderboard", 
                 description="User leaderboard")
    
    test_endpoint("/api/v1/users/leaderboard?metric=volume&days=7&limit=5", 
                 description="Volume leaderboard")
    
    # Test search functionality
    test_endpoint("/api/v1/users/search?query=test", 
                 description="Search users")
    
    # Test active users
    test_endpoint("/api/v1/users/active?days=30", 
                 description="Active users in last 30 days")
    
    # Test users by university
    test_endpoint("/api/v1/users/by-university?university=MIT", 
                 description="Users by university")
    
    print("\n" + "="*60)
    print("Testing Complete!")
    print("Note: Many endpoints require authentication.")
    print("To test authenticated endpoints, you would need to:")
    print("1. Create a user account")
    print("2. Login to get an access token")
    print("3. Include the token in the Authorization header")

if __name__ == "__main__":
    main()
