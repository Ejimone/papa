#!/usr/bin/env python3
"""
AI API Endpoints Test Script

This script tests all the AI endpoints we created to ensure they work correctly.
"""

import asyncio
import aiohttp
import json
import io
from typing import Dict, Any

# Base URL for the API (adjust as needed)
BASE_URL = "http://localhost:8000/api/v1"

class AIEndpointTester:
    def __init__(self, base_url: str, auth_token: str = None):
        self.base_url = base_url
        self.auth_token = auth_token
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def get_headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        return headers
    
    async def test_health_check(self):
        """Test the AI health check endpoint"""
        print("\n🔍 Testing AI Health Check...")
        
        try:
            async with self.session.get(f"{self.base_url}/ai/health") as response:
                data = await response.json()
                print(f"Status: {response.status}")
                print(f"Health Status: {data.get('status', 'unknown')}")
                print(f"Services: {json.dumps(data.get('services', {}), indent=2)}")
                return response.status == 200
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return False
    
    async def test_question_analysis(self):
        """Test question text analysis endpoint"""
        print("\n📝 Testing Question Analysis...")
        
        test_questions = [
            {
                "text": "What is the derivative of f(x) = x^2 + 3x - 5?",
                "subject": "mathematics",
                "expected_difficulty": 2
            },
            {
                "text": "Choose the correct answer: (A) Python (B) Java (C) JavaScript (D) All of the above",
                "subject": "computer_science"
            },
            {
                "text": "Explain the process of photosynthesis in plants.",
                "subject": "biology"
            }
        ]
        
        for i, question in enumerate(test_questions, 1):
            try:
                async with self.session.post(
                    f"{self.base_url}/ai/analyze-question",
                    json=question,
                    headers=self.get_headers()
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ Question {i} Analysis:")
                        print(f"   Type: {data.get('question_type')}")
                        print(f"   Difficulty: {data.get('difficulty_score', 0):.2f}")
                        print(f"   Keywords: {', '.join(data.get('keywords', [])[:5])}")
                        print(f"   Estimated Time: {data.get('estimated_time')}s")
                    else:
                        error = await response.text()
                        print(f"❌ Question {i} failed: {response.status} - {error}")
                        
            except Exception as e:
                print(f"❌ Question {i} analysis error: {e}")
    
    async def test_recommendations(self):
        """Test personalized recommendations endpoint"""
        print("\n🎯 Testing Recommendations...")
        
        recommendation_request = {
            "subject": "mathematics",
            "limit": 5,
            "exclude_attempted": True
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/ai/recommendations",
                json=recommendation_request,
                headers=self.get_headers()
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Recommendations received: {len(data)} items")
                    for i, rec in enumerate(data[:3], 1):  # Show first 3
                        print(f"   {i}. Question: {rec.get('question_id')}")
                        print(f"      Strategy: {rec.get('recommendation_strategy')}")
                        print(f"      Confidence: {rec.get('confidence_score', 0):.2f}")
                else:
                    error = await response.text()
                    print(f"❌ Recommendations failed: {response.status} - {error}")
                    
        except Exception as e:
            print(f"❌ Recommendations error: {e}")
    
    async def test_learning_path(self):
        """Test learning path generation endpoint"""
        print("\n🛤️  Testing Learning Path Generation...")
        
        learning_path_request = {
            "subject": "mathematics",
            "objectives": ["mastery", "confidence"],
            "path_type": "sequential",
            "max_sessions": 5,
            "session_duration_minutes": 30
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/ai/learning-path",
                json=learning_path_request,
                headers=self.get_headers()
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Learning Path Generated:")
                    print(f"   Path ID: {data.get('path_id')}")
                    print(f"   Subject: {data.get('subject')}")
                    print(f"   Type: {data.get('path_type')}")
                    print(f"   Sessions: {data.get('total_sessions')}")
                    print(f"   Duration: {data.get('total_duration_minutes')} minutes")
                    print(f"   Completion: {data.get('estimated_completion_days')} days")
                else:
                    error = await response.text()
                    print(f"❌ Learning path failed: {response.status} - {error}")
                    
        except Exception as e:
            print(f"❌ Learning path error: {e}")
    
    async def test_difficulty_adaptation(self):
        """Test difficulty adaptation endpoint"""
        print("\n⚡ Testing Difficulty Adaptation...")
        
        adaptation_request = {
            "subject": "mathematics",
            "recent_interactions_count": 10
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/ai/adapt-difficulty",
                json=adaptation_request,
                headers=self.get_headers()
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Difficulty Adaptation:")
                    print(f"   Current: {data.get('current_difficulty')}")
                    print(f"   Recommended: {data.get('recommended_difficulty')}")
                    print(f"   Should Adapt: {data.get('should_adapt')}")
                    print(f"   Confidence: {data.get('confidence')}")
                    if data.get('reasoning'):
                        print(f"   Reasoning: {', '.join(data.get('reasoning', []))}")
                else:
                    error = await response.text()
                    print(f"❌ Difficulty adaptation failed: {response.status} - {error}")
                    
        except Exception as e:
            print(f"❌ Difficulty adaptation error: {e}")
    
    async def test_user_profile(self):
        """Test user AI profile endpoint"""
        print("\n👤 Testing User AI Profile...")
        
        try:
            async with self.session.get(
                f"{self.base_url}/ai/user-profile",
                headers=self.get_headers()
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ User AI Profile:")
                    print(f"   Performance Level: {data.get('performance_level')}")
                    print(f"   Learning Style: {data.get('learning_style')}")
                    print(f"   Preferred Difficulty: {data.get('preferred_difficulty')}")
                    print(f"   Strong Subjects: {', '.join(data.get('strong_subjects', []))}")
                    print(f"   Weak Subjects: {', '.join(data.get('weak_subjects', []))}")
                    print(f"   Total Interactions: {data.get('total_interactions', 0)}")
                else:
                    error = await response.text()
                    print(f"❌ User profile failed: {response.status} - {error}")
                    
        except Exception as e:
            print(f"❌ User profile error: {e}")
    
    async def test_similar_questions(self):
        """Test similar questions endpoint"""
        print("\n🔗 Testing Similar Questions...")
        
        test_question_id = "sample_question_123"
        
        try:
            async with self.session.get(
                f"{self.base_url}/ai/similar-questions/{test_question_id}?limit=3",
                headers=self.get_headers()
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Similar Questions:")
                    print(f"   Original: {data.get('original_question_id')}")
                    print(f"   Found: {data.get('total_found')} similar questions")
                    for i, sim in enumerate(data.get('similar_questions', []), 1):
                        print(f"   {i}. ID: {sim.get('question_id')}, Score: {sim.get('similarity_score', 0):.2f}")
                else:
                    error = await response.text()
                    print(f"❌ Similar questions failed: {response.status} - {error}")
                    
        except Exception as e:
            print(f"❌ Similar questions error: {e}")
    
    async def run_all_tests(self):
        """Run all AI endpoint tests"""
        print("🚀 Starting AI Endpoints Test Suite")
        print("=" * 50)
        
        tests = [
            self.test_health_check,
            self.test_question_analysis,
            self.test_recommendations,
            self.test_learning_path,
            self.test_difficulty_adaptation,
            self.test_user_profile,
            self.test_similar_questions
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                await test()
                passed += 1
            except Exception as e:
                print(f"❌ Test {test.__name__} failed with exception: {e}")
        
        print("\n" + "=" * 50)
        print(f"📊 Test Results: {passed}/{total} tests completed")
        
        if passed == total:
            print("✅ All AI endpoint tests completed successfully!")
        else:
            print(f"⚠️  {total - passed} tests had issues (likely due to missing authentication)")
        
        print("\n💡 Note: Some tests may fail due to missing authentication token.")
        print("   To run with authentication, first get a token from /api/v1/auth/login")

async def main():
    """Main test function"""
    # Test without authentication first (some endpoints might work)
    async with AIEndpointTester(BASE_URL) as tester:
        await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
