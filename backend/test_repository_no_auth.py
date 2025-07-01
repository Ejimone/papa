#!/usr/bin/env python3
"""
Test script for user repository endpoints without authentication.
"""
import requests
import json

BASE_URL = "http://127.0.0.1:9000"

def test_endpoint(endpoint, method="GET", params=None, data=None):
    """Test an endpoint and return the response."""
    try:
        if method == "GET":
            response = requests.get(f"{BASE_URL}{endpoint}", params=params)
        elif method == "POST":
            response = requests.post(f"{BASE_URL}{endpoint}", json=data, params=params)
        
        print(f"\n{'='*60}")
        print(f"Testing: {method} {endpoint}")
        if params:
            print(f"Params: {params}")
        if data:
            print(f"Data: {json.dumps(data, indent=2)}")
        print(f"Status: {response.status_code}")
        
        try:
            response_json = response.json()
            print(f"Response: {json.dumps(response_json, indent=2, default=str)}")
        except:
            print(f"Response Text: {response.text}")
        
        return response
    except Exception as e:
        print(f"Error testing {endpoint}: {e}")
        return None

def main():
    print("Testing Past Questions App - User Repository Endpoints")
    print("Testing endpoints that don't require authentication...")
    
    # Test basic connectivity
    print(f"\n{'='*60}")
    print("1. Testing basic connectivity...")
    response = test_endpoint("/")
    
    # Test database status
    print(f"\n{'='*60}")
    print("2. Testing database connection...")
    response = test_endpoint("/api/v1/test/database/status")
    
    # Test user repository methods
    print(f"\n{'='*60}")
    print("3. Testing user repository methods...")
    response = test_endpoint("/api/v1/test/repository/user/methods")
    
    # Create sample user if needed
    print(f"\n{'='*60}")
    print("4. Creating sample user...")
    response = test_endpoint("/api/v1/test/repository/user/create-sample")
    
    # Test leaderboard
    print(f"\n{'='*60}")
    print("5. Testing leaderboard...")
    response = test_endpoint("/api/v1/test/repository/user/leaderboard", params={
        "metric": "accuracy",
        "days": 30,
        "limit": 5
    })
    
    # Test search
    print(f"\n{'='*60}")
    print("6. Testing user search...")
    response = test_endpoint("/api/v1/test/repository/user/search", params={
        "query": "test",
        "limit": 5
    })
    
    # Test active users
    print(f"\n{'='*60}")
    print("7. Testing active users...")
    response = test_endpoint("/api/v1/test/repository/user/active", params={
        "days": 30,
        "limit": 5
    })
    
    # Test users by university
    print(f"\n{'='*60}")
    print("8. Testing users by university...")
    response = test_endpoint("/api/v1/test/repository/user/by-university", params={
        "university": "MIT",
        "limit": 5
    })
    
    print(f"\n{'='*60}")
    print("Testing complete!")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
