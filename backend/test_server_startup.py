#!/usr/bin/env python3
"""
Server startup test script
Tests if the FastAPI server can start properly with all endpoints.
"""

import sys
import os
import traceback
from typing import List

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all modules can be imported without errors"""
    print("🔍 Testing module imports...")
    
    import_tests = [
        ("FastAPI core", "from fastapi import FastAPI"),
        ("Database config", "from app.core.database import get_db"),
        ("User models", "from app.models.user import User"),
        ("Subject models", "from app.models.subject import Subject, Topic"),
        ("Question models", "from app.models.question import Question"),
        ("Practice models", "from app.models.practice import PracticeSession"),
        ("Analytics models", "from app.models.analytics import UserAnalytics"),
        ("Base schemas", "from app.schemas.base import BaseSchema"),
        ("User schemas", "from app.schemas.user import UserCreate"),
        ("Question schemas", "from app.schemas.question import QuestionCreate"),
        ("Practice schemas", "from app.schemas.practice import PracticeSessionCreate"),
        ("Analytics schemas", "from app.schemas.analytics import UserAnalyticsCreate"),
        ("Base service", "from app.services.base import BaseService"),
        ("Question service", "from app.services.question_service import QuestionService"),
        ("Practice service", "from app.services.practice_service import PracticeService"),
        ("Analytics service", "from app.services.analytics_service import AnalyticsService"),
        ("Search service", "from app.services.search_service import SearchService"),
        ("Auth endpoints", "from app.api.v1.endpoints.auth import router"),
        ("User endpoints", "from app.api.v1.endpoints.users import router"),
        ("Subject endpoints", "from app.api.v1.endpoints.subjects import router"),
        ("Question endpoints", "from app.api.v1.endpoints.questions import router"),
        ("Practice endpoints", "from app.api.v1.endpoints.practice import router"),
        ("Analytics endpoints", "from app.api.v1.endpoints.analytics import router"),
        ("Search endpoints", "from app.api.v1.endpoints.search import router"),
        ("Admin endpoints", "from app.api.v1.endpoints.admin import router"),
        ("API router", "from app.api.v1.api import api_router"),
        ("Main app", "from app.main import app"),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, import_statement in import_tests:
        try:
            exec(import_statement)
            print(f"  ✅ {test_name}")
            passed += 1
        except Exception as e:
            print(f"  ❌ {test_name}: {str(e)}")
            failed += 1
    
    print(f"\n📊 Import Results: {passed} passed, {failed} failed")
    return failed == 0

def test_app_creation():
    """Test if the FastAPI app can be created"""
    print("\n🏗️  Testing FastAPI app creation...")
    
    try:
        from app.main import app
        print(f"  ✅ App created successfully")
        print(f"  ✅ App title: {app.title}")
        print(f"  ✅ App version: {app.version}")
        return True
    except Exception as e:
        print(f"  ❌ Failed to create app: {str(e)}")
        traceback.print_exc()
        return False

def test_router_configuration():
    """Test if all routers are properly configured"""
    print("\n🛣️  Testing router configuration...")
    
    try:
        from app.api.v1.api import api_router
        
        # Check if routes are registered
        routes = [route.path for route in api_router.routes]
        expected_prefixes = [
            "/auth",
            "/users", 
            "/subjects",
            "/questions",
            "/practice",
            "/analytics", 
            "/search",
            "/admin",
            "/ai"
        ]
        
        found_prefixes = []
        for prefix in expected_prefixes:
            if any(route.startswith(prefix) for route in routes):
                found_prefixes.append(prefix)
                print(f"  ✅ {prefix} routes registered")
            else:
                print(f"  ❌ {prefix} routes missing")
        
        print(f"\n📊 Router Results: {len(found_prefixes)}/{len(expected_prefixes)} route groups found")
        return len(found_prefixes) == len(expected_prefixes)
        
    except Exception as e:
        print(f"  ❌ Failed to test routers: {str(e)}")
        traceback.print_exc()
        return False

def test_database_models():
    """Test if database models can be loaded"""
    print("\n🗄️  Testing database models...")
    
    try:
        # Test model imports and basic instantiation
        from app.models.user import User
        from app.models.subject import Subject, Topic
        from app.models.question import Question
        from app.models.practice import PracticeSession
        from app.models.analytics import UserAnalytics
        
        print("  ✅ All model classes imported successfully")
        
        # Test model attributes exist
        models_to_test = [
            (User, ['id', 'email', 'full_name']),
            (Subject, ['id', 'name', 'description']),
            (Topic, ['id', 'name', 'subject_id']),
            (Question, ['id', 'title', 'content']),
            (PracticeSession, ['id', 'user_id', 'session_type']),
            (UserAnalytics, ['id', 'user_id', 'total_questions_attempted'])
        ]
        
        for model_class, expected_attrs in models_to_test:
            missing_attrs = []
            for attr in expected_attrs:
                if not hasattr(model_class, attr):
                    missing_attrs.append(attr)
            
            if missing_attrs:
                print(f"  ❌ {model_class.__name__} missing attributes: {missing_attrs}")
            else:
                print(f"  ✅ {model_class.__name__} has all expected attributes")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Failed to test models: {str(e)}")
        traceback.print_exc()
        return False

def test_service_instantiation():
    """Test if services can be instantiated"""
    print("\n🔧 Testing service instantiation...")
    
    try:
        # Mock database session for testing
        class MockDB:
            async def execute(self, query):
                pass
            async def commit(self):
                pass
            async def rollback(self):
                pass
            def add(self, obj):
                pass
            async def refresh(self, obj):
                pass
            async def delete(self, obj):
                pass
        
        mock_db = MockDB()
        
        # Test service creation
        from app.services.question_service import QuestionService
        from app.services.practice_service import PracticeService
        from app.services.analytics_service import AnalyticsService
        from app.services.search_service import SearchService
        
        services = [
            ("QuestionService", QuestionService),
            ("PracticeService", PracticeService), 
            ("AnalyticsService", AnalyticsService),
            ("SearchService", SearchService)
        ]
        
        for service_name, service_class in services:
            try:
                service = service_class(mock_db)
                print(f"  ✅ {service_name} instantiated successfully")
            except Exception as e:
                print(f"  ❌ {service_name} failed to instantiate: {str(e)}")
                return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ Failed to test services: {str(e)}")
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🚀 AI-Powered Past Questions App - Server Startup Test")
    print("=" * 60)
    
    tests = [
        ("Module Imports", test_imports),
        ("App Creation", test_app_creation),
        ("Router Configuration", test_router_configuration),
        ("Database Models", test_database_models),
        ("Service Instantiation", test_service_instantiation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} test...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\n📊 Overall Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("\n🎉 All tests passed! The server should start successfully.")
        print("💡 You can now run: uvicorn app.main:app --reload")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please fix the issues before starting the server.")
    
    return failed == 0

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Unexpected error: {str(e)}")
        traceback.print_exc()
        sys.exit(1) 