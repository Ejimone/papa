import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator, Generator, Any

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.main import app # Main FastAPI application
from app.core.config import settings
from app.core.database import Base, get_db # Base for creating tables, get_db to override
from app.models.user import User # For creating test user
from app.schemas.user import UserCreate # For creating test user
from app.core.security import create_access_token, get_password_hash # For test user and auth

# Use a separate test database if possible, or ensure transactions isolate tests.
# For simplicity, this uses the same DB defined in settings but with NullPool and rollbacks.
# It's better to use a dedicated test DB by modifying settings.SQLALCHEMY_DATABASE_URI for tests.
# For example, by setting an environment variable like `TESTING=True`

TEST_SQLALCHEMY_DATABASE_URI = settings.SQLALCHEMY_DATABASE_URI + "_test" if settings.SQLALCHEMY_DATABASE_URI else "sqlite+aiosqlite:///./test.db"


# Create a new engine instance for testing
test_engine = create_async_engine(TEST_SQLALCHEMY_DATABASE_URI, poolclass=NullPool)

# Create a new sessionmaker instance for testing
TestingSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, bind=test_engine, class_=AsyncSession, expire_on_commit=False
)

# Override the get_db dependency for testing
async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        try:
            yield session
            # For testing, we usually want to rollback changes after each test
            await session.rollback()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture(scope="session")
async def _db_setup_session_scoped() -> AsyncGenerator[None, None]:
    """
    Session-scoped fixture to create and drop tables once per test session.
    """
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()


@pytest_asyncio.fixture(scope="function") # Changed from session to function for db isolation
async def db_session( _db_setup_session_scoped: None) -> AsyncGenerator[AsyncSession, None]:
    """
    Provides a transactional database session for tests.
    Rolls back after each test.
    """
    # _db_setup_session_scoped ensures tables are created before any test runs
    # and dropped after all tests complete.
    # This fixture provides a session that will be rolled back.
    async with TestingSessionLocal() as session:
        try:
            yield session
            await session.rollback() # Ensure rollback even if test doesn't fail
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@pytest_asyncio.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for each test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Provides an Httpx AsyncClient for making requests to the FastAPI app.
    The `db_session` fixture ensures that the override_get_db uses a session
    that's part of the test's transaction.
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Ensure get_db override is active for this client's lifespan if needed,
        # but it's globally overridden for the app instance.
        yield client


# --- Test User Fixtures ---

@pytest_asyncio.fixture(scope="function")
async def test_user_data() -> dict[str, Any]:
    return {
        "email": "testuser@example.com",
        "username": "testusername",
        "password": "testpassword123"
    }

@pytest_asyncio.fixture(scope="function")
async def test_superuser_data() -> dict[str, Any]:
    return {
        "email": settings.FIRST_SUPERUSER_EMAIL, # Use email defined for superuser
        "username": "testsuperuser",
        "password": settings.FIRST_SUPERUSER_PASSWORD # Use password for superuser
    }


@pytest_asyncio.fixture(scope="function")
async def created_test_user(db_session: AsyncSession, test_user_data: dict[str, Any]) -> User:
    """
    Creates a standard test user directly in the database.
    """
    user_in = UserCreate(**test_user_data)
    hashed_password = get_password_hash(user_in.password)
    db_user = User(
        email=user_in.email,
        username=user_in.username,
        hashed_password=hashed_password,
        is_active=True,
        is_superuser=False
    )
    db_session.add(db_user)
    await db_session.commit()
    await db_session.refresh(db_user)
    return db_user

@pytest_asyncio.fixture(scope="function")
async def created_test_superuser(db_session: AsyncSession, test_superuser_data: dict[str, Any]) -> User:
    """
    Creates a superuser directly in the database.
    """
    user_in = UserCreate(**test_superuser_data)
    hashed_password = get_password_hash(user_in.password)
    db_user = User(
        email=user_in.email,
        username=user_in.username,
        hashed_password=hashed_password,
        is_active=True,
        is_superuser=True # Explicitly set as superuser
    )
    db_session.add(db_user)
    await db_session.commit()
    await db_session.refresh(db_user)
    return db_user


@pytest_asyncio.fixture(scope="function")
async def authenticated_client(test_client: AsyncClient, created_test_user: User) -> AsyncClient:
    """
    Returns an AsyncClient authenticated as the standard test user.
    """
    access_token = create_access_token(subject=created_test_user.id)
    test_client.headers["Authorization"] = f"Bearer {access_token}"
    return test_client


@pytest_asyncio.fixture(scope="function")
async def superuser_authenticated_client(test_client: AsyncClient, created_test_superuser: User) -> AsyncClient:
    """
    Returns an AsyncClient authenticated as the test superuser.
    """
    access_token = create_access_token(subject=created_test_superuser.id)
    test_client.headers["Authorization"] = f"Bearer {access_token}"
    return test_client


# Fixture to provide UserCreate schema for tests needing to post user data
@pytest.fixture(scope="function")
def user_create_schema(test_user_data: dict[str, Any]) -> UserCreate:
    return UserCreate(**test_user_data)

# If you need to modify settings for tests, you can use a fixture like this:
# @pytest.fixture(scope="session", autouse=True)
# def test_settings():
#     original_db_uri = settings.SQLALCHEMY_DATABASE_URI
#     settings.SQLALCHEMY_DATABASE_URI = "sqlite+aiosqlite:///./test_override.db" # Or your test DB URI
#     yield
#     settings.SQLALCHEMY_DATABASE_URI = original_db_uri
