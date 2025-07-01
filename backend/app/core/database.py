from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import create_engine
from typing import AsyncGenerator
from app.core.config import settings

# For testing with SQLite, we'll use a synchronous engine
if settings.SQLALCHEMY_DATABASE_URI.startswith("sqlite"):
    # Use sync engine for SQLite testing
    from sqlalchemy.orm import sessionmaker
    sync_engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, echo=False)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)
    
    # Mock async engine for testing
    engine = sync_engine
    
    def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
            
else:
    # Create async engine for production
    engine = create_async_engine(
        settings.database_url, 
        pool_pre_ping=True, 
        echo=False  # Set echo=True for SQL logging
    )

if not settings.SQLALCHEMY_DATABASE_URI.startswith("sqlite"):
    # Create async session maker for production
    AsyncSessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    # Dependency to get async DB session
    async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
        async with AsyncSessionLocal() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
