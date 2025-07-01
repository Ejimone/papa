#!/usr/bin/env python3
"""
Simple test script for models to avoid import conflicts
"""

import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_basic_imports():
    """Test basic model imports one by one"""
    print("🔍 Testing basic imports...")
    
    try:
        # Test base import first
        from app.models.base import Base
        print("✅ Base model imported successfully")
        
        # Test user model
        from app.models.user import User
        print("✅ User model imported successfully")
        
        # Test subject model
        from app.models.subject import Subject, Topic
        print("✅ Subject and Topic models imported successfully")
        
        # Test question model
        from app.models.question import Question, QuestionType, DifficultyLevel
        print("✅ Question model and enums imported successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_enum_values():
    """Test enum values"""
    print("\n🔍 Testing enum values...")
    
    try:
        from app.models.question import QuestionType, DifficultyLevel
        
        # Test QuestionType enum
        assert QuestionType.MULTIPLE_CHOICE == "multiple_choice"
        assert QuestionType.SHORT_ANSWER == "short_answer"
        print("✅ QuestionType enum values correct")
        
        # Test DifficultyLevel enum
        assert DifficultyLevel.BEGINNER == "beginner"
        assert DifficultyLevel.INTERMEDIATE == "intermediate"
        print("✅ DifficultyLevel enum values correct")
        
        return True
        
    except Exception as e:
        print(f"❌ Enum test failed: {e}")
        return False

def test_model_creation():
    """Test basic model creation without database"""
    print("\n🔍 Testing model creation...")
    
    try:
        from app.models.user import User
        from app.models.subject import Subject
        from app.models.question import Question, QuestionType, DifficultyLevel
        
        # Test User creation
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password_123"
        )
        print("✅ User model created successfully")
        
        # Test Subject creation
        subject = Subject(
            name="Computer Science 101",
            code="CS101",
            description="Introduction to Computer Science"
        )
        print("✅ Subject model created successfully")
        
        # Test Question creation
        question = Question(
            title="What is a stack?",
            content="Explain the concept of a stack data structure",
            question_type=QuestionType.SHORT_ANSWER,
            difficulty_level=DifficultyLevel.BEGINNER,
            subject_id=1
        )
        print("✅ Question model created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Model creation failed: {e}")
        return False

def test_model_attributes():
    """Test model attributes and relationships"""
    print("\n🔍 Testing model attributes...")
    
    try:
        from app.models.question import Question
        from app.models.user import User
        from app.models.subject import Subject
        
        # Check that models have expected attributes
        user_attrs = ['email', 'username', 'hashed_password', 'is_active']
        for attr in user_attrs:
            if hasattr(User, attr):
                print(f"✅ User.{attr} attribute exists")
            else:
                print(f"⚠️  User.{attr} attribute missing")
        
        question_attrs = ['title', 'content', 'question_type', 'difficulty_level', 'subject_id']
        for attr in question_attrs:
            if hasattr(Question, attr):
                print(f"✅ Question.{attr} attribute exists")
            else:
                print(f"⚠️  Question.{attr} attribute missing")
        
        return True
        
    except Exception as e:
        print(f"❌ Attribute test failed: {e}")
        return False

def main():
    """Run all simple tests"""
    print("🚀 Starting Simple Model Tests\n")
    print("=" * 50)
    
    tests = [
        ("Basic Imports", test_basic_imports),
        ("Enum Values", test_enum_values),
        ("Model Creation", test_model_creation),
        ("Model Attributes", test_model_attributes),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            if result:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"\n❌ {test_name} test crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Summary:")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success Rate: {(passed / (passed + failed)) * 100:.1f}%")
    
    if failed == 0:
        print("\n🎉 All simple tests passed!")
        return True
    else:
        print(f"\n⚠️  {failed} test(s) failed.")
        return False

if __name__ == "__main__":
    result = main()
    sys.exit(0 if result else 1) 