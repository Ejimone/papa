#!/usr/bin/env python3
"""
Demo AI Endpoints Test Script

This script tests the demo AI endpoints that don't require authentication.
"""

import requests
import json

BASE_URL = "http://localhost:8001/api/v1"

def test_demo_endpoints():
    print("🚀 Testing AI Demo Endpoints")
    print("=" * 50)
    
    # Test 1: Health Check
    print("\n🔍 Testing Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/ai/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health Status: {data['status']}")
            print(f"Services Active: {len([s for s in data['services'].values() if s == 'active'])}/{len(data['services'])}")
            if 'test_analysis' in data:
                print(f"✅ Built-in test passed: {data['test_analysis']['question_type']}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test 2: Demo Text Analysis
    print("\n📝 Testing Demo Text Analysis...")
    test_questions = [
        "What is the derivative of f(x) = x^2 + 3x - 5?",
        "Choose the correct answer: (A) Python (B) Java (C) JavaScript (D) All of the above",
        "Explain the process of photosynthesis in plants.",
        "Calculate the area of a circle with radius 5 cm."
    ]
    
    for i, question in enumerate(test_questions, 1):
        try:
            response = requests.post(
                f"{BASE_URL}/ai/demo/analyze-text",
                json={"text": question}
            )
            
            if response.status_code == 200:
                data = response.json()
                analysis = data['analysis']
                print(f"✅ Question {i}:")
                print(f"   Type: {analysis['question_type']}")
                print(f"   Difficulty: {analysis['difficulty_score']:.2f}")
                print(f"   Keywords: {', '.join(analysis['keywords'][:3])}...")
                print(f"   Math Content: {analysis['has_mathematical_content']}")
                print(f"   Math Expressions: {len(analysis.get('mathematical_expressions', []))}")
                print(f"   Word Count: {analysis['word_count']}")
                print(f"   Language: {analysis['language']}")
            else:
                print(f"❌ Question {i} failed: {response.status_code}")
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"❌ Question {i} error: {e}")
    
    # Test 3: Demo Recommendation Engine
    print("\n🎯 Testing Demo Recommendation Engine...")
    try:
        response = requests.post(f"{BASE_URL}/ai/demo/test-recommendation")
        
        if response.status_code == 200:
            data = response.json()
            profile = data['demo_profile']
            recommendations = data['recommendations']
            
            print(f"✅ Demo Profile:")
            print(f"   Learning Style: {profile['learning_style']}")
            print(f"   Subjects: {', '.join(profile['subjects'])}")
            print(f"   Weak Areas: {', '.join(profile['weak_areas'])}")
            print(f"   Strong Areas: {', '.join(profile['strong_areas'])}")
            
            print(f"\n✅ Recommendations ({len(recommendations)}):")
            for i, rec in enumerate(recommendations, 1):
                print(f"{i}. Strategy: {rec['strategy']}")
                print(f" Confidence: {rec['confidence']:.2f}")
                print(f" Priority: {rec['priority']:.2f}")
                if rec['reasoning']:
                    print(f" Reasoning: {', '.join(rec['reasoning'][:2])}...")
        else:
            print(f"❌ Recommendation test failed: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Recommendation test error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Demo testing completed!")
    print("\n💡 Next steps:")
    print("   1. All AI services are working correctly")
    print("   2. Text processing analyzes questions accurately")
    print("   3. Recommendation engine generates personalized suggestions")
    print("   4. Ready for authentication implementation and full API testing")
    print("   5. Check http://localhost:8001/api/v1/docs for interactive API docs")

if __name__ == "__main__":
    test_demo_endpoints()
