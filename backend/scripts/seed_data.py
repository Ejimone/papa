#!/usr/bin/env python3
"""
Database seeding script.
Populates the database with sample questions, users, and test data for development.
"""

import asyncio
import sys
import os
import json
from pathlib import Path
from datetime import datetime, timedelta, date
import random

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.append(str(backend_dir))

from sqlalchemy import text
from app.core.database import AsyncSessionLocal
from app.core.security import get_password_hash
from app.core.logging import get_logger

logger = get_logger(__name__)

# Sample questions data
SAMPLE_QUESTIONS = [
    # Mathematics - Algebra
    {
        "title": "Solve for x: 2x + 5 = 13",
        "content": "Find the value of x in the equation 2x + 5 = 13",
        "answer": "x = 4",
        "question_type": "multiple_choice",
        "difficulty_level": "easy",
        "subject": "Mathematics",
        "topic": "Algebra",
        "options": ["x = 2", "x = 4", "x = 6", "x = 8"],
        "correct_option": 1,
        "explanation": "Subtract 5 from both sides: 2x = 8, then divide by 2: x = 4"
    },
    {
        "title": "Quadratic Formula",
        "content": "What is the quadratic formula used to solve ax² + bx + c = 0?",
        "answer": "x = (-b ± √(b² - 4ac)) / 2a",
        "question_type": "multiple_choice",
        "difficulty_level": "intermediate",
        "subject": "Mathematics",
        "topic": "Algebra",
        "options": [
            "x = (-b ± √(b² - 4ac)) / 2a",
            "x = (-b ± √(b² + 4ac)) / 2a", 
            "x = (b ± √(b² - 4ac)) / 2a",
            "x = (-b ± √(b² - 4ac)) / a"
        ],
        "correct_option": 0,
        "explanation": "The quadratic formula is derived by completing the square on the general quadratic equation."
    },
    
    # Mathematics - Calculus
    {
        "title": "Derivative of x²",
        "content": "What is the derivative of f(x) = x²?",
        "answer": "f'(x) = 2x",
        "question_type": "multiple_choice",
        "difficulty_level": "easy",
        "subject": "Mathematics",
        "topic": "Calculus",
        "options": ["f'(x) = x", "f'(x) = 2x", "f'(x) = x²", "f'(x) = 2x²"],
        "correct_option": 1,
        "explanation": "Using the power rule: d/dx(x^n) = nx^(n-1), so d/dx(x²) = 2x^(2-1) = 2x"
    },
    
    # Physics - Mechanics
    {
        "title": "Newton's Second Law",
        "content": "According to Newton's second law, force equals:",
        "answer": "mass times acceleration",
        "question_type": "multiple_choice",
        "difficulty_level": "easy",
        "subject": "Physics",
        "topic": "Mechanics",
        "options": [
            "mass times velocity",
            "mass times acceleration", 
            "mass times displacement",
            "acceleration times time"
        ],
        "correct_option": 1,
        "explanation": "Newton's second law states that F = ma, where F is force, m is mass, and a is acceleration."
    },
    
    # Computer Science - Programming
    {
        "title": "Python List Comprehension",
        "content": "What does [x**2 for x in range(5)] produce?",
        "answer": "[0, 1, 4, 9, 16]",
        "question_type": "multiple_choice",
        "difficulty_level": "intermediate",
        "subject": "Computer Science",
        "topic": "Programming Fundamentals",
        "options": [
            "[0, 1, 4, 9, 16]",
            "[1, 4, 9, 16, 25]",
            "[0, 1, 2, 3, 4]",
            "[1, 2, 3, 4, 5]"
        ],
        "correct_option": 0,
        "explanation": "The list comprehension squares each number from 0 to 4: 0²=0, 1²=1, 2²=4, 3²=9, 4²=16"
    },
    
    # Add more questions for each subject...
    {
        "title": "Time Complexity",
        "content": "What is the time complexity of binary search?",
        "answer": "O(log n)",
        "question_type": "multiple_choice", 
        "difficulty_level": "intermediate",
        "subject": "Computer Science",
        "topic": "Algorithms",
        "options": ["O(n)", "O(log n)", "O(n log n)", "O(n²)"],
        "correct_option": 1,
        "explanation": "Binary search eliminates half the search space with each comparison, resulting in O(log n) time complexity."
    }
]

