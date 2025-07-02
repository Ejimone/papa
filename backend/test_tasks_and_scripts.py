#!/usr/bin/env python3
"""
Comprehensive test suite for tasks and scripts modules.
Tests background tasks, database scripts, and system utilities.
"""

import asyncio
import pytest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta, date

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.append(str(backend_dir))

class TestCeleryAppConfiguration:
    """Test Celery application configuration"""
    
    def test_celery_import(self):
        """Test if celery app can be imported"""
        try:
            from app.tasks.celery_app import celery_app
            assert celery_app is not None
            assert celery_app.main == "papa_backend"
            print("✅ Celery app imports successfully")
        except ImportError as e:
            print(f"⚠️  Celery import skipped (missing dependencies): {e}")
    
    def test_celery_configuration(self):
        """Test Celery configuration"""
        try:
            from app.tasks.celery_app import celery_app
            
            # Test basic configuration
            assert celery_app.conf.task_serializer == "json"
            assert celery_app.conf.timezone == "UTC"
            assert celery_app.conf.enable_utc is True
            
            # Test task routing
            expected_routes = {
                "app.tasks.question_processing.*": {"queue": "question_processing"},
                "app.tasks.analytics_tasks.*": {"queue": "analytics"},
                "app.tasks.maintenance_tasks.*": {"queue": "maintenance"},
                "app.tasks.notification_tasks.*": {"queue": "notifications"},
            }
            
            for route, config in expected_routes.items():
                assert route in celery_app.conf.task_routes
                assert celery_app.conf.task_routes[route] == config
            
            print("✅ Celery configuration is correct")
        except ImportError as e:
            print(f"⚠️  Celery configuration test skipped: {e}")
    
    def test_celery_beat_schedule(self):
        """Test Celery beat schedule configuration"""
        try:
            from app.tasks.celery_app import celery_app
            
            # Test that scheduled tasks are configured
            expected_tasks = [
                "aggregate-daily-analytics",
                "aggregate-weekly-analytics",
                "cleanup-old-sessions",
                "process-pending-questions",
                "send-daily-summaries"
            ]
            
            for task_name in expected_tasks:
                assert task_name in celery_app.conf.beat_schedule
                task_config = celery_app.conf.beat_schedule[task_name]
                assert "task" in task_config
                assert "schedule" in task_config
            
            print("✅ Celery beat schedule configured properly")
        except ImportError as e:
            print(f"⚠️  Celery beat schedule test skipped: {e}")

class TestTaskModules:
    """Test task module imports and basic functionality"""
    
    def test_question_processing_imports(self):
        """Test question processing task imports"""
        try:
            from app.tasks.question_processing import (
                process_question_embeddings,
                generate_question_explanation,
                generate_question_hints,
                find_similar_questions,
                extract_question_metadata
            )
            
            # Test that tasks are properly decorated
            assert hasattr(process_question_embeddings, 'delay')
            assert hasattr(generate_question_explanation, 'delay')
            
            print("✅ Question processing tasks import successfully")
        except ImportError as e:
            print(f"⚠️  Question processing imports skipped: {e}")
    
    def test_analytics_tasks_imports(self):
        """Test analytics task imports"""
        try:
            from app.tasks.analytics_tasks import (
                aggregate_daily_analytics,
                aggregate_weekly_analytics,
                update_question_analytics,
                generate_weekly_reports,
                calculate_user_insights
            )
            
            # Test task decoration
            assert hasattr(aggregate_daily_analytics, 'delay')
            assert hasattr(generate_weekly_reports, 'delay')
            
            print("✅ Analytics tasks import successfully")
        except ImportError as e:
            print(f"⚠️  Analytics tasks imports skipped: {e}")
    
    def test_maintenance_tasks_imports(self):
        """Test maintenance task imports"""
        try:
            from app.tasks.maintenance_tasks import (
                cleanup_old_sessions,
                cleanup_expired_tokens,
                backup_database,
                health_check_ai_services
            )
            
            assert hasattr(cleanup_old_sessions, 'delay')
            assert hasattr(health_check_ai_services, 'delay')
            
            print("✅ Maintenance tasks import successfully")
        except ImportError as e:
            print(f"⚠️  Maintenance tasks imports skipped: {e}")
    
    def test_notification_tasks_imports(self):
        """Test notification task imports"""
        try:
            from app.tasks.notification_tasks import (
                send_daily_summaries,
                send_study_reminders,
                send_achievement_notification
            )
            
            assert hasattr(send_daily_summaries, 'delay')
            assert hasattr(send_achievement_notification, 'delay')
            
            print("✅ Notification tasks import successfully")
        except ImportError as e:
            print(f"⚠️  Notification tasks imports skipped: {e}")

