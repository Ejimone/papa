#!/usr/bin/env python3
"""
Test script for all repository classes with sample data
"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.repositories.user_repository import user_repo
from app.repositories.question_repository import question_repo
from app.repositories.subject_repository import subject_repo
from app.repositories.practice_repository import (
    practice_session_repo, user_attempt_repo, user_bookmark_repo, 
    user_progress_repo
)
from app.repositories.analytics_repository import (
    analytics_repo, daily_activity_repo, subject_performance_repo
)

async def test_all_repositories():
    """Test all repository classes with actual data"""
    
    # Get database session
    async for db in get_db():
        try:
            print("🧪 Testing All Repository Classes with Sample Data\n")
            
            # Test User Repository
            print("👥 Testing User Repository:")
            user_count = await user_repo.count(db)
            print(f"   • Total users: {user_count}")
            
            active_users = await user_repo.get_active_users(db, days=30, limit=5)
            print(f"   • Active users (last 30 days): {len(active_users)}")
            
            leaderboard = await user_repo.get_leaderboard(db, metric="accuracy", days=30, limit=5)
            print(f"   • Accuracy leaderboard entries: {len(leaderboard)}")
            
            # Test Subject Repository  
            print("\n📚 Testing Subject Repository:")
            subject_count = await subject_repo.count(db)
            print(f"   • Total subjects: {subject_count}")
            
            subjects = await subject_repo.get_multi(db, limit=5)
            print(f"   • Retrieved subjects: {[s.name for s in subjects]}")
            
            if subjects:
                popular_subjects = await subject_repo.get_popular_subjects(db, limit=3)
                print(f"   • Popular subjects: {len(popular_subjects)}")
            
            # Test Question Repository
            print("\n❓ Testing Question Repository:")
            question_count = await question_repo.count(db)
            print(f"   • Total questions: {question_count}")
            
            questions = await question_repo.get_multi(db, limit=3)
            print(f"   • Retrieved questions: {len(questions)}")
            
            if questions:
                priority_questions = await question_repo.get_high_priority_questions(db, limit=3)
                print(f"   • High priority questions: {len(priority_questions)}")
                
                random_questions = await question_repo.get_random_questions(db, count=2)
                print(f"   • Random questions: {len(random_questions)}")
            
            # Test Practice Repository
            print("\n🎯 Testing Practice Repository:")
            session_count = await practice_session_repo.count(db)
            print(f"   • Total practice sessions: {session_count}")
            
            attempt_count = await user_attempt_repo.count(db)
            print(f"   • Total user attempts: {attempt_count}")
            
            bookmark_count = await user_bookmark_repo.count(db)
            print(f"   • Total bookmarks: {bookmark_count}")
            
            # Get recent sessions
            recent_sessions = await practice_session_repo.get_multi(db, limit=3)
            print(f"   • Recent sessions: {len(recent_sessions)}")
            
            # Test Analytics Repository
            print("\n📈 Testing Analytics Repository:")
            daily_analytics_count = await daily_activity_repo.count(db)
            print(f"   • Total daily analytics records: {daily_analytics_count}")
            
            subject_analytics_count = await subject_performance_repo.count(db)
            print(f"   • Total subject performance analytics: {subject_analytics_count}")
            
            # Get user dashboard data if we have users
            if user_count > 0:
                users = await user_repo.get_multi(db, limit=1)
                if users:
                    user_id = users[0].id
                    dashboard_data = await analytics_repo.get_user_dashboard_data(db, user_id=user_id)
                    print(f"   • User dashboard data for user {user_id}: {'Found' if dashboard_data else 'Not found'}")
            
            print("\n✅ All repository tests completed successfully!")
            
        except Exception as e:
            print(f"❌ Error during repository testing: {e}")
            import traceback
            traceback.print_exc()
        finally:
            break

if __name__ == "__main__":
    asyncio.run(test_all_repositories())
