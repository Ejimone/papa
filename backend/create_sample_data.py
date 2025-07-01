#!/usr/bin/env python3
"""
Create comprehensive sample data for testing all repository functionality.
"""
import asyncio
import sys
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.database import engine, AsyncSessionLocal
from app.core.security import get_password_hash
from app.models.user import User
from app.models.subject import Subject, Topic
from app.models.question import Question, QuestionMetadata, QuestionImage, Explanation, Hint
from app.models.practice import PracticeSession, UserAttempt, UserBookmark, UserProgress
from app.models.analytics import UserAnalytics, DailyUserActivity, WeeklyUserActivity
from app.schemas.user import UserCreate
from app.schemas.subject import SubjectCreate, TopicCreate
from app.schemas.question import QuestionCreate
from app.schemas.practice import PracticeSessionCreate, UserAttemptCreate

async def create_sample_data():
    """Create comprehensive sample data for testing."""
    async with AsyncSessionLocal() as db:
        print("🚀 Creating sample data...")
        
        # Check if data already exists
        existing_subjects = await db.execute(text("SELECT COUNT(*) FROM subjects"))
        subject_count = existing_subjects.scalar()
        
        if subject_count > 0:
            print(f"📊 Sample data already exists ({subject_count} subjects found)")
            print("To recreate, delete existing data first")
            return
        
        try:
            # 1. Create Users with Profiles and Preferences
            print("👥 Creating users...")
            users_data = [
                {
                    "email": "john.doe@mit.edu",
                    "username": "johndoe",
                    "password": "testpass123",
                    "profile": {
                        "first_name": "John",
                        "last_name": "Doe", 
                        "university": "MIT",
                        "degree": "Computer Science",
                        "year": "Senior",
                        "major": "AI & Machine Learning"
                    }
                },
                {
                    "email": "jane.smith@stanford.edu", 
                    "username": "janesmith",
                    "password": "testpass123",
                    "profile": {
                        "first_name": "Jane",
                        "last_name": "Smith",
                        "university": "Stanford University", 
                        "degree": "Mathematics",
                        "year": "Junior",
                        "major": "Applied Mathematics"
                    }
                },
                {
                    "email": "mike.wilson@berkeley.edu",
                    "username": "mikewilson", 
                    "password": "testpass123",
                    "profile": {
                        "first_name": "Mike",
                        "last_name": "Wilson",
                        "university": "UC Berkeley",
                        "degree": "Physics", 
                        "year": "Graduate",
                        "major": "Theoretical Physics"
                    }
                },
                {
                    "email": "sara.johnson@harvard.edu",
                    "username": "saraj",
                    "password": "testpass123", 
                    "profile": {
                        "first_name": "Sara",
                        "last_name": "Johnson",
                        "university": "Harvard University",
                        "degree": "Engineering",
                        "year": "Sophomore", 
                        "major": "Electrical Engineering"
                    }
                }
            ]
            
            created_users = []
            for user_data in users_data:
                # Create user
                hashed_password = get_password_hash(user_data["password"])
                user = User(
                    email=user_data["email"],
                    username=user_data["username"],
                    hashed_password=hashed_password,
                    is_active=True,
                    is_superuser=False
                )
                db.add(user)
                await db.flush()
                created_users.append(user)
                
                # Create user profile
                from app.models.user import UserProfile
                profile_data = user_data["profile"]
                profile = UserProfile(
                    user_id=user.id,
                    first_name=profile_data["first_name"],
                    last_name=profile_data["last_name"],
                    university=profile_data["university"],
                    degree=profile_data["degree"],
                    year=profile_data["year"],
                    major=profile_data["major"],
                    email_notifications=True,
                    push_notifications=True
                )
                db.add(profile)
                
                # Create user preferences
                from app.models.user import UserPreferences
                preferences = UserPreferences(
                    user_id=user.id,
                    preferred_difficulty="INTERMEDIATE",
                    daily_question_goal=10,
                    immediate_feedback=True,
                    show_explanations=True,
                    theme="light"
                )
                db.add(preferences)
            
            print(f"✅ Created {len(created_users)} users with profiles and preferences")
            
            # 2. Create Subjects
            print("📚 Creating subjects...")
            subjects_data = [
                {
                    "name": "Calculus I",
                    "code": "MATH101", 
                    "description": "Introduction to differential and integral calculus",
                    "department": "Mathematics",
                    "level": 1,
                    "credits": 4,
                    "category": "Mathematics",
                    "difficulty_average": 3
                },
                {
                    "name": "Physics I - Mechanics", 
                    "code": "PHYS101",
                    "description": "Classical mechanics, forces, energy, and motion",
                    "department": "Physics",
                    "level": 1, 
                    "credits": 4,
                    "category": "Science",
                    "difficulty_average": 4
                },
                {
                    "name": "Introduction to Programming",
                    "code": "CS101",
                    "description": "Programming fundamentals using Python",
                    "department": "Computer Science", 
                    "level": 1,
                    "credits": 3,
                    "category": "Computer Science",
                    "difficulty_average": 2
                },
                {
                    "name": "Linear Algebra",
                    "code": "MATH201",
                    "description": "Vector spaces, matrices, and linear transformations", 
                    "department": "Mathematics",
                    "level": 2,
                    "credits": 3,
                    "category": "Mathematics", 
                    "difficulty_average": 4
                },
                {
                    "name": "Data Structures and Algorithms",
                    "code": "CS201", 
                    "description": "Fundamental data structures and algorithmic techniques",
                    "department": "Computer Science",
                    "level": 2,
                    "credits": 4,
                    "category": "Computer Science",
                    "difficulty_average": 5
                }
            ]
            
            created_subjects = []
            for subject_data in subjects_data:
                subject = Subject(**subject_data)
                db.add(subject)
                await db.flush()
                created_subjects.append(subject)
            
            print(f"✅ Created {len(created_subjects)} subjects")
            
            # 3. Create Topics for each subject
            print("📖 Creating topics...")
            topics_data = {
                "Calculus I": [
                    {"name": "Limits", "description": "Limits of functions and continuity"},
                    {"name": "Derivatives", "description": "Differentiation rules and applications"},
                    {"name": "Integrals", "description": "Integration techniques and applications"}
                ],
                "Physics I - Mechanics": [
                    {"name": "Kinematics", "description": "Motion in one and two dimensions"},
                    {"name": "Forces", "description": "Newton's laws and force analysis"},
                    {"name": "Energy", "description": "Work, energy, and conservation laws"}
                ],
                "Introduction to Programming": [
                    {"name": "Variables and Data Types", "description": "Basic programming concepts"},
                    {"name": "Control Structures", "description": "Loops and conditional statements"},
                    {"name": "Functions", "description": "Function definition and usage"}
                ],
                "Linear Algebra": [
                    {"name": "Vectors", "description": "Vector operations and properties"},
                    {"name": "Matrices", "description": "Matrix operations and properties"},
                    {"name": "Linear Systems", "description": "Solving systems of linear equations"}
                ],
                "Data Structures and Algorithms": [
                    {"name": "Arrays and Lists", "description": "Linear data structures"},
                    {"name": "Trees and Graphs", "description": "Hierarchical and network structures"},
                    {"name": "Sorting and Searching", "description": "Fundamental algorithms"}
                ]
            }
            
            created_topics = []
            for subject in created_subjects:
                if subject.name in topics_data:
                    for topic_data in topics_data[subject.name]:
                        topic = Topic(
                            name=topic_data["name"],
                            description=topic_data["description"],
                            subject_id=subject.id,
                            difficulty_level="INTERMEDIATE",
                            is_active=True
                        )
                        db.add(topic)
                        await db.flush()
                        created_topics.append(topic)
            
            print(f"✅ Created {len(created_topics)} topics")
            
            # 4. Create Questions 
            print("❓ Creating questions...")
            questions_data = []
            
            # Sample questions for each subject
            calculus_questions = [
                {
                    "title": "Find the limit of (x²-1)/(x-1) as x approaches 1",
                    "content": "Calculate: lim(x→1) (x²-1)/(x-1)",
                    "answer": "2",
                    "question_type": "NUMERICAL",
                    "difficulty_level": "INTERMEDIATE"
                },
                {
                    "title": "Derivative of x³ + 2x² - 5x + 3",
                    "content": "Find the derivative of f(x) = x³ + 2x² - 5x + 3",
                    "answer": "3x² + 4x - 5",
                    "question_type": "SHORT_ANSWER", 
                    "difficulty_level": "BEGINNER"
                }
            ]
            
            physics_questions = [
                {
                    "title": "Projectile Motion Problem",
                    "content": "A ball is thrown horizontally from a 20m high building with initial velocity 15 m/s. How long does it take to hit the ground?",
                    "answer": "2.02 seconds",
                    "question_type": "NUMERICAL",
                    "difficulty_level": "INTERMEDIATE"
                },
                {
                    "title": "Newton's Second Law",
                    "content": "What is Newton's second law of motion?",
                    "answer": "F = ma (Force equals mass times acceleration)",
                    "question_type": "SHORT_ANSWER",
                    "difficulty_level": "BEGINNER"
                }
            ]
            
            programming_questions = [
                {
                    "title": "Python List Comprehension",
                    "content": "Write a list comprehension to create a list of squares of even numbers from 1 to 10",
                    "answer": "[x**2 for x in range(1, 11) if x % 2 == 0]",
                    "question_type": "SHORT_ANSWER",
                    "difficulty_level": "INTERMEDIATE"
                },
                {
                    "title": "Variable Assignment",
                    "content": "Which of the following is the correct way to assign a value to a variable in Python?",
                    "options": ["a) x := 5", "b) x = 5", "c) x == 5", "d) var x = 5"],
                    "answer": "b",
                    "question_type": "MULTIPLE_CHOICE",
                    "difficulty_level": "BEGINNER"
                }
            ]
            
            # Map questions to subjects
            subject_questions = {
                "Calculus I": calculus_questions,
                "Physics I - Mechanics": physics_questions, 
                "Introduction to Programming": programming_questions
            }
            
            created_questions = []
            for subject in created_subjects:
                if subject.name in subject_questions:
                    # Get first topic for this subject
                    subject_topics = [t for t in created_topics if t.subject_id == subject.id]
                    if subject_topics:
                        for q_data in subject_questions[subject.name]:
                            question = Question(
                                title=q_data["title"],
                                content=q_data["content"],
                                answer=q_data["answer"],
                                options=q_data.get("options"),
                                question_type=q_data["question_type"],
                                difficulty_level=q_data["difficulty_level"],
                                subject_id=subject.id,
                                topic_id=subject_topics[0].id,  # Assign to first topic
                                created_by=created_users[0].id,  # Created by first user
                                is_active=True,
                                is_verified=True,
                                priority_score=0.8
                            )
                            db.add(question)
                            await db.flush()
                            created_questions.append(question)
            
            print(f"✅ Created {len(created_questions)} questions")
            
            # 5. Create Practice Sessions and User Attempts
            print("🎯 Creating practice sessions and attempts...")
            
            # Create practice sessions for each user
            session_count = 0
            attempt_count = 0
            
            for user in created_users:
                # Create 2-3 practice sessions per user
                for i in range(2):
                    session = PracticeSession(
                        user_id=user.id,
                        session_type="QUICK_PRACTICE",
                        status="COMPLETED",
                        title=f"Practice Session {i+1}",
                        subject_id=created_subjects[i % len(created_subjects)].id,
                        difficulty_level="INTERMEDIATE",
                        started_at=datetime.utcnow() - timedelta(days=i+1),
                        completed_at=datetime.utcnow() - timedelta(days=i+1) + timedelta(minutes=30),
                        total_time_spent=30,
                        total_questions=len(created_questions),
                        correct_answers=int(len(created_questions) * 0.7),  # 70% accuracy
                        incorrect_answers=int(len(created_questions) * 0.3),
                        score_percentage=70.0
                    )
                    db.add(session)
                    await db.flush()
                    session_count += 1
                    
                    # Create attempts for each question in the session
                    for question in created_questions:
                        is_correct = (attempt_count % 10) < 7  # 70% correct rate
                        attempt = UserAttempt(
                            user_id=user.id,
                            question_id=question.id,
                            session_id=session.id,
                            user_answer="Sample answer" if question.question_type == "SHORT_ANSWER" else "b",
                            is_correct=is_correct,
                            status="CORRECT" if is_correct else "INCORRECT",
                            time_taken=30.0 + (attempt_count % 60),  # Varying time 
                            started_at=session.started_at,
                            submitted_at=session.started_at + timedelta(seconds=30),
                            hints_used=0 if is_correct else 1,
                            explanation_viewed=not is_correct,
                            confidence_level=4 if is_correct else 2
                        )
                        db.add(attempt)
                        attempt_count += 1
            
            print(f"✅ Created {session_count} practice sessions and {attempt_count} attempts")
            
            # 6. Create User Progress and Analytics
            print("📈 Creating user progress and analytics...")
            
            for user in created_users:
                for subject in created_subjects[:3]:  # Progress for first 3 subjects
                    progress = UserProgress(
                        user_id=user.id,
                        subject_id=subject.id,
                        total_questions_attempted=len(created_questions),
                        correct_answers=int(len(created_questions) * 0.7),
                        incorrect_answers=int(len(created_questions) * 0.3),
                        accuracy_rate=70.0,
                        average_time_per_question=45.0,
                        improvement_rate=0.15,
                        consistency_score=0.8,
                        mastery_level=0.7,
                        last_practiced_at=datetime.utcnow() - timedelta(days=1),
                        streak_days=5,
                        total_study_time=180,  # 3 hours
                        sessions_completed=3
                    )
                    db.add(progress)
                
                # Create daily analytics
                for days_ago in range(7):  # Last 7 days
                    date = datetime.utcnow() - timedelta(days=days_ago)
                    analytics = DailyUserActivity(
                        user_id=user.id,
                        date=date,
                        questions_attempted=10 + (days_ago % 5),
                        correct_answers=7 + (days_ago % 3),
                        incorrect_answers=3 - (days_ago % 3),
                        study_time_minutes=30 + (days_ago * 10),
                        sessions_completed=1 + (days_ago % 2),
                        accuracy_rate=0.7 + (days_ago * 0.05)
                    )
                    db.add(analytics)
            
            print("✅ Created user progress and daily analytics")
            
            # 7. Create some bookmarks
            print("🔖 Creating bookmarks...")
            bookmark_count = 0
            for user in created_users:
                for question in created_questions[:3]:  # Bookmark first 3 questions
                    bookmark = UserBookmark(
                        user_id=user.id,
                        question_id=question.id,
                        bookmark_type="REVIEW",
                        notes=f"Need to review this {question.title}",
                        priority=3,
                        is_active=True,
                        is_mastered=False
                    )
                    db.add(bookmark)
                    bookmark_count += 1
            
            print(f"✅ Created {bookmark_count} bookmarks")
            
            # Commit all changes
            await db.commit()
            print("\n🎉 Sample data creation completed successfully!")
            print(f"📊 Summary:")
            print(f"   • {len(created_users)} users with profiles and preferences")
            print(f"   • {len(created_subjects)} subjects")
            print(f"   • {len(created_topics)} topics")
            print(f"   • {len(created_questions)} questions")
            print(f"   • {session_count} practice sessions")
            print(f"   • {attempt_count} user attempts")
            print(f"   • {bookmark_count} bookmarks")
            print(f"   • User progress and analytics data")
            
        except Exception as e:
            await db.rollback()
            print(f"❌ Error creating sample data: {e}")
            raise

if __name__ == "__main__":
    asyncio.run(create_sample_data())