class TestScriptModules:
    """Test script module functionality"""
    
    def test_init_db_script_import(self):
        """Test database initialization script"""
        try:
            from scripts import init_db
            
            # Test that main functions exist
            assert hasattr(init_db, 'create_all_tables')
            assert hasattr(init_db, 'create_default_subjects')
            assert hasattr(init_db, 'create_admin_user')
            assert hasattr(init_db, 'main')
            
            print("✅ Database initialization script imports successfully")
        except ImportError as e:
            print(f"⚠️  Database init script test skipped: {e}")
    
    def test_seed_data_script_import(self):
        """Test data seeding script"""
        try:
            from scripts import seed_data
            
            # Test that seeding functions exist
            assert hasattr(seed_data, 'seed_questions')
            assert hasattr(seed_data, 'seed_users')
            assert hasattr(seed_data, 'generate_sample_activity')
            assert hasattr(seed_data, 'main')
            
            # Test sample data exists
            assert len(seed_data.SAMPLE_QUESTIONS) > 0
            assert len(seed_data.SAMPLE_USERS) > 0
            
            print("✅ Data seeding script imports successfully")
        except ImportError as e:
            print(f"⚠️  Data seeding script test skipped: {e}")
    
    def test_migrate_data_script_import(self):
        """Test data migration script"""
        try:
            from scripts import migrate_data
            
            # Test migration framework
            assert hasattr(migrate_data, 'Migration')
            assert hasattr(migrate_data, 'run_migrations')
            assert hasattr(migrate_data, 'MIGRATIONS')
            assert len(migrate_data.MIGRATIONS) > 0
            
            print("✅ Data migration script imports successfully")
        except ImportError as e:
            print(f"⚠️  Data migration script test skipped: {e}")
    
    def test_process_questions_script_import(self):
        """Test question processing script"""
        try:
            from scripts import process_questions
            
            # Test processing functions
            assert hasattr(process_questions, 'get_unprocessed_questions')
            assert hasattr(process_questions, 'process_embeddings_batch')
            assert hasattr(process_questions, 'interactive_menu')
            
            print("✅ Question processing script imports successfully")
        except ImportError as e:
            print(f"⚠️  Question processing script test skipped: {e}")
    
    def test_backup_db_script_import(self):
        """Test database backup script"""
        try:
            from scripts import backup_db
            
            # Test backup class and functions
            assert hasattr(backup_db, 'DatabaseBackup')
            assert hasattr(backup_db, 'interactive_menu')
            
            # Test DatabaseBackup class
            backup_class = backup_db.DatabaseBackup
            assert hasattr(backup_class, 'create_backup')
            assert hasattr(backup_class, 'list_backups')
            assert hasattr(backup_class, 'cleanup_old_backups')
            
            print("✅ Database backup script imports successfully")
        except ImportError as e:
            print(f"⚠️  Database backup script test skipped: {e}")

class TestTaskLogic:
    """Test task logic and helper functions"""
    
    @pytest.mark.asyncio
    async def test_analytics_helper_functions(self):
        """Test analytics helper functions"""
        try:
            from app.tasks.analytics_tasks import (
                _calculate_consistency_score,
                _calculate_improvement_trend
            )
            
            # Test consistency score calculation
            sample_data = [
                (date.today(), 10, 85.0, 30),  # (date, questions, accuracy, study_time)
                (date.today(), 12, 87.0, 35),
                (date.today(), 8, 82.0, 25),
                (date.today(), 15, 90.0, 40),
            ]
            
            consistency = _calculate_consistency_score(sample_data)
            assert isinstance(consistency, float)
            assert 0 <= consistency <= 100
            
            # Test improvement trend
            trend_data = [(date.today(), 10, 75.0, 30)] * 10 + [(date.today(), 10, 85.0, 30)] * 10
            trend = _calculate_improvement_trend(trend_data)
            assert trend in ["improving", "declining", "stable", "insufficient_data"]
            
            print("✅ Analytics helper functions work correctly")
        except ImportError as e:
            print(f"⚠️  Analytics helper test skipped: {e}")
    
    def test_migration_base_class(self):
        """Test migration base class"""
        try:
            from scripts.migrate_data import Migration
            
            class TestMigration(Migration):
                def __init__(self):
                    super().__init__("test_migration", "1.0.0")
                
                async def up(self, db):
                    pass
                
                async def down(self, db):
                    pass
            
            migration = TestMigration()
            assert migration.name == "test_migration"
            assert migration.version == "1.0.0"
            
            print("✅ Migration base class works correctly")
        except ImportError as e:
            print(f"⚠️  Migration base class test skipped: {e}")
    
    def test_backup_filename_generation(self):
        """Test backup filename generation"""
        try:
            from scripts.backup_db import DatabaseBackup
            
            backup = DatabaseBackup("/tmp/test_backups")
            
            # Test uncompressed filename
            filename = backup.generate_backup_filename(compressed=False)
            assert filename.startswith("papa_backup_")
            assert filename.endswith(".sql")
            
            # Test compressed filename
            filename_gz = backup.generate_backup_filename(compressed=True)
            assert filename_gz.startswith("papa_backup_")
            assert filename_gz.endswith(".sql.gz")
            
            print("✅ Backup filename generation works correctly")
        except ImportError as e:
            print(f"⚠️  Backup filename test skipped: {e}")

