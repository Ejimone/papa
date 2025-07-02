#!/usr/bin/env python3
"""
Database initialization script.
Creates all tables, indexes, and sets up initial system data.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.append(str(backend_dir))

from sqlalchemy import text
from app.core.database import engine, AsyncSessionLocal
from app.models.base import Base
from app.models import user, subject, question, practice, analytics
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

async def create_all_tables():
    """Create all database tables"""
    try:
        async with engine.begin() as conn:
            logger.info("Creating all database tables...")
            await conn.run_sync(Base.metadata.create_all)
            logger.info("✅ All tables created successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to create tables: {e}")
        return False

async def create_indexes():
    """Create additional database indexes for performance"""
    try:
        async with AsyncSessionLocal() as db:
            indexes = [
                # User indexes
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_email ON users(email)",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_active ON users(is_active) WHERE is_active = true",
                
                # Question indexes
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_questions_subject ON questions(subject_id)",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_questions_topic ON questions(topic_id)",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_questions_difficulty ON questions(difficulty_level)",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_questions_active ON questions(is_active) WHERE is_active = true",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_questions_priority ON questions(priority_score DESC)",
                
                # Practice session indexes
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_practice_sessions_user ON practice_sessions(user_id)",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_practice_sessions_created ON practice_sessions(created_at DESC)",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_practice_sessions_status ON practice_sessions(status)",
                
                # User attempt indexes
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_user_attempts_user ON user_attempts(user_id)",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_user_attempts_question ON user_attempts(question_id)",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_user_attempts_session ON user_attempts(session_id)",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_user_attempts_created ON user_attempts(created_at DESC)",
                
                # Analytics indexes
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_daily_activities_user_date ON daily_user_activities(user_id, date DESC)",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_weekly_activities_user_year_week ON weekly_user_activities(user_id, year, week_number)",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_user_analytics_user ON user_analytics(user_id)",
                
                # Subject and topic indexes
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_topics_subject ON topics(subject_id)",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_subjects_active ON subjects(is_active) WHERE is_active = true",
            ]
            
            logger.info("Creating performance indexes...")
            for index_sql in indexes:
                try:
                    await db.execute(text(index_sql))
                    logger.info(f"✅ Created index: {index_sql.split('idx_')[1].split(' ')[0]}")
                except Exception as e:
                    if "already exists" in str(e):
                        logger.info(f"ℹ️  Index already exists: {index_sql.split('idx_')[1].split(' ')[0]}")
                    else:
                        logger.warning(f"⚠️  Index creation failed: {e}")
            
            await db.commit()
            logger.info("✅ All indexes processed")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to create indexes: {e}")
        return False

async def create_default_subjects():
    """Create default subjects and topics"""
    try:
        async with AsyncSessionLocal() as db:
            # Check if subjects already exist
            result = await db.execute(text("SELECT COUNT(*) FROM subjects"))
            count = result.scalar()
            
            if count > 0:
                logger.info("ℹ️  Subjects already exist, skipping creation")
                return True
            
            logger.info("Creating default subjects and topics...")
            
            # Default subjects data
            subjects_data = [
                {
                    "name": "Mathematics",
                    "code": "MATH",
                    "description": "Core mathematics subjects including algebra, calculus, geometry, and statistics",
                    "department": "Mathematics",
                    "category": "STEM",
                    "is_active": True,
                    "is_popular": True,
                    "topics": [
                        {"name": "Algebra", "description": "Linear and quadratic equations, polynomials", "difficulty_level": "intermediate"},
                        {"name": "Calculus", "description": "Differential and integral calculus", "difficulty_level": "advanced"},
                        {"name": "Geometry", "description": "Euclidean geometry, trigonometry", "difficulty_level": "intermediate"},
                        {"name": "Statistics", "description": "Descriptive and inferential statistics", "difficulty_level": "intermediate"},
                    ]
                },
                {
                    "name": "Physics",
                    "code": "PHYS",
                    "description": "Fundamental physics concepts and applications",
                    "department": "Physics",
                    "category": "STEM",
                    "is_active": True,
                    "is_popular": True,
                    "topics": [
                        {"name": "Mechanics", "description": "Classical mechanics, motion, forces", "difficulty_level": "intermediate"},
                        {"name": "Thermodynamics", "description": "Heat, temperature, energy transfer", "difficulty_level": "advanced"},
                        {"name": "Electromagnetism", "description": "Electric and magnetic fields", "difficulty_level": "advanced"},
                        {"name": "Optics", "description": "Light, reflection, refraction", "difficulty_level": "intermediate"},
                    ]
                },
                {
                    "name": "Computer Science",
                    "code": "CS",
                    "description": "Programming, algorithms, and computer science theory",
                    "department": "Computer Science",
                    "category": "STEM",
                    "is_active": True,
                    "is_popular": True,
                    "topics": [
                        {"name": "Programming Fundamentals", "description": "Basic programming concepts", "difficulty_level": "beginner"},
                        {"name": "Data Structures", "description": "Arrays, lists, trees, graphs", "difficulty_level": "intermediate"},
                        {"name": "Algorithms", "description": "Sorting, searching, optimization", "difficulty_level": "advanced"},
                        {"name": "Database Systems", "description": "SQL, database design", "difficulty_level": "intermediate"},
                    ]
                },
                {
                    "name": "Chemistry",
                    "code": "CHEM", 
                    "description": "General chemistry, organic chemistry, and biochemistry",
                    "department": "Chemistry",
                    "category": "STEM",
                    "is_active": True,
                    "is_popular": True,
                    "topics": [
                        {"name": "General Chemistry", "description": "Atomic structure, chemical bonds", "difficulty_level": "intermediate"},
                        {"name": "Organic Chemistry", "description": "Carbon compounds, reactions", "difficulty_level": "advanced"},
                        {"name": "Physical Chemistry", "description": "Thermodynamics, kinetics", "difficulty_level": "advanced"},
                    ]
                },
                {
                    "name": "Biology",
                    "code": "BIO",
                    "description": "Life sciences including molecular biology, genetics, and ecology",
                    "department": "Biology",
                    "category": "Life Sciences",
                    "is_active": True,
                    "is_popular": True,
                    "topics": [
                        {"name": "Cell Biology", "description": "Cell structure and function", "difficulty_level": "intermediate"},
                        {"name": "Genetics", "description": "DNA, inheritance patterns", "difficulty_level": "intermediate"},
                        {"name": "Ecology", "description": "Ecosystems, environmental interactions", "difficulty_level": "intermediate"},
                    ]
                }
            ]
            
            # Insert subjects and topics
            for subject_data in subjects_data:
                topics = subject_data.pop("topics")
                
                # Insert subject
                subject_insert = text("""
                    INSERT INTO subjects (name, code, description, department, category, is_active, is_popular, 
                                        total_questions, total_students, difficulty_average, created_at, updated_at)
                    VALUES (:name, :code, :description, :department, :category, :is_active, :is_popular,
                           0, 0, 3, NOW(), NOW())
                    RETURNING id
                """)
                
                result = await db.execute(subject_insert, subject_data)
                subject_id = result.scalar()
                
                # Insert topics for this subject
                for i, topic in enumerate(topics, 1):
                    topic_insert = text("""
                        INSERT INTO topics (name, description, subject_id, level, order_index, difficulty_level,
                                          is_active, total_questions, completion_rate, created_at, updated_at)
                        VALUES (:name, :description, :subject_id, 1, :order_index, :difficulty_level,
                               true, 0, 0, NOW(), NOW())
                    """)
                    
                    await db.execute(topic_insert, {
                        "name": topic["name"],
                        "description": topic["description"],
                        "subject_id": subject_id,
                        "order_index": i,
                        "difficulty_level": topic["difficulty_level"]
                    })
                
                logger.info(f"✅ Created subject: {subject_data['name']} with {len(topics)} topics")
            
            await db.commit()
            logger.info("✅ All default subjects and topics created")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to create default subjects: {e}")
        return False

async def create_admin_user():
    """Create default admin user if it doesn't exist"""
    try:
        async with AsyncSessionLocal() as db:
            # Check if admin user exists
            admin_check = text("SELECT id FROM users WHERE email = :email")
            result = await db.execute(admin_check, {"email": "admin@papa.com"})
            
            if result.scalar():
                logger.info("ℹ️  Admin user already exists")
                return True
            
            logger.info("Creating default admin user...")
            
            from app.core.security import get_password_hash
            
            # Create admin user
            admin_insert = text("""
                INSERT INTO users (email, hashed_password, full_name, is_active, is_verified, created_at, updated_at)
                VALUES (:email, :hashed_password, :full_name, true, true, NOW(), NOW())
                RETURNING id
            """)
            
            hashed_password = get_password_hash("admin123")  # Change this in production!
            
            result = await db.execute(admin_insert, {
                "email": "admin@papa.com",
                "hashed_password": hashed_password,
                "full_name": "System Administrator"
            })
            
            admin_user_id = result.scalar()
            
            # Create admin profile
            profile_insert = text("""
                INSERT INTO user_profiles (user_id, academic_level, institution, field_of_study, 
                                         bio, timezone, language, created_at, updated_at)
                VALUES (:user_id, 'administrator', 'PAPA System', 'Administration',
                       'System Administrator Account', 'UTC', 'en', NOW(), NOW())
            """)
            
            await db.execute(profile_insert, {"user_id": admin_user_id})
            
            # Create admin preferences
            preferences_insert = text("""
                INSERT INTO user_preferences (user_id, preferred_difficulty, daily_question_goal,
                                           study_reminder_enabled, dark_mode, notifications_enabled,
                                           email_notifications, created_at, updated_at)
                VALUES (:user_id, 'medium', 0, false, false, true, true, NOW(), NOW())
            """)
            
            await db.execute(preferences_insert, {"user_id": admin_user_id})
            
            await db.commit()
            
            logger.info("✅ Admin user created successfully")
            logger.warning("⚠️  Default admin password is 'admin123' - CHANGE THIS IN PRODUCTION!")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to create admin user: {e}")
        return False