# Sample test users
SAMPLE_USERS = [
    {
        "email": "student1@test.com",
        "password": "password123",
        "full_name": "Alice Johnson",
        "profile": {
            "academic_level": "undergraduate",
            "institution": "University of Technology",
            "field_of_study": "Computer Science"
        }
    },
    {
        "email": "student2@test.com", 
        "password": "password123",
        "full_name": "Bob Smith",
        "profile": {
            "academic_level": "undergraduate",
            "institution": "State University",
            "field_of_study": "Mathematics"
        }
    },
    {
        "email": "student3@test.com",
        "password": "password123",
        "full_name": "Carol Davis",
        "profile": {
            "academic_level": "graduate",
            "institution": "Tech Institute",
            "field_of_study": "Physics"
        }
    }
]

async def get_subject_topic_ids():
    """Get subject and topic IDs for question insertion"""
    async with AsyncSessionLocal() as db:
        # Get subjects
        subjects_query = text("SELECT id, name FROM subjects ORDER BY name")
        subjects_result = await db.execute(subjects_query)
        subjects = {row[1]: row[0] for row in subjects_result.fetchall()}
        
        # Get topics
        topics_query = text("SELECT id, name, subject_id FROM topics ORDER BY name")
        topics_result = await db.execute(topics_query)
        topics = {}
        for row in topics_result.fetchall():
            topic_id, topic_name, subject_id = row
            if subject_id not in topics:
                topics[subject_id] = {}
            topics[subject_id][topic_name] = topic_id
        
        return subjects, topics

async def seed_questions():
    """Seed the database with sample questions"""
    try:
        async with AsyncSessionLocal() as db:
            # Check if questions already exist
            count_result = await db.execute(text("SELECT COUNT(*) FROM questions"))
            existing_count = count_result.scalar()
            
            if existing_count > 0:
                logger.info(f"ℹ️  {existing_count} questions already exist")
                response = input("Do you want to add more sample questions? (y/N): ")
                if response.lower() != 'y':
                    return True
            
            logger.info("Adding sample questions...")
            
            # Get subject and topic mappings
            subjects, topics = await get_subject_topic_ids()
            
            added_count = 0
            for question_data in SAMPLE_QUESTIONS:
                try:
                    subject_name = question_data["subject"]
                    topic_name = question_data["topic"]
                    
                    if subject_name not in subjects:
                        logger.warning(f"⚠️  Subject '{subject_name}' not found, skipping question")
                        continue
                    
                    subject_id = subjects[subject_name]
                    
                    if subject_id not in topics or topic_name not in topics[subject_id]:
                        logger.warning(f"⚠️  Topic '{topic_name}' not found in subject '{subject_name}', skipping question")
                        continue
                    
                    topic_id = topics[subject_id][topic_name]
                    
                    # Insert question
                    question_insert = text("""
                        INSERT INTO questions (title, content, answer, question_type, difficulty_level,
                                             subject_id, topic_id, is_active, priority_score,
                                             created_at, updated_at)
                        VALUES (:title, :content, :answer, :question_type, :difficulty_level,
                               :subject_id, :topic_id, true, :priority_score, NOW(), NOW())
                        RETURNING id
                    """)
                    
                    # Calculate priority score based on difficulty
                    priority_map = {"easy": 3, "intermediate": 5, "advanced": 7, "expert": 9}
                    priority_score = priority_map.get(question_data["difficulty_level"], 5)
                    
                    result = await db.execute(question_insert, {
                        "title": question_data["title"],
                        "content": question_data["content"],
                        "answer": question_data["answer"],
                        "question_type": question_data["question_type"],
                        "difficulty_level": question_data["difficulty_level"],
                        "subject_id": subject_id,
                        "topic_id": topic_id,
                        "priority_score": priority_score
                    })
                    
                    question_id = result.scalar()
                    
                    # Insert question options if multiple choice
                    if question_data["question_type"] == "multiple_choice" and "options" in question_data:
                        for i, option in enumerate(question_data["options"]):
                            option_insert = text("""
                                INSERT INTO question_options (question_id, option_text, option_order, is_correct)
                                VALUES (:question_id, :option_text, :option_order, :is_correct)
                            """)
                            
                            await db.execute(option_insert, {
                                "question_id": question_id,
                                "option_text": option,
                                "option_order": i,
                                "is_correct": i == question_data.get("correct_option", -1)
                            })
                    
                    # Insert explanation if provided
                    if "explanation" in question_data:
                        explanation_insert = text("""
                            INSERT INTO explanations (question_id, content, explanation_type, is_ai_generated)
                            VALUES (:question_id, :content, 'step_by_step', false)
                        """)
                        
                        await db.execute(explanation_insert, {
                            "question_id": question_id,
                            "content": question_data["explanation"]
                        })
                    
                    added_count += 1
                    
                except Exception as e:
                    logger.error(f"❌ Failed to add question '{question_data['title']}': {e}")
                    continue
            
            await db.commit()
            logger.info(f"✅ Added {added_count} sample questions")
            return True
            
    except Exception as e:
        logger.error(f"❌ Failed to seed questions: {e}")
        return False

