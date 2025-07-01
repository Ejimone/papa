# Database Documentation

## Overview

This document covers the complete database setup, configuration, and implementation for the AI-Powered Past Questions App backend. The application uses PostgreSQL as the primary database with async SQLAlchemy for ORM operations.

## Table of Contents

1. [Database Architecture](#database-architecture)
2. [Database Configuration](#database-configuration)
3. [Models Implementation](#models-implementation)
4. [Migration Setup](#migration-setup)
5. [Repository Pattern](#repository-pattern)
6. [Authentication Implementation](#authentication-implementation)
7. [Database Schema](#database-schema)
8. [Troubleshooting](#troubleshooting)

---

## Database Architecture

### Technology Stack

- **Database**: PostgreSQL 15+
- **ORM**: SQLAlchemy 2.0+ with AsyncIO support
- **Async Driver**: asyncpg
- **Migration Tool**: Alembic
- **Connection Management**: Async session management with automatic rollback/commit

### Database Configuration Files

```
backend/
├── app/
│   ├── core/
│   │   ├── config.py          # Database configuration settings
│   │   └── database.py        # Database connection and session management
│   └── models/
│       ├── base.py           # Base model class
│       └── user.py           # User model implementation
├── alembic/
│   ├── alembic.ini          # Alembic configuration
│   ├── env.py               # Alembic environment setup
│   └── versions/            # Migration files
└── .env                     # Environment variables
```

---

## Database Configuration

### Environment Variables (`.env`)

```env
# Database Configuration
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=
POSTGRES_DB=papa_db

# Application Settings
SECRET_KEY=your-secret-key-here
FIRST_SUPERUSER_EMAIL=admin@papa.com
FIRST_SUPERUSER_PASSWORD=admin123
```

### Core Configuration (`app/core/config.py`)

```python
class Settings(BaseSettings):
    # Database settings
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "papa_db")
    SQLALCHEMY_DATABASE_URI: Optional[str] = None

# Construct async SQLAlchemy Database URI
settings.SQLALCHEMY_DATABASE_URI = f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}/{settings.POSTGRES_DB}"
```

### Database Connection (`app/core/database.py`)

```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from typing import AsyncGenerator

# Create async engine
engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True,
    echo=False  # Set echo=True for SQL logging
)

# Create async session maker
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Dependency to get async DB session
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

**Key Implementation Details:**

- Uses async SQLAlchemy with `asyncpg` driver
- Automatic session management with commit/rollback
- Connection pooling with `pool_pre_ping=True`
- Generator-based dependency injection for FastAPI

---

## Models Implementation

### Base Model (`app/models/base.py`)

```python
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class TimestampMixin:
    """Mixin for adding timestamp fields to models."""
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
```

### User Model (`app/models/user.py`)

```python
from sqlalchemy import Column, String, Boolean
from app.models.base import Base

class User(Base):
    __tablename__ = "users"

    # id, created_at, updated_at inherited from Base
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', username='{self.username}')>"
```

**Key Features:**

- Inherits timestamp fields from Base
- Email-based authentication with optional username
- Boolean flags for user status and permissions
- Proper indexing on frequently queried fields

---

## Migration Setup

### Alembic Configuration (`alembic/alembic.ini`)

```ini
[alembic]
script_location = alembic
prepend_sys_path = .
version_path_separator = os
sqlalchemy.url =
```

### Alembic Environment (`alembic/env.py`)

```python
import sys
import os
from sqlalchemy import engine_from_config, pool
from alembic import context

# Add the app directory to Python path
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.config import settings
from app.models.base import Base
from app.models.user import User  # Import all models for autogenerate

# Set the sqlalchemy.url from application settings
sync_db_url = settings.SQLALCHEMY_DATABASE_URI.replace("+asyncpg", "")
config.set_main_option("sqlalchemy.url", sync_db_url.replace('%', '%%'))

target_metadata = Base.metadata
```

**Key Configuration:**

- Automatic model discovery for migrations
- Dynamic database URL from application settings
- Sync driver for migration operations (converts asyncpg to psycopg2)

### Migration Commands

```bash
# Create a new migration
alembic -c alembic/alembic.ini revision --autogenerate -m "description"

# Apply migrations
alembic -c alembic/alembic.ini upgrade head

# Check current migration status
alembic -c alembic/alembic.ini current

# Show migration history
alembic -c alembic/alembic.ini history
```

---

## Repository Pattern

### Base Repository (`app/repositories/base.py`)

```python
from typing import TypeVar, Generic, Type, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(self, db: AsyncSession, id: int) -> Optional[ModelType]:
        result = await db.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()

    async def get_by_attribute(self, db: AsyncSession, *, attribute: str, value: str) -> Optional[ModelType]:
        attr = getattr(self.model, attribute)
        statement = select(self.model).where(attr == value)
        result = await db.execute(statement)
        return result.scalar_one_or_none()
```

### User Repository (`app/repositories/user_repository.py`)

```python
from app.repositories.base import BaseRepository
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    async def get_by_email(self, db: AsyncSession, *, email: str) -> Optional[User]:
        return await self.get_by_attribute(db, attribute="email", value=email)

    async def get_by_username(self, db: AsyncSession, *, username: str) -> Optional[User]:
        return await self.get_by_attribute(db, attribute="username", value=username)

    async def is_active(self, user: User) -> bool:
        return user.is_active

    async def is_superuser(self, user: User) -> bool:
        return user.is_superuser

# Initialize repository instance
user_repo = UserRepository(User)
```

**Repository Pattern Benefits:**

- Separation of data access logic
- Reusable CRUD operations
- Type safety with generics
- Easy testing with dependency injection

---

## Authentication Implementation

### Password Security (`app/core/security.py`)

```python
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(subject: Union[str, int]) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": str(subject)}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
```

### Authentication Service (`app/services/auth_service.py`)

```python
class AuthService:
    async def register_user(self, db: AsyncSession, *, user_in: UserCreate) -> User:
        # Check for existing users
        existing_user_email = await user_repo.get_by_email(db, email=user_in.email)
        if existing_user_email:
            raise HTTPException(status_code=400, detail="User with this email already exists")

        # Hash password and create user
        hashed_password = get_password_hash(user_in.password)
        user_data = user_in.model_dump(exclude={"password"})
        user_data["hashed_password"] = hashed_password

        # Create user in database
        db_user = User(**user_data)
        db.add(db_user)
        await db.flush()
        await db.refresh(db_user)
        return db_user

    async def login_user(self, db: AsyncSession, *, login_data: LoginRequest) -> Token:
        user = await user_repo.get_by_email(db, email=login_data.email)
        if not user or not verify_password(login_data.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Incorrect email or password")

        access_token = create_access_token(subject=user.id)
        refresh_token = create_refresh_token(subject=user.id)
        return Token(access_token=access_token, refresh_token=refresh_token)
```

---

## Database Schema

### Current Tables

#### Users Table

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    username VARCHAR UNIQUE,
    hashed_password VARCHAR NOT NULL,
    is_active BOOLEAN DEFAULT true,
    is_superuser BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX ix_users_email ON users(email);
CREATE INDEX ix_users_username ON users(username);
CREATE INDEX ix_users_id ON users(id);
```

### Admin User Setup

A script `create_admin.py` is provided to create the initial admin user:

```python
async def create_admin_user():
    admin_user = User(
        email=settings.FIRST_SUPERUSER_EMAIL,
        username="admin",
        hashed_password=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
        is_active=True,
        is_superuser=True
    )
    # ... save to database
```

**Admin Credentials:**

- Email: `admin@papa.com`
- Password: `admin123`
- Username: `admin`
- Superuser: `True`

---

## Troubleshooting

### Common Issues and Solutions

#### 1. "relation 'users' does not exist" Error

**Problem**: Database tables haven't been created.

**Solution**:

```bash
# Run migrations to create tables
alembic -c alembic/alembic.ini upgrade head
```

#### 2. Async/Sync Database Configuration Mismatch

**Problem**: Using sync SQLAlchemy with async repositories.

**Solution**: Ensure database URI uses `postgresql+asyncpg://` and all database operations are async:

```python
# Correct async configuration
settings.SQLALCHEMY_DATABASE_URI = f"postgresql+asyncpg://{user}:{password}@{host}/{db}"
```

#### 3. OAuth2 Authentication Issues in Swagger UI

**Problem**: 422 Unprocessable Content when using Swagger UI authentication.

**Solution**: Use separate endpoints for different authentication methods:

- `/api/v1/auth/token` - OAuth2 form data (Swagger UI)
- `/api/v1/auth/login` - JSON data (programmatic access)

#### 4. Migration Import Errors

**Problem**: Alembic can't import models for autogenerate.

**Solution**: Ensure all models are imported in `alembic/env.py`:

```python
from app.models.user import User
from app.models.question import Question  # Add as models are created
```

### Database Connection Testing

Test database connectivity:

```python
# Test script
import asyncio
from app.core.database import AsyncSessionLocal

async def test_connection():
    async with AsyncSessionLocal() as session:
        result = await session.execute("SELECT 1")
        print("Database connection successful:", result.scalar())

asyncio.run(test_connection())
```

### Performance Considerations

1. **Connection Pooling**: Configured with `pool_pre_ping=True` for connection health checks
2. **Indexing**: Proper indexes on frequently queried columns (email, username, id)
3. **Session Management**: Automatic cleanup with async context managers
4. **Query Optimization**: Use `select()` for explicit query construction

---

## Future Enhancements

### Planned Database Additions

1. **Question Models**: For storing past questions and metadata
2. **Subject Models**: For categorizing questions by academic subjects
3. **Practice Session Models**: For tracking user practice sessions
4. **Analytics Models**: For storing user performance data
5. **Vector Database Integration**: Chroma for semantic search capabilities

### Security Enhancements

1. **Row-Level Security**: PostgreSQL RLS for multi-tenant data isolation
2. **Audit Logging**: Track database changes for security and compliance
3. **Connection Encryption**: SSL/TLS for database connections in production
4. **Backup Strategy**: Automated backups with point-in-time recovery

---

## Development Workflow

### Setting Up Development Database

1. **Install PostgreSQL** (if not already installed)
2. **Create database**: `createdb papa_db`
3. **Configure environment**: Copy `.env.example` to `.env` and update settings
4. **Run migrations**: `alembic -c alembic/alembic.ini upgrade head`
5. **Create admin user**: `python create_admin.py`
6. **Start application**: `uvicorn app.main:app --reload`

### Making Database Changes

1. **Modify models** in `app/models/`
2. **Generate migration**: `alembic -c alembic/alembic.ini revision --autogenerate -m "description"`
3. **Review migration** in `alembic/versions/`
4. **Apply migration**: `alembic -c alembic/alembic.ini upgrade head`
5. **Test changes** with application

This documentation provides a comprehensive overview of the database implementation and serves as a reference for development and maintenance activities.