async def verify_setup():
    """Verify that everything was set up correctly"""
    try:
        async with AsyncSessionLocal() as db:
            # Check tables exist
            tables_check = text("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
                ORDER BY table_name
            """)
            
            result = await db.execute(tables_check)
            tables = [row[0] for row in result.fetchall()]
            
            expected_tables = [
                'users', 'user_profiles', 'user_preferences', 'subjects', 'topics', 
                'questions', 'practice_sessions', 'user_attempts', 'user_analytics'
            ]
            
            missing_tables = [table for table in expected_tables if table not in tables]
            
            if missing_tables:
                logger.error(f"❌ Missing tables: {missing_tables}")
                return False
            
            # Check data exists
            counts = {}
            for table in ['users', 'subjects', 'topics']:
                count_result = await db.execute(text(f"SELECT COUNT(*) FROM {table}"))
                counts[table] = count_result.scalar()
            
            logger.info("📊 Database verification:")
            logger.info(f"   Tables created: {len(tables)}")
            logger.info(f"   Users: {counts['users']}")
            logger.info(f"   Subjects: {counts['subjects']}")
            logger.info(f"   Topics: {counts['topics']}")
            
            if all(count > 0 for count in counts.values()):
                logger.info("✅ Database setup verification passed")
                return True
            else:
                logger.error("❌ Database setup verification failed - missing data")
                return False
                
    except Exception as e:
        logger.error(f"❌ Database verification failed: {e}")
        return False

async def main():
    """Main initialization function"""
    print("🚀 PAPA Database Initialization")
    print("=" * 50)
    
    success = True
    
    # Step 1: Create tables
    logger.info("Step 1: Creating database tables...")
    if not await create_all_tables():
        success = False
    
    # Step 2: Create indexes
    logger.info("\nStep 2: Creating performance indexes...")
    if not await create_indexes():
        success = False
    
    # Step 3: Create default data
    logger.info("\nStep 3: Creating default subjects...")
    if not await create_default_subjects():
        success = False
    
    # Step 4: Create admin user
    logger.info("\nStep 4: Creating admin user...")
    if not await create_admin_user():
        success = False
    
    # Step 5: Verify setup
    logger.info("\nStep 5: Verifying setup...")
    if not await verify_setup():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Database initialization completed successfully!")
        print("\n📝 Next steps:")
        print("   1. Change the admin password (admin@papa.com / admin123)")
        print("   2. Add questions using the question management system")
        print("   3. Configure email settings for notifications")
        print("   4. Set up Celery workers for background tasks")
    else:
        print("❌ Database initialization failed!")
        print("   Check the logs above for specific error details")
        return 1
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⏹️  Initialization interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Unexpected error: {str(e)}")
        sys.exit(1)
