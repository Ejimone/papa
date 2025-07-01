#!/usr/bin/env python3
"""
Test script for all models in the AI-Powered Past Questions App
This script tests model imports, basic functionality, and relationships
"""

import sys
import os
import asyncio
from datetime import datetime, timedelta

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_model_imports():
    """Test that all models can be imported without errors"""
    print("🔍 Testing model imports...")
    
    try:
        from app.models import (
            Base, User, UserProfile, UserPreferences,
            Subject, Topic, Question, QuestionMetadata, QuestionImage,
            Explanation, Hint, SimilarQuestion, PracticeSession,
            UserAttempt, UserBookmark, UserProgress, UserAnalytics,
            LearningAnalytics, QuestionAnalytics, SystemAnalytics,
            UserEvent, PerformanceTrend, StudyGroup
        )
        print("✅ All models imported successfully!")
        return True
    except Exception as e:
        print(f"❌ Model import failed: {e}")
        return False

def test_model_creation():
    """Test basic model creation and attributes"""
    print("\n🔍 Testing model creation...")
    
    try:
        from app.models import (
            User, Subject, Topic, Question, QuestionType, DifficultyLevel,
            PracticeSession, SessionType, SessionStatus
        )
        
        # Test User creation
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password_123",
            is_active=True
        )
        print("✅ User model created successfully")
        
        # Test Subject creation
        subject = Subject(
            name="Computer Science 101",
            code="CS101",
            description="Introduction to Computer Science",
            department="Computer Science",
            level=100
        )
        print("✅ Subject model created successfully")
        
        # Test Topic creation
        topic = Topic(
            name="Data Structures",
            description="Introduction to data structures",
            subject_id=1,  # Would be set by relationship
            level=1
        )
        print("✅ Topic model created successfully")
        
        # Test Question creation
        question = Question(
            title="What is a stack?",
            content="Explain the concept of a stack data structure",
            question_type=QuestionType.SHORT_ANSWER,
            difficulty_level=DifficultyLevel.BEGINNER,
            subject_id=1,
            points=5
        )
        print("✅ Question model created successfully")
        
        # Test PracticeSession creation
        session = PracticeSession(
            user_id=1,
            session_type=SessionType.QUICK_PRACTICE,
            status=SessionStatus.STARTED,
            title="Quick CS Practice",
            question_count=10
        )
        print("✅ PracticeSession model created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Model creation failed: {e}")
        return False

def test_enum_values():
    """Test that all enum values are properly defined"""
    print("\n🔍 Testing enum values...")
    
    try:
        from app.models import (
            QuestionType, DifficultyLevel, SessionType, 
            SessionStatus, AttemptStatus, EventType, PerformanceLevel
        )
        
        # Test QuestionType enum
        assert QuestionType.MULTIPLE_CHOICE == "multiple_choice"
        assert QuestionType.SHORT_ANSWER == "short_answer"
        assert QuestionType.ESSAY == "essay"
        print("✅ QuestionType enum values correct")
        
        # Test DifficultyLevel enum
        assert DifficultyLevel.BEGINNER == "beginner"
        assert DifficultyLevel.INTERMEDIATE == "intermediate"
        assert DifficultyLevel.ADVANCED == "advanced"
        print("✅ DifficultyLevel enum values correct")
        
        # Test SessionType enum
        assert SessionType.QUICK_PRACTICE == "quick_practice"
        assert SessionType.MOCK_TEST == "mock_test"
        print("✅ SessionType enum values correct")
        
        # Test EventType enum
        assert EventType.LOGIN == "login"
        assert EventType.QUESTION_ANSWERED == "question_answered"
        print("✅ EventType enum values correct")
        
        return True
        
    except Exception as e:
        print(f"❌ Enum test failed: {e}")
        return False

def test_model_relationships():
    """Test model relationship definitions"""
    print("\n🔍 Testing model relationships...")
    
    try:
        from app.models import User, Subject, Question, UserProfile
        from sqlalchemy.orm import relationship
        
        # Test User relationships
        user_relationships = [attr for attr in dir(User) if isinstance(getattr(User, attr), relationship)]
        expected_user_rels = ['profile', 'preferences', 'attempts', 'bookmarks', 'progress']
        
        for rel in expected_user_rels:
            if rel in user_relationships:
                print(f"✅ User.{rel} relationship defined")
            else:
                print(f"⚠️  User.{rel} relationship not found")
        
        # Test Subject relationships
        subject_relationships = [attr for attr in dir(Subject) if isinstance(getattr(Subject, attr), relationship)]
        expected_subject_rels = ['topics', 'questions', 'user_progress']
        
        for rel in expected_subject_rels:
            if rel in subject_relationships:
                print(f"✅ Subject.{rel} relationship defined")
            else:
                print(f"⚠️  Subject.{rel} relationship not found")
        
        # Test Question relationships
        question_relationships = [attr for attr in dir(Question) if isinstance(getattr(Question, attr), relationship)]
        expected_question_rels = ['subject', 'topic', 'question_metadata', 'images', 'explanations']
        
        for rel in expected_question_rels:
            if rel in question_relationships:
                print(f"✅ Question.{rel} relationship defined")
            else:
                print(f"⚠️  Question.{rel} relationship not found")
        
        return True
        
    except Exception as e:
        print(f"❌ Relationship test failed: {e}")
        return False

