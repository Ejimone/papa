#!/usr/bin/env python3
"""
Test JWT authentication endpoints
"""
import requests
import json

BASE_URL = "http://localhost:8001/api/v1"

def test_authenticated_endpoints(access_token, token_type):
    """Test authenticated endpoints with valid token"""
    print("\n2. Testing authenticated endpoint...")
    
    headers = {
        "Authorization": f"{token_type} {access_token}",
        "Content-Type": "application/json"
    }
    
    # Test getting current user profile
    profile_response = requests.get(f"{BASE_URL}/users/me", headers=headers)
    
    if profile_response.status_code == 200:
        user_data = profile_response.json()
        print(f"   ✅ Authenticated request successful!")
        print(f"   • User ID: {user_data['id']}")
        print(f"   • Username: {user_data['username']}")
        print(f"   • Email: {user_data['email']}")
        
        # Test getting user statistics
        print("\n3. Testing user statistics endpoint...")
        stats_response = requests.get(f"{BASE_URL}/users/me/statistics", headers=headers)
        
        if stats_response.status_code == 200:
            stats_data = stats_response.json()
            print(f"   ✅ User statistics retrieved!")
            print(f"   • Total attempts: {stats_data.get('total_attempts', 0)}")
            print(f"   • Average accuracy: {stats_data.get('average_accuracy', 0):.1f}%")
            print(f"   • Total study time: {stats_data.get('total_study_time', 0)} seconds")
            
            # Test user leaderboard
            print("\n4. Testing user leaderboard endpoint...")
            leaderboard_response = requests.get(f"{BASE_URL}/users/leaderboard", headers=headers)
            
            if leaderboard_response.status_code == 200:
                leaderboard_data = leaderboard_response.json()
                print(f"   ✅ Leaderboard retrieved!")
                print(f"   • Leaderboard entries: {len(leaderboard_data)}")
                if leaderboard_data:
                    top_user = leaderboard_data[0]
                    print(f"   • Top user: {top_user['username']} with {top_user['accuracy']:.1f}% accuracy")
            
            else:
                print(f"   ❌ Leaderboard request failed: {leaderboard_response.status_code}")
                print(f"   Response: {leaderboard_response.text}")
            
        else:
            print(f"   ❌ Statistics request failed: {stats_response.status_code}")
            print(f"   Response: {stats_response.text}")
        
    else:
        print(f"   ❌ Authenticated request failed: {profile_response.status_code}")
        print(f"   Response: {profile_response.text}")

def test_registration():
    """Test user registration"""
    print("\n5. Testing user registration...")
    
    register_data = {
        "email": "testuser@example.com",
        "username": "testuser",
        "password": "testpass123",
        "is_active": True
    }
    
    register_response = requests.post(
        f"{BASE_URL}/auth/register",
        json=register_data,
        headers={"Content-Type": "application/json"}
    )
    
    if register_response.status_code in [200, 201]:
        print(f"   ✅ Registration successful!")
        user_data = register_response.json()
        print(f"   • New user ID: {user_data['id']}")
        print(f"   • New username: {user_data['username']}")
        
        # Try login with new user
        print("\n6. Testing login with new user...")
        new_login_data = {
            "email": "testuser@example.com",
            "password": "testpass123"
        }
        
        new_login_response = requests.post(
            f"{BASE_URL}/auth/login",
            json=new_login_data,
            headers={"Content-Type": "application/json"}
        )
        
        if new_login_response.status_code == 200:
            print(f"   ✅ New user login successful!")
            token_data = new_login_response.json()
            test_authenticated_endpoints(token_data["access_token"], token_data["token_type"])
        else:
            print(f"   ❌ New user login failed: {new_login_response.status_code}")
    
    else:
        print(f"   ❌ Registration failed: {register_response.status_code}")
        print(f"   Response: {register_response.text}")

def test_authentication():
    """Test JWT authentication flow"""
    print("🔐 Testing JWT Authentication\n")
    
    # Test data for login
    login_data_json = {
        "email": "john.doe@mit.edu",  # From our sample data - use email instead of username
        "password": "testpass123"
    }
    
    login_data_form = {
        "username": "john.doe@mit.edu",  # OAuth2 expects email as username
        "password": "testpass123"
    }
    
    print("1. Testing user login (JSON endpoint)...")
    
    # Test JSON login endpoint
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json=login_data_json,
        headers={"Content-Type": "application/json"}
    )
    
    if login_response.status_code == 200:
        token_data = login_response.json()
        access_token = token_data["access_token"]
        token_type = token_data["token_type"]
        
        print(f"   ✅ JSON login successful!")
        print(f"   • Token type: {token_type}")
        print(f"   • Access token (first 50 chars): {access_token[:50]}...")
        
        test_authenticated_endpoints(access_token, token_type)
        
    else:
        print(f"   ❌ JSON login failed: {login_response.status_code}")
        print(f"   Response: {login_response.text}")
        
        print("\n1b. Testing user login (OAuth2 token endpoint)...")
        
        # Test OAuth2 token endpoint
        token_response = requests.post(
            f"{BASE_URL}/auth/token",
            data=login_data_form,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if token_response.status_code == 200:
            token_data = token_response.json()
            access_token = token_data["access_token"]
            token_type = token_data["token_type"]
            
            print(f"   ✅ OAuth2 login successful!")
            print(f"   • Token type: {token_type}")
            print(f"   • Access token (first 50 chars): {access_token[:50]}...")
            
            test_authenticated_endpoints(access_token, token_type)
            
        else:
            print(f"   ❌ OAuth2 login failed: {token_response.status_code}")
            print(f"   Response: {token_response.text}")
            test_registration()

if __name__ == "__main__":
    test_authentication()