async def seed_users():
    """Seed the database with sample users"""
    try:
        async with AsyncSessionLocal() as db:
            # Check if test users already exist
            count_result = await db.execute(text("SELECT COUNT(*) FROM users WHERE email LIKE '%@test.com'"))
            existing_count = count_result.scalar()
            
            if existing_count > 0:
                logger.info(f"ℹ️  {existing_count} test users already exist, skipping user creation")
                return True
            
            logger.info("Creating sample users...")
            
            created_count = 0
            for user_data in SAMPLE_USERS:
                try:
                    # Create user
                    user_insert = text("""
                        INSERT INTO users (email, hashed_password, full_name, is_active, is_verified,
                                         created_at, updated_at)
                        VALUES (:email, :hashed_password, :full_name, true, true, NOW(), NOW())
                        RETURNING id
                    """)
                    
                    hashed_password = get_password_hash(user_data["password"])
                    
                    result = await db.execute(user_insert, {
                        "email": user_data["email"],
                        "hashed_password": hashed_password,
                        "full_name": user_data["full_name"]
                    })
                    
                    user_id = result.scalar()
                    
                    # Create user profile
                    profile_data = user_data["profile"]
                    profile_insert = text("""
                        INSERT INTO user_profiles (user_id, academic_level, institution, field_of_study,
                                                 timezone, language, created_at, updated_at)
                        VALUES (:user_id, :academic_level, :institution, :field_of_study,
                               'UTC', 'en', NOW(), NOW())
                    """)
                    
                    await db.execute(profile_insert, {
                        "user_id": user_id,
                        "academic_level": profile_data["academic_level"],
                        "institution": profile_data["institution"],
                        "field_of_study": profile_data["field_of_study"]
                    })
                    
                    # Create user preferences
                    preferences_insert = text("""
                        INSERT INTO user_preferences (user_id, preferred_difficulty, daily_question_goal,
                                                   study_reminder_enabled, notifications_enabled, 
                                                   email_notifications, created_at, updated_at)
                        VALUES (:user_id, 'medium', 10, true, true, true, NOW(), NOW())
                    """)
                    
                    await db.execute(preferences_insert, {"user_id": user_id})
                    
                    created_count += 1
                    logger.info(f"✅ Created user: {user_data['email']}")
                    
                except Exception as e:
                    logger.error(f"❌ Failed to create user {user_data['email']}: {e}")
                    continue
            
            await db.commit()
            logger.info(f"✅ Created {created_count} sample users")
            return True
            
    except Exception as e:
        logger.error(f"❌ Failed to seed users: {e}")
        return False

