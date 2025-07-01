#!/usr/bin/env python3
"""
Quick database schema fix script
Adds missing columns and creates tables as needed.
"""

import asyncio
import sys
import os
from sqlalchemy import text

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import engine
from app.models.base import Base
from app.models import user, subject, question, practice, analytics

async def fix_database_schema():
    """Fix database schema issues"""
    from app.core.database import engine
    
    try:
        async with engine.begin() as conn:
            print("🔧 Fixing database schema...")
            
            # Check if users table exists and add missing columns
            print("📝 Checking users table...")
            try:
                # Add full_name column if it doesn't exist
                await conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN IF NOT EXISTS full_name VARCHAR(255);
                """))
                print("   ✅ Added full_name column to users table")
                
                # Add is_verified column if it doesn't exist
                await conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN IF NOT EXISTS is_verified BOOLEAN DEFAULT FALSE;
                """))
                print("   ✅ Added is_verified column to users table")
                
            except Exception as e:
                print(f"   ⚠️  Users table update issue: {e}")
            
            # Create all tables that don't exist
            print("📝 Creating missing tables...")
            await conn.run_sync(Base.metadata.create_all)
            print("   ✅ All tables created/verified")
            
            await conn.commit()
            print("✅ Database schema fixed successfully!")
            
    except Exception as e:
        print(f"❌ Database schema fix failed: {e}")
        return False
    
    finally:
        await engine.dispose()
    
    return True

async def create_sample_data():
    """Create some sample data for testing"""
    from app.core.database import engine
    
    try:
        async with engine.begin() as conn:
            print("📦 Creating sample data...")
            
            # Create sample subjects
            await conn.execute(text("""
                INSERT INTO subjects (name, description, is_active, is_popular, total_questions, total_students, difficulty_average, created_at, updated_at)
                VALUES 
                    ('Mathematics', 'Core mathematics subjects including algebra, calculus, and geometry', true, true, 0, 0, 3, NOW(), NOW()),
                    ('Physics', 'Fundamental physics concepts and applications', true, true, 0, 0, 4, NOW(), NOW()),
                    ('Computer Science', 'Programming, algorithms, and computer science theory', true, true, 0, 0, 3, NOW(), NOW())
                ON CONFLICT (name) DO NOTHING;
            """))
            
            # Create sample topics
            await conn.execute(text("""
                INSERT INTO topics (name, description, subject_id, level, order_index, difficulty_level, is_active, total_questions, completion_rate, created_at, updated_at)
                SELECT 
                    'Algebra', 'Basic algebraic concepts and equations', s.id, 1, 1, 'intermediate', true, 0, 0, NOW(), NOW()
                FROM subjects s WHERE s.name = 'Mathematics'
                ON CONFLICT (name, subject_id) DO NOTHING;
            """))
            
            await conn.execute(text("""
                INSERT INTO topics (name, description, subject_id, level, order_index, difficulty_level, is_active, total_questions, completion_rate, created_at, updated_at)
                SELECT 
                    'Mechanics', 'Classical mechanics and motion', s.id, 1, 1, 'intermediate', true, 0, 0, NOW(), NOW()
                FROM subjects s WHERE s.name = 'Physics'
                ON CONFLICT (name, subject_id) DO NOTHING;
            """))
            
            await conn.commit()
            print("   ✅ Sample subjects and topics created")
            
    except Exception as e:
        print(f"   ⚠️  Sample data creation issue: {e}")
    
    finally:
        await engine.dispose()

async def main():
    """Main function"""
    print("🚀 Database Schema Fix Tool")
    print("=" * 40)
    
    # Fix schema
    if await fix_database_schema():
        # Create sample data
        await create_sample_data()
        print("\n🎉 Database is ready for testing!")
        print("💡 You can now test authentication and other endpoints")
    else:
        print("\n❌ Schema fix failed. Check your database connection.")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⏹️  Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Unexpected error: {str(e)}")
        sys.exit(1) 