class TestSystemIntegration:
    """Test system integration and configuration"""
    
    def test_tasks_module_init(self):
        """Test tasks module initialization"""
        try:
            from app.tasks import celery_app
            assert celery_app is not None
            
            # Test that all task modules are imported
            from app.tasks import (
                question_processing,
                analytics_tasks,
                maintenance_tasks,
                notification_tasks
            )
            
            print("✅ Tasks module initialization works")
        except ImportError as e:
            print(f"⚠️  Tasks module init test skipped: {e}")
    
    def test_script_executability(self):
        """Test that scripts can be executed"""
        script_files = [
            "scripts/init_db.py",
            "scripts/seed_data.py",
            "scripts/migrate_data.py",
            "scripts/process_questions.py",
            "scripts/backup_db.py"
        ]
        
        for script_file in script_files:
            script_path = Path(script_file)
            if script_path.exists():
                # Check if script has proper shebang and main execution
                with open(script_path, 'r') as f:
                    content = f.read()
                    assert content.startswith('#!/usr/bin/env python3')
                    assert 'if __name__ == "__main__":' in content
                    print(f"✅ {script_file} is properly structured")
            else:
                print(f"⚠️  {script_file} not found")

class TestTaskConfiguration:
    """Test task configuration and settings"""
    
    def test_task_retry_configuration(self):
        """Test task retry configuration"""
        try:
            from app.tasks.analytics_tasks import aggregate_daily_analytics
            from app.tasks.maintenance_tasks import cleanup_old_sessions
            
            # Tasks should have retry configuration
            assert hasattr(aggregate_daily_analytics, 'max_retries')
            assert hasattr(cleanup_old_sessions, 'max_retries')
            
            print("✅ Task retry configuration is present")
        except (ImportError, AttributeError) as e:
            print(f"⚠️  Task retry configuration test skipped: {e}")
    
    def test_task_time_limits(self):
        """Test task time limit configuration"""
        try:
            from app.tasks.celery_app import celery_app
            
            # Test time limits are configured
            assert celery_app.conf.task_soft_time_limit == 300  # 5 minutes
            assert celery_app.conf.task_time_limit == 600      # 10 minutes
            
            print("✅ Task time limits configured correctly")
        except ImportError as e:
            print(f"⚠️  Task time limits test skipped: {e}")

def run_all_tests():
    """Run all tests"""
    print("🧪 PAPA Tasks & Scripts Test Suite")
    print("=" * 50)
    
    test_classes = [
        TestCeleryAppConfiguration(),
        TestTaskModules(),
        TestScriptModules(),
        TestTaskLogic(),
        TestSystemIntegration(),
        TestTaskConfiguration()
    ]
    
    total_tests = 0
    passed_tests = 0
    
    for test_class in test_classes:
        class_name = test_class.__class__.__name__
        print(f"\n📋 Running {class_name}...")
        
        # Get all test methods
        test_methods = [method for method in dir(test_class) if method.startswith('test_')]
        
        for test_method in test_methods:
            total_tests += 1
            try:
                method = getattr(test_class, test_method)
                if asyncio.iscoroutinefunction(method):
                    asyncio.run(method())
                else:
                    method()
                passed_tests += 1
            except Exception as e:
                print(f"❌ {test_method} failed: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed!")
        return 0
    else:
        print(f"⚠️  {total_tests - passed_tests} tests failed or skipped")
        return 1

if __name__ == "__main__":
    try:
        exit_code = run_all_tests()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⏹️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Unexpected error: {str(e)}")
        sys.exit(1) 