async def generate_sample_activity():
    """Generate sample user activity data for testing analytics"""
    try:
        async with AsyncSessionLocal() as db:
            logger.info("Generating sample user activity...")
            
            # Get test users
            users_query = text("SELECT id FROM users WHERE email LIKE '%@test.com'")
            users_result = await db.execute(users_query)
            user_ids = [row[0] for row in users_result.fetchall()]
            
            if not user_ids:
                logger.warning("⚠️  No test users found, skipping activity generation")
                return True
            
            # Get some questions
            questions_query = text("SELECT id FROM questions LIMIT 20")
            questions_result = await db.execute(questions_query)
            question_ids = [row[0] for row in questions_result.fetchall()]
            
            if not question_ids:
                logger.warning("⚠️  No questions found, skipping activity generation")
                return True
            
            # Generate activity for the past 7 days
            activities_created = 0
            for days_ago in range(7):
                activity_date = date.today() - timedelta(days=days_ago)
                
                for user_id in user_ids:
                    # Create practice session
                    session_insert = text("""
                        INSERT INTO practice_sessions (user_id, session_type, status, 
                                                     total_questions, questions_completed,
                                                     correct_answers, accuracy_rate,
                                                     created_at, updated_at)
                        VALUES (:user_id, 'practice', 'completed', :total_q, :completed_q,
                               :correct, :accuracy, :created_at, :created_at)
                        RETURNING id
                    """)
                    
                    # Random session data
                    total_questions = random.randint(5, 15)
                    questions_completed = total_questions
                    correct_answers = random.randint(int(total_questions * 0.4), total_questions)
                    accuracy_rate = (correct_answers / total_questions) * 100
                    
                    session_created_at = datetime.combine(activity_date, datetime.min.time()) + timedelta(
                        hours=random.randint(8, 20),
                        minutes=random.randint(0, 59)
                    )
                    
                    session_result = await db.execute(session_insert, {
                        "user_id": user_id,
                        "total_q": total_questions,
                        "completed_q": questions_completed,
                        "correct": correct_answers,
                        "accuracy": accuracy_rate,
                        "created_at": session_created_at
                    })
                    
                    session_id = session_result.scalar()
                    
                    # Create user attempts for this session
                    selected_questions = random.sample(question_ids, total_questions)
                    
                    for i, question_id in enumerate(selected_questions):
                        is_correct = i < correct_answers
                        time_taken = random.randint(30, 180)  # 30 seconds to 3 minutes
                        
                        attempt_insert = text("""
                            INSERT INTO user_attempts (user_id, question_id, session_id, 
                                                     user_answer, is_correct, time_taken,
                                                     hint_used, created_at)
                            VALUES (:user_id, :question_id, :session_id, :answer, 
                                   :is_correct, :time_taken, :hint_used, :created_at)
                        """)
                        
                        attempt_time = session_created_at + timedelta(minutes=i * 2)
                        
                        await db.execute(attempt_insert, {
                            "user_id": user_id,
                            "question_id": question_id,
                            "session_id": session_id,
                            "answer": "Sample answer" if is_correct else "Wrong answer",
                            "is_correct": is_correct,
                            "time_taken": time_taken,
                            "hint_used": random.choice([True, False]),
                            "created_at": attempt_time
                        })
                    
                    activities_created += 1
            
            await db.commit()
            logger.info(f"✅ Generated {activities_created} sample practice sessions")
            return True
            
    except Exception as e:
        logger.error(f"❌ Failed to generate sample activity: {e}")
        return False

async def main():
    """Main seeding function"""
    print("🌱 PAPA Database Seeding")
    print("=" * 50)
    
    success = True
    
    # Step 1: Seed questions
    logger.info("Step 1: Seeding sample questions...")
    if not await seed_questions():
        success = False
    
    # Step 2: Seed users
    logger.info("\nStep 2: Seeding sample users...")
    if not await seed_users():
        success = False
    
    # Step 3: Generate sample activity
    logger.info("\nStep 3: Generating sample user activity...")
    if not await generate_sample_activity():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Database seeding completed successfully!")
        print("\n📝 Sample data added:")
        print("   - Sample questions across multiple subjects")
        print("   - Test users (student1@test.com, student2@test.com, student3@test.com)")
        print("   - Sample practice sessions and user attempts")
        print("   - Password for all test users: password123")
        print("\n💡 You can now test the application with this sample data!")
    else:
        print("❌ Database seeding failed!")
        print("   Check the logs above for specific error details")
        return 1
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⏹️  Seeding interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Unexpected error: {str(e)}")
        sys.exit(1)
