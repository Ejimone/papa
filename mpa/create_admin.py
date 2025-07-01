#!/usr/bin/env python3
"""
Script to create an admin user for testing purposes.
"""
import asyncio
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent))

from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.core.security import get_password_hash
from app.core.config import settings


async def create_admin_user():
    """Create an admin user if it doesn't exist."""
    async with AsyncSessionLocal() as session:
        try:
            # Check if admin user already exists
            from sqlalchemy import select
            stmt = select(User).where(User.email == settings.FIRST_SUPERUSER_EMAIL)
            result = await session.execute(stmt)
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                print(f"Admin user with email {settings.FIRST_SUPERUSER_EMAIL} already exists.")
                print(f"ID: {existing_user.id}")
                print(f"Username: {existing_user.username}")
                print(f"Is Superuser: {existing_user.is_superuser}")
                return existing_user
            
            # Create admin user
            admin_user = User(
                email=settings.FIRST_SUPERUSER_EMAIL,
                username="admin",
                hashed_password=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
                is_active=True,
                is_superuser=True
            )
            
            session.add(admin_user)
            await session.commit()
            await session.refresh(admin_user)
            
            print(f"✅ Admin user created successfully!")
            print(f"Email: {admin_user.email}")
            print(f"Username: {admin_user.username}")
            print(f"Password: {settings.FIRST_SUPERUSER_PASSWORD}")
            print(f"Is Superuser: {admin_user.is_superuser}")
            
            return admin_user
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Error creating admin user: {e}")
            raise


async def main():
    """Main function."""
    print("Creating admin user...")
    await create_admin_user()


if __name__ == "__main__":
    asyncio.run(main())
