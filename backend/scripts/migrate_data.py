#!/usr/bin/env python3
"""
Data migration script.
Handles database schema migrations and data transformations.
"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.append(str(backend_dir))

from sqlalchemy import text
from app.core.database import AsyncSessionLocal
from app.core.logging import get_logger

logger = get_logger(__name__)

class Migration:
    """Base migration class"""
    
    def __init__(self, name: str, version: str):
        self.name = name
        self.version = version
    
    async def up(self, db):
        """Apply migration"""
        raise NotImplementedError
    
    async def down(self, db):
        """Rollback migration"""
        raise NotImplementedError

class AddUserProfilesMigration(Migration):
    """Migration to add missing user profile fields"""
    
    def __init__(self):
        super().__init__("add_user_profiles", "1.0.0")
    
    async def up(self, db):
        """Add user profile fields if they don't exist"""
        try:
            # Add full_name to users if missing
            await db.execute(text("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS full_name VARCHAR(255)
            """))
            
            # Add is_verified to users if missing
            await db.execute(text("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS is_verified BOOLEAN DEFAULT FALSE
            """))
            
            logger.info("✅ User profile fields added successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to add user profile fields: {e}")
            raise

class UpdateQuestionPriorityMigration(Migration):
    """Migration to update question priority scores"""
    
    def __init__(self):
        super().__init__("update_question_priority", "1.1.0")
    
    async def up(self, db):
        """Update question priority scores based on difficulty"""
        try:
            # Update priority scores
            await db.execute(text("""
                UPDATE questions 
                SET priority_score = CASE 
                    WHEN difficulty_level = 'easy' THEN 3
                    WHEN difficulty_level = 'intermediate' THEN 5
                    WHEN difficulty_level = 'advanced' THEN 7
                    WHEN difficulty_level = 'expert' THEN 9
                    ELSE 5
                END
                WHERE priority_score IS NULL OR priority_score = 0
            """))
            
            logger.info("✅ Question priority scores updated")
            
        except Exception as e:
            logger.error(f"❌ Failed to update priority scores: {e}")
            raise

# Migration registry
MIGRATIONS = [
    AddUserProfilesMigration(),
    UpdateQuestionPriorityMigration(),
]

async def create_migration_table():
    """Create migration tracking table"""
    async with AsyncSessionLocal() as db:
        try:
            await db.execute(text("""
                CREATE TABLE IF NOT EXISTS migrations (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL UNIQUE,
                    version VARCHAR(50) NOT NULL,
                    applied_at TIMESTAMP DEFAULT NOW()
                )
            """))
            await db.commit()
            logger.info("✅ Migration table ready")
        except Exception as e:
            logger.error(f"❌ Failed to create migration table: {e}")
            raise

async def get_applied_migrations():
    """Get list of applied migrations"""
    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(text("SELECT name FROM migrations"))
            return [row[0] for row in result.fetchall()]
        except:
            return []  # Table might not exist yet

async def record_migration(migration: Migration):
    """Record migration as applied"""
    async with AsyncSessionLocal() as db:
        try:
            await db.execute(text("""
                INSERT INTO migrations (name, version, applied_at)
                VALUES (:name, :version, NOW())
                ON CONFLICT (name) DO NOTHING
            """), {
                "name": migration.name,
                "version": migration.version
            })
            await db.commit()
        except Exception as e:
            logger.error(f"❌ Failed to record migration: {e}")
            raise

async def run_migrations():
    """Run all pending migrations"""
    try:
        await create_migration_table()
        applied = await get_applied_migrations()
        
        pending = [m for m in MIGRATIONS if m.name not in applied]
        
        if not pending:
            logger.info("✅ All migrations already applied")
            return True
        
        logger.info(f"Running {len(pending)} pending migrations...")
        
        async with AsyncSessionLocal() as db:
            for migration in pending:
                try:
                    logger.info(f"Applying migration: {migration.name}")
                    await migration.up(db)
                    await db.commit()
                    await record_migration(migration)
                    logger.info(f"✅ Applied: {migration.name}")
                except Exception as e:
                    await db.rollback()
                    logger.error(f"❌ Failed migration {migration.name}: {e}")
                    raise
        
        logger.info("✅ All migrations completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        return False

async def main():
    """Main migration function"""
    print("🔄 PAPA Database Migration")
    print("=" * 40)
    
    success = await run_migrations()
    
    if success:
        print("🎉 Migration completed successfully!")
    else:
        print("❌ Migration failed!")
        return 1
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⏹️  Migration interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Unexpected error: {str(e)}")
        sys.exit(1)