def test_model_table_names():
    """Test that all models have correct table names"""
    print("\n🔍 Testing model table names...")
    
    try:
        from app.models import (
            User, Subject, Topic, Question, QuestionMetadata,
            PracticeSession, UserAttempt, UserBookmark, UserAnalytics
        )
        
        table_tests = [
            (User, "users"),
            (Subject, "subjects"),
            (Topic, "topics"),
            (Question, "questions"),
            (QuestionMetadata, "question_metadata"),
            (PracticeSession, "practice_sessions"),
            (UserAttempt, "user_attempts"),
            (UserBookmark, "user_bookmarks"),
            (UserAnalytics, "user_analytics"),
        ]
        
        for model_class, expected_table in table_tests:
            actual_table = model_class.__tablename__
            if actual_table == expected_table:
                print(f"✅ {model_class.__name__} table name: {actual_table}")
            else:
                print(f"❌ {model_class.__name__} table name mismatch: expected {expected_table}, got {actual_table}")
        
        return True
        
    except Exception as e:
        print(f"❌ Table name test failed: {e}")
        return False

def test_model_repr_methods():
    """Test that model __repr__ methods work correctly"""
    print("\n🔍 Testing model __repr__ methods...")
    
    try:
        from app.models import User, Subject, Question, QuestionType, DifficultyLevel
        
        # Test User repr
        user = User(email="test@example.com", username="testuser", hashed_password="hash123")
        user.id = 1  # Simulate database ID
        user_repr = repr(user)
        assert "User" in user_repr and "test@example.com" in user_repr
        print(f"✅ User repr: {user_repr}")
        
        # Test Subject repr
        subject = Subject(name="Mathematics", code="MATH101")
        subject.id = 1
        subject_repr = repr(subject)
        assert "Subject" in subject_repr and "Mathematics" in subject_repr
        print(f"✅ Subject repr: {subject_repr}")
        
        # Test Question repr
        question = Question(
            title="What is calculus?",
            content="Explain the basics of calculus",
            question_type=QuestionType.SHORT_ANSWER,
            difficulty_level=DifficultyLevel.INTERMEDIATE,
            subject_id=1
        )
        question.id = 1
        question_repr = repr(question)
        assert "Question" in question_repr
        print(f"✅ Question repr: {question_repr}")
        
        return True
        
    except Exception as e:
        print(f"❌ Repr method test failed: {e}")
        return False

async def test_database_connection():
    """Test database connection and basic operations"""
    print("\n🔍 Testing database connection...")
    
    try:
        from app.core.database import engine, AsyncSessionLocal
        from app.models import Base
        
        # Test engine creation
        assert engine is not None
        print("✅ Database engine created successfully")
        
        # Test session creation
        async with AsyncSessionLocal() as session:
            assert session is not None
            print("✅ Database session created successfully")
        
        print("✅ Database connection test passed")
        return True
        
    except Exception as e:
        print(f"❌ Database connection test failed: {e}")
        return False

def test_json_field_defaults():
    """Test that JSON fields have proper default values"""
    print("\n🔍 Testing JSON field defaults...")
    
    try:
        from app.models import QuestionMetadata, UserPreferences, Subject
        
        # Test QuestionMetadata JSON defaults
        metadata = QuestionMetadata(question_id=1)
        assert metadata.tags == []
        assert metadata.keywords == []
        print("✅ QuestionMetadata JSON defaults work")
        
        # Test UserPreferences JSON defaults
        preferences = UserPreferences(user_id=1)
        assert preferences.question_types == []
        assert preferences.subjects_of_interest == []
        print("✅ UserPreferences JSON defaults work")
        
        # Test Subject JSON defaults
        subject = Subject(name="Test Subject")
        assert subject.tags == []
        assert subject.prerequisites == []
        print("✅ Subject JSON defaults work")
        
        return True
        
    except Exception as e:
        print(f"❌ JSON field defaults test failed: {e}")
        return False

async def run_all_tests():
    """Run all tests and provide a summary"""
    print("🚀 Starting AI-Powered Past Questions App Model Tests\n")
    print("=" * 60)
    
    tests = [
        ("Model Imports", test_model_imports),
        ("Model Creation", test_model_creation),
        ("Enum Values", test_enum_values),
        ("Model Relationships", test_model_relationships),
        ("Table Names", test_model_table_names),
        ("Repr Methods", test_model_repr_methods),
        ("JSON Field Defaults", test_json_field_defaults),
        ("Database Connection", test_database_connection),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            if result:
                passed += 1
            else:
                failed += 1
                
        except Exception as e:
            print(f"\n❌ {test_name} test crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Test Summary:")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success Rate: {(passed / (passed + failed)) * 100:.1f}%")
    
    if failed == 0:
        print("\n🎉 All tests passed! Your models are ready for the next phase.")
        return True
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please review the errors above.")
        return False

if __name__ == "__main__":
    # Run the tests
    result = asyncio.run(run_all_tests())
    sys.exit(0 if result else 1) 