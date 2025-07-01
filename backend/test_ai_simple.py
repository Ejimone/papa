#!/usr/bin/env python3
"""
Simple AI API Endpoints Test Script

This script provides a basic test for our AI endpoints using requests library.
"""

import requests
import json
import sys
from typing import Dict, Any

# Base URL for the API (adjust as needed)
BASE_URL = "http://localhost:8000/api/v1"

class SimpleAITester:
    def __init__(self, base_url: str, auth_token: str = None):
        self.base_url = base_url
        self.auth_token = auth_token
        self.session = requests.Session()
    
    def get_headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        return headers
    
    def test_health_check(self):
        """Test the AI health check endpoint"""
        print("\n🔍 Testing AI Health Check...")
        
        try:
            response = self.session.get(f"{self.base_url}/ai/health")
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health Status: {data.get('status', 'unknown')}")
                print(f"Services: {json.dumps(data.get('services', {}), indent=2)}")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection failed: Is the server running on localhost:8000?")
            return False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False
    
    def test_question_analysis(self):
        """Test question text analysis endpoint"""
        print("\n📝 Testing Question Analysis...")
        
        test_question = {
            "text": "What is the derivative of f(x) = x^2 + 3x - 5?",
            "subject": "mathematics"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/ai/analyze-question",
                json=test_question,
                headers=self.get_headers()
            )
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Question Analysis:")
                print(f"   Type: {data.get('question_type')}")
                print(f"   Difficulty: {data.get('difficulty_score', 0):.2f}")
                print(f"   Keywords: {', '.join(data.get('keywords', [])[:5])}")
                print(f"   Estimated Time: {data.get('estimated_time')}s")
                return True
            else:
                print(f"❌ Analysis failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Question analysis error: {e}")
            return False
    
    def test_recommendations(self):
        """Test personalized recommendations endpoint"""
        print("\n🎯 Testing Recommendations...")
        
        recommendation_request = {
            "subject": "mathematics",
            "limit": 5,
            "exclude_attempted": True
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/ai/recommendations",
                json=recommendation_request,
                headers=self.get_headers()
            )
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Recommendations received: {len(data)} items")
                if data:
                    for i, rec in enumerate(data[:3], 1):  # Show first 3
                        print(f"   {i}. Strategy: {rec.get('recommendation_strategy')}")
                        print(f"      Confidence: {rec.get('confidence_score', 0):.2f}")
                return True
            else:
                print(f"❌ Recommendations failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Recommendations error: {e}")
            return False
    
    def test_user_profile(self):
        """Test user AI profile endpoint"""
        print("\n👤 Testing User AI Profile...")
        
        try:
            response = self.session.get(
                f"{self.base_url}/ai/user-profile",
                headers=self.get_headers()
            )
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ User AI Profile:")
                print(f"   Performance Level: {data.get('performance_level')}")
                print(f"   Learning Style: {data.get('learning_style')}")
                print(f"   Preferred Difficulty: {data.get('preferred_difficulty')}")
                return True
            else:
                print(f"❌ User profile failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ User profile error: {e}")
            return False
    
    def run_basic_tests(self):
        """Run basic AI endpoint tests"""
        print("🚀 Starting Basic AI Endpoints Test")
        print("=" * 50)
        
        # Test server connectivity first
        if not self.test_health_check():
            print("\n❌ Server is not running or not accessible.")
            print("💡 To start the server, run: python backend/run.py")
            return False
        
        tests = [
            ("Question Analysis", self.test_question_analysis),
            ("Recommendations", self.test_recommendations),
            ("User Profile", self.test_user_profile),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed += 1
                    print(f"✅ {test_name}: PASSED")
                else:
                    print(f"❌ {test_name}: FAILED")
            except Exception as e:
                print(f"❌ {test_name}: ERROR - {e}")
        
        print("\n" + "=" * 50)
        print(f"📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed successfully!")
        else:
            print(f"⚠️  {total - passed} tests failed")
            print("💡 Note: Some failures may be due to missing authentication or test data")
        
        return passed == total

def main():
    """Main test function"""
    print("AI-Powered Past Questions App - API Test Suite")
    print("=" * 60)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--with-auth":
        token = input("Enter your auth token (or press Enter to skip): ").strip()
        tester = SimpleAITester(BASE_URL, token if token else None)
    else:
        print("Running tests without authentication...")
        print("Use --with-auth flag to test with authentication")
        tester = SimpleAITester(BASE_URL)
    
    success = tester.run_basic_tests()
    
    if not success:
        print("\n📋 Troubleshooting:")
        print("1. Make sure the FastAPI server is running: python backend/run.py")
        print("2. Check that all dependencies are installed")
        print("3. Verify database connection and environment variables")
        print("4. For authenticated endpoints, get a token from /api/v1/auth/login")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
