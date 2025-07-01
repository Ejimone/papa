#!/usr/bin/env python3
"""
Comprehensive endpoint testing script for the AI-Powered Past Questions App
Tests all major endpoints and their functionality.
"""

import asyncio
import httpx
import json
from typing import Dict, Any, Optional
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Test configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

class EndpointTester:
    def __init__(self):
        self.client = httpx.AsyncClient(base_url=BASE_URL, timeout=30.0)
        self.auth_token = None
        self.test_user_id = None
        self.test_subject_id = None
        self.test_question_id = None
        self.test_session_id = None
        
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    def print_test_result(self, test_name: str, success: bool, details: str = ""):
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   {details}")
        print()
    
    async def test_server_health(self):
        """Test if the server is running and responsive"""
        try:
            response = await self.client.get("/")
            success = response.status_code in [200, 404]  # 404 is OK, means server is running
            self.print_test_result("Server Health Check", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.print_test_result("Server Health Check", False, f"Error: {str(e)}")
            return False
    
    async def test_docs_endpoint(self):
        """Test if the API documentation is accessible"""
        try:
            response = await self.client.get("/docs")
            success = response.status_code == 200
            self.print_test_result("API Documentation", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.print_test_result("API Documentation", False, f"Error: {str(e)}")
            return False
    
    async def authenticate(self):
        """Authenticate and get a test token"""
        try:
            # First, try to create a test user
            user_data = {
                "email": "test@example.com",
                "password": "testpassword123",
                "full_name": "Test User"
            }
            
            # Try to register (might fail if user exists)
            register_response = await self.client.post(f"{API_BASE}/auth/register", json=user_data)
            
            # Try to login
            login_data = {
                "username": user_data["email"],
                "password": user_data["password"]
            }
            
            login_response = await self.client.post(f"{API_BASE}/auth/login", data=login_data)
            
            if login_response.status_code == 200:
                token_data = login_response.json()
                self.auth_token = token_data.get("access_token")
                self.print_test_result("Authentication", True, "Successfully authenticated")
                return True
            else:
                self.print_test_result("Authentication", False, f"Login failed: {login_response.status_code}")
                return False
                
        except Exception as e:
            self.print_test_result("Authentication", False, f"Error: {str(e)}")
            return False
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers"""
        if self.auth_token:
            return {"Authorization": f"Bearer {self.auth_token}"}
        return {}
    
    async def test_subjects_endpoints(self):
        """Test subjects and topics endpoints"""
        headers = self.get_auth_headers()
        
        try:
            # Test GET /subjects
            response = await self.client.get(f"{API_BASE}/subjects")
            success = response.status_code == 200
            self.print_test_result("GET /subjects", success, f"Status: {response.status_code}")
            
            if success:
                subjects = response.json()
                print(f"   Found {len(subjects)} subjects")
                if subjects:
                    self.test_subject_id = subjects[0]["id"]
            
            # Test subjects search
            search_response = await self.client.get(f"{API_BASE}/subjects/search?q=math")
            success = search_response.status_code == 200
            self.print_test_result("GET /subjects/search", success, f"Status: {search_response.status_code}")
            
            # Test subjects with topics
            topics_response = await self.client.get(f"{API_BASE}/subjects/with-topics")
            success = topics_response.status_code == 200
            self.print_test_result("GET /subjects/with-topics", success, f"Status: {topics_response.status_code}")
            
            # Test topics search
            topic_search_response = await self.client.get(f"{API_BASE}/subjects/topics/search?q=algebra")
            success = topic_search_response.status_code == 200
            self.print_test_result("GET /subjects/topics/search", success, f"Status: {topic_search_response.status_code}")
            
            return True
            
        except Exception as e:
            self.print_test_result("Subjects Endpoints", False, f"Error: {str(e)}")
            return False
    
    async def test_questions_endpoints(self):
        """Test questions endpoints"""
        try:
            # Test GET /questions
            response = await self.client.get(f"{API_BASE}/questions")
            success = response.status_code == 200
            self.print_test_result("GET /questions", success, f"Status: {response.status_code}")
            
            if success:
                questions = response.json()
                print(f"   Found {len(questions)} questions")
                if questions:
                    self.test_question_id = questions[0]["id"]
            
            # Test questions search
            search_response = await self.client.get(f"{API_BASE}/questions/search?q=algebra")
            success = search_response.status_code == 200
            self.print_test_result("GET /questions/search", success, f"Status: {search_response.status_code}")
            
            # Test random questions
            random_response = await self.client.get(f"{API_BASE}/questions/random?count=5")
            success = random_response.status_code == 200
            self.print_test_result("GET /questions/random", success, f"Status: {random_response.status_code}")
            
            # Test question stats
            stats_response = await self.client.get(f"{API_BASE}/questions/stats")
            success = stats_response.status_code == 200
            self.print_test_result("GET /questions/stats", success, f"Status: {stats_response.status_code}")
            
            if success:
                stats = stats_response.json()
                print(f"   Total questions: {stats.get('total_questions', 0)}")
            
            # Test specific question if we have an ID
            if self.test_question_id:
                question_response = await self.client.get(f"{API_BASE}/questions/{self.test_question_id}")
                success = question_response.status_code == 200
                self.print_test_result(f"GET /questions/{self.test_question_id}", success, f"Status: {question_response.status_code}")
            
            return True
            
        except Exception as e:
            self.print_test_result("Questions Endpoints", False, f"Error: {str(e)}")
            return False
    
    async def test_search_endpoints(self):
        """Test search endpoints"""
        try:
            # Test question search
            response = await self.client.get(f"{API_BASE}/search/questions?q=algebra")
            success = response.status_code == 200
            self.print_test_result("GET /search/questions", success, f"Status: {response.status_code}")
            
            # Test subjects-topics search
            subjects_response = await self.client.get(f"{API_BASE}/search/subjects-topics?q=math")
            success = subjects_response.status_code == 200
            self.print_test_result("GET /search/subjects-topics", success, f"Status: {subjects_response.status_code}")
            
            # Test search suggestions
            suggestions_response = await self.client.get(f"{API_BASE}/search/suggestions?q=alg")
            success = suggestions_response.status_code == 200
            self.print_test_result("GET /search/suggestions", success, f"Status: {suggestions_response.status_code}")
            
            # Test popular searches
            popular_response = await self.client.get(f"{API_BASE}/search/popular")
            success = popular_response.status_code == 200
            self.print_test_result("GET /search/popular", success, f"Status: {popular_response.status_code}")
            
            # Test filter options
            filters_response = await self.client.get(f"{API_BASE}/search/filters/options")
            success = filters_response.status_code == 200
            self.print_test_result("GET /search/filters/options", success, f"Status: {filters_response.status_code}")
            
            # Test autocomplete
            autocomplete_response = await self.client.get(f"{API_BASE}/search/autocomplete?q=algebra")
            success = autocomplete_response.status_code == 200
            self.print_test_result("GET /search/autocomplete", success, f"Status: {autocomplete_response.status_code}")
            
            return True
            
        except Exception as e:
            self.print_test_result("Search Endpoints", False, f"Error: {str(e)}")
            return False
    
    async def test_practice_endpoints(self):
        """Test practice endpoints (requires authentication)"""
        headers = self.get_auth_headers()
        
        if not headers:
            self.print_test_result("Practice Endpoints", False, "No authentication token available")
            return False
        
        try:
            # Test GET practice sessions
            response = await self.client.get(f"{API_BASE}/practice/sessions", headers=headers)
            success = response.status_code == 200
            self.print_test_result("GET /practice/sessions", success, f"Status: {response.status_code}")
            
            # Test GET practice progress
            progress_response = await self.client.get(f"{API_BASE}/practice/progress", headers=headers)
            success = progress_response.status_code == 200
            self.print_test_result("GET /practice/progress", success, f"Status: {progress_response.status_code}")
            
            # Test GET practice stats
            stats_response = await self.client.get(f"{API_BASE}/practice/stats", headers=headers)
            success = stats_response.status_code == 200
            self.print_test_result("GET /practice/stats", success, f"Status: {stats_response.status_code}")
            
            # Test GET user attempts
            attempts_response = await self.client.get(f"{API_BASE}/practice/attempts", headers=headers)
            success = attempts_response.status_code == 200
            self.print_test_result("GET /practice/attempts", success, f"Status: {attempts_response.status_code}")
            
            # Test GET bookmarks
            bookmarks_response = await self.client.get(f"{API_BASE}/practice/bookmarks", headers=headers)
            success = bookmarks_response.status_code == 200
            self.print_test_result("GET /practice/bookmarks", success, f"Status: {bookmarks_response.status_code}")
            
            return True
            
        except Exception as e:
            self.print_test_result("Practice Endpoints", False, f"Error: {str(e)}")
            return False
    
    async def test_analytics_endpoints(self):
        """Test analytics endpoints (requires authentication)"""
        headers = self.get_auth_headers()
        
        if not headers:
            self.print_test_result("Analytics Endpoints", False, "No authentication token available")
            return False
        
        try:
            # Test dashboard data
            response = await self.client.get(f"{API_BASE}/analytics/dashboard", headers=headers)
            success = response.status_code == 200
            self.print_test_result("GET /analytics/dashboard", success, f"Status: {response.status_code}")
            
            # Test user analytics
            analytics_response = await self.client.get(f"{API_BASE}/analytics/user-analytics", headers=headers)
            # This might return 404 if no analytics exist yet, which is OK
            success = analytics_response.status_code in [200, 404]
            self.print_test_result("GET /analytics/user-analytics", success, f"Status: {analytics_response.status_code}")
            
            # Test performance trends
            trends_response = await self.client.get(f"{API_BASE}/analytics/performance-trends", headers=headers)
            success = trends_response.status_code == 200
            self.print_test_result("GET /analytics/performance-trends", success, f"Status: {trends_response.status_code}")
            
            # Test weekly activity
            weekly_response = await self.client.get(f"{API_BASE}/analytics/weekly-activity", headers=headers)
            success = weekly_response.status_code == 200
            self.print_test_result("GET /analytics/weekly-activity", success, f"Status: {weekly_response.status_code}")
            
            # Test learning insights
            insights_response = await self.client.get(f"{API_BASE}/analytics/learning-insights", headers=headers)
            success = insights_response.status_code == 200
            self.print_test_result("GET /analytics/learning-insights", success, f"Status: {insights_response.status_code}")
            
            return True
            
        except Exception as e:
            self.print_test_result("Analytics Endpoints", False, f"Error: {str(e)}")
            return False
    
    async def test_admin_endpoints(self):
        """Test admin endpoints (requires authentication and admin privileges)"""
        headers = self.get_auth_headers()
        
        if not headers:
            self.print_test_result("Admin Endpoints", False, "No authentication token available")
            return False
        
        try:
            # Test admin dashboard (might fail if user is not admin)
            response = await self.client.get(f"{API_BASE}/admin/dashboard", headers=headers)
            success = response.status_code in [200, 403]  # 403 is OK if not admin
            status_msg = "Admin access" if response.status_code == 200 else "Non-admin user (expected)"
            self.print_test_result("GET /admin/dashboard", success, f"Status: {response.status_code} - {status_msg}")
            
            return True
            
        except Exception as e:
            self.print_test_result("Admin Endpoints", False, f"Error: {str(e)}")
            return False
    
    async def run_all_tests(self):
        """Run all endpoint tests"""
        print("🚀 Starting Comprehensive Endpoint Testing\n")
        print("=" * 50)
        
        # Basic server tests
        if not await self.test_server_health():
            print("❌ Server is not running. Please start the server first.")
            return False
        
        await self.test_docs_endpoint()
        
        # Authentication test
        auth_success = await self.authenticate()
        
        # Core endpoint tests
        await self.test_subjects_endpoints()
        await self.test_questions_endpoints()
        await self.test_search_endpoints()
        
        # Authenticated endpoint tests
        if auth_success:
            await self.test_practice_endpoints()
            await self.test_analytics_endpoints()
            await self.test_admin_endpoints()
        else:
            print("⚠️  Skipping authenticated endpoints due to authentication failure")
        
        print("=" * 50)
        print("🏁 Testing Complete!")
        return True

async def main():
    """Main test function"""
    async with EndpointTester() as tester:
        await tester.run_all_tests()

if __name__ == "__main__":
    print("🧪 AI-Powered Past Questions App - Endpoint Testing")
    print("📝 This script will test all endpoints and their functionality\n")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⏹️  Testing interrupted by user")
    except Exception as e:
        print(f"\n\n💥 Unexpected error: {str(e)}")
        sys.exit(1) 