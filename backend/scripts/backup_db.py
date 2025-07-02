#!/usr/bin/env python3
"""
Database backup script.
Creates backups of the database with optional compression and retention management.
"""

import asyncio
import sys
import os
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
import gzip
import shutil

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.append(str(backend_dir))

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

class DatabaseBackup:
    """Database backup manager"""
    
    def __init__(self, backup_dir: str = None):
        self.backup_dir = Path(backup_dir or getattr(settings, 'BACKUP_DIRECTORY', '/tmp/backups'))
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_backup_filename(self, compressed: bool = False) -> str:
        """Generate backup filename with timestamp"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        extension = ".sql.gz" if compressed else ".sql"
        return f"papa_backup_{timestamp}{extension}"
    
    async def create_backup(self, compressed: bool = True) -> dict:
        """Create database backup"""
        try:
            backup_filename = self.generate_backup_filename(compressed)
            backup_path = self.backup_dir / backup_filename
            temp_path = self.backup_dir / f"temp_{backup_filename.replace('.gz', '')}"
            
            logger.info(f"Creating backup: {backup_filename}")
            
            # Get database URL
            db_url = settings.database_url
            
            if not db_url.startswith('postgresql'):
                raise ValueError("Only PostgreSQL backups are currently supported")
            
            # Create pg_dump command
            cmd = [
                'pg_dump',
                '--no-password',
                '--format=plain',
                '--clean',
                '--if-exists',
                '--verbose',
                '--file', str(temp_path),
                db_url
            ]
            
            # Execute backup
            logger.info("Running pg_dump...")
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=1800  # 30 minutes timeout
            )
            
            if process.returncode != 0:
                raise RuntimeError(f"pg_dump failed: {process.stderr}")
            
            # Compress if requested
            if compressed:
                logger.info("Compressing backup...")
                with open(temp_path, 'rb') as f_in:
                    with gzip.open(backup_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                
                # Remove uncompressed file
                temp_path.unlink()
            else:
                # Move temp file to final location
                temp_path.rename(backup_path)
            
            # Get backup size
            backup_size = backup_path.stat().st_size
            
            logger.info(f"✅ Backup created: {backup_filename} ({backup_size:,} bytes)")
            
            return {
                "status": "success",
                "filename": backup_filename,
                "path": str(backup_path),
                "size_bytes": backup_size,
                "compressed": compressed,
                "created_at": datetime.now().isoformat()
            }
            
        except subprocess.TimeoutExpired:
            logger.error("❌ Backup timed out")
            return {"status": "failed", "error": "Backup timed out"}
        except Exception as e:
            logger.error(f"❌ Backup failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    def list_backups(self) -> list:
        """List all available backups"""
        try:
            backups = []
            
            for backup_file in self.backup_dir.glob("papa_backup_*"):
                if backup_file.is_file():
                    stat = backup_file.stat()
                    backups.append({
                        "filename": backup_file.name,
                        "path": str(backup_file),
                        "size_bytes": stat.st_size,
                        "created_at": datetime.fromtimestamp(stat.st_mtime),
                        "compressed": backup_file.suffix == ".gz"
                    })
            
            # Sort by creation time (newest first)
            backups.sort(key=lambda x: x["created_at"], reverse=True)
            return backups
            
        except Exception as e:
            logger.error(f"❌ Failed to list backups: {e}")
            return []
    
    def cleanup_old_backups(self, keep_days: int = 7) -> dict:
        """Clean up old backup files"""
        try:
            cutoff_date = datetime.now() - timedelta(days=keep_days)
            deleted_count = 0
            deleted_size = 0
            
            for backup_file in self.backup_dir.glob("papa_backup_*"):
                if backup_file.is_file():
                    file_time = datetime.fromtimestamp(backup_file.stat().st_mtime)
                    
                    if file_time < cutoff_date:
                        file_size = backup_file.stat().st_size
                        backup_file.unlink()
                        deleted_count += 1
                        deleted_size += file_size
                        logger.info(f"Deleted old backup: {backup_file.name}")
            
            logger.info(f"✅ Cleaned up {deleted_count} old backups ({deleted_size:,} bytes freed)")
            
            return {
                "status": "success",
                "deleted_count": deleted_count,
                "deleted_size_bytes": deleted_size
            }
            
        except Exception as e:
            logger.error(f"❌ Cleanup failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def restore_backup(self, backup_filename: str, confirm: bool = False) -> dict:
        """Restore database from backup"""
        try:
            if not confirm:
                raise ValueError("Restore requires explicit confirmation")
            
            backup_path = self.backup_dir / backup_filename
            
            if not backup_path.exists():
                raise FileNotFoundError(f"Backup file not found: {backup_filename}")
            
            logger.warning(f"⚠️  RESTORING DATABASE FROM: {backup_filename}")
            logger.warning("⚠️  THIS WILL OVERWRITE ALL CURRENT DATA!")
            
            # Handle compressed backups
            if backup_filename.endswith('.gz'):
                # Decompress to temporary file
                temp_path = self.backup_dir / f"temp_restore_{backup_filename[:-3]}"
                
                with gzip.open(backup_path, 'rb') as f_in:
                    with open(temp_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                
                restore_file = temp_path
            else:
                restore_file = backup_path
            
            # Create psql restore command
            db_url = settings.database_url
            cmd = [
                'psql',
                '--no-password',
                '--file', str(restore_file),
                db_url
            ]
            
            # Execute restore
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=1800  # 30 minutes timeout
            )
            
            # Clean up temporary file
            if backup_filename.endswith('.gz') and temp_path.exists():
                temp_path.unlink()
            
            if process.returncode != 0:
                raise RuntimeError(f"psql restore failed: {process.stderr}")
            
            logger.info(f"✅ Database restored from: {backup_filename}")
            
            return {
                "status": "success",
                "backup_filename": backup_filename,
                "restored_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Restore failed: {e}")
            return {"status": "failed", "error": str(e)}

async def interactive_menu():
    """Interactive backup menu"""
    backup = DatabaseBackup()
    
    while True:
        print("\n💾 Database Backup Menu")
        print("=" * 40)
        print("1. Create new backup")
        print("2. List available backups")
        print("3. Clean up old backups")
        print("4. Restore from backup")
        print("5. Set backup directory")
        print("0. Exit")
        
        choice = input("\nSelect option (0-5): ").strip()
        
        if choice == "0":
            break
        elif choice == "1":
            compressed = input("Compress backup? (Y/n): ").strip().lower() != 'n'
            result = await backup.create_backup(compressed)
            
            if result["status"] == "success":
                size_mb = result["size_bytes"] / 1024 / 1024
                print(f"✅ Backup created: {result['filename']} ({size_mb:.1f} MB)")
            else:
                print(f"❌ Backup failed: {result['error']}")
                
        elif choice == "2":
            backups = backup.list_backups()
            
            if not backups:
                print("ℹ️  No backups found")
            else:
                print(f"\n📦 Found {len(backups)} backups:")
                for i, b in enumerate(backups, 1):
                    size_mb = b["size_bytes"] / 1024 / 1024
                    compressed = " (compressed)" if b["compressed"] else ""
                    print(f"   {i}. {b['filename']} - {size_mb:.1f} MB{compressed}")
                    print(f"      Created: {b['created_at'].strftime('%Y-%m-%d %H:%M:%S')}")
                    
        elif choice == "3":
            days = input("Keep backups from last N days (default 7): ").strip()
            try:
                keep_days = int(days) if days else 7
                result = backup.cleanup_old_backups(keep_days)
                
                if result["status"] == "success":
                    freed_mb = result["deleted_size_bytes"] / 1024 / 1024
                    print(f"✅ Cleaned up {result['deleted_count']} backups ({freed_mb:.1f} MB freed)")
                else:
                    print(f"❌ Cleanup failed: {result['error']}")
            except ValueError:
                print("❌ Invalid number of days")
                
        elif choice == "4":
            backups = backup.list_backups()
            
            if not backups:
                print("❌ No backups available for restore")
                continue
            
            print("\n📦 Available backups:")
            for i, b in enumerate(backups, 1):
                size_mb = b["size_bytes"] / 1024 / 1024
                print(f"   {i}. {b['filename']} - {size_mb:.1f} MB")
                print(f"      Created: {b['created_at'].strftime('%Y-%m-%d %H:%M:%S')}")
            
            try:
                selection = int(input("\nSelect backup number: ").strip()) - 1
                if 0 <= selection < len(backups):
                    selected_backup = backups[selection]
                    
                    print(f"\n⚠️  WARNING: This will OVERWRITE all current data!")
                    print(f"   Restoring from: {selected_backup['filename']}")
                    confirm = input("Type 'CONFIRM' to proceed: ").strip()
                    
                    if confirm == "CONFIRM":
                        result = await backup.restore_backup(selected_backup['filename'], True)
                        
                        if result["status"] == "success":
                            print(f"✅ Database restored from: {selected_backup['filename']}")
                        else:
                            print(f"❌ Restore failed: {result['error']}")
                    else:
                        print("❌ Restore cancelled")
                else:
                    print("❌ Invalid selection")
            except ValueError:
                print("❌ Invalid backup number")
                
        elif choice == "5":
            current_dir = str(backup.backup_dir)
            print(f"Current backup directory: {current_dir}")
            new_dir = input("Enter new backup directory (or press Enter to keep current): ").strip()
            
            if new_dir:
                try:
                    backup = DatabaseBackup(new_dir)
                    print(f"✅ Backup directory set to: {backup.backup_dir}")
                except Exception as e:
                    print(f"❌ Failed to set directory: {e}")
        else:
            print("❌ Invalid option. Please try again.")

async def main():
    """Main backup function"""
    print("💾 PAPA Database Backup")
    print("=" * 40)
    
    # Check if backup tools are available
    try:
        subprocess.run(['pg_dump', '--version'], capture_output=True, check=True)
        subprocess.run(['psql', '--version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ PostgreSQL tools (pg_dump, psql) are not available!")
        print("   Please install PostgreSQL client tools.")
        return 1
    
    # Start interactive menu
    await interactive_menu()
    
    print("\n👋 Backup operations completed!")
    return 0

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⏹️  Backup interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Unexpected error: {str(e)}")
        sys.exit(1)
