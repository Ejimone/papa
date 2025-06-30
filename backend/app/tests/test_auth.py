import pytest
from httpx import AsyncClient
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.schemas.user import UserCreate
from app.models.user import User # For type checking
from app.repositories.user_repository import user_repo # To verify user creation in DB

# Mark all tests in this module as asyncio
pytestmark = pytest.mark.asyncio


async def test_user_registration(
    test_client: AsyncClient,
    db_session: AsyncSession, # For DB verification
    test_user_data: dict
):
    """
    Test user registration endpoint.
    """
    response = await test_client.post(
        f"{settings.API_V1_STR}/auth/register",
        json=test_user_data,
    )
    assert response.status_code == status.HTTP_201_CREATED
    created_user_data = response.json()
    assert created_user_data["email"] == test_user_data["email"]
    assert created_user_data["username"] == test_user_data["username"]
    assert "id" in created_user_data
    assert "hashed_password" not in created_user_data # Ensure password is not returned

    # Verify user in database
    db_user = await user_repo.get_by_email(db_session, email=test_user_data["email"])
    assert db_user is not None
    assert db_user.email == test_user_data["email"]
    assert db_user.username == test_user_data["username"]


async def test_user_registration_duplicate_email(
    test_client: AsyncClient,
    created_test_user: User, # Uses fixture that creates a user
    test_user_data: dict
):
    """
    Test registration with an email that already exists.
    """
    # created_test_user fixture already created a user with test_user_data["email"]
    # Try to register again with the same email but different username
    duplicate_email_data = {
        "email": test_user_data["email"], # Same email
        "username": "anotherusername",
        "password": "anotherpassword123"
    }
    response = await test_client.post(
        f"{settings.API_V1_STR}/auth/register",
        json=duplicate_email_data,
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    error_data = response.json()
    assert "email already exists" in error_data["detail"].lower()


async def test_user_registration_duplicate_username(
    test_client: AsyncClient,
    created_test_user: User, # Uses fixture that creates a user
    test_user_data: dict
):
    """
    Test registration with a username that already exists.
    """
    # created_test_user fixture already created a user with test_user_data["username"]
    # Try to register again with the same username but different email
    duplicate_username_data = {
        "email": "anotheremail@example.com",
        "username": test_user_data["username"], # Same username
        "password": "anotherpassword123"
    }
    response = await test_client.post(
        f"{settings.API_V1_STR}/auth/register",
        json=duplicate_username_data,
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    error_data = response.json()
    assert "username already exists" in error_data["detail"].lower()


async def test_user_login(
    test_client: AsyncClient,
    created_test_user: User, # Ensures user exists and is created with known pass
    test_user_data: dict # For login credentials
):
    """
    Test user login and token generation.
    """
    login_payload = {
        "email": test_user_data["email"],
        "password": test_user_data["password"],
    }
    response = await test_client.post(
        f"{settings.API_V1_STR}/auth/login",
        # FastAPI's OAuth2PasswordRequestForm expects form data, not JSON
        # For testing, we can send JSON if the endpoint auth_service.login_user
        # and schema LoginRequest are set up for it.
        # If endpoint expects form data (e.g. using Body() with specific media type or OAuth2PasswordRequestForm = Depends()),
        # then client.post should use `data=login_payload` instead of `json=login_payload`.
        # My current auth.py endpoint uses LoginRequest (Pydantic model), so JSON is fine.
        json=login_payload
    )
    assert response.status_code == status.HTTP_200_OK
    token_data = response.json()
    assert "access_token" in token_data
    assert "refresh_token" in token_data
    assert token_data["token_type"] == "bearer"


async def test_user_login_incorrect_password(
    test_client: AsyncClient,
    created_test_user: User, # Ensures user exists
    test_user_data: dict
):
    """
    Test login with an incorrect password.
    """
    login_payload = {
        "email": test_user_data["email"],
        "password": "wrongpassword",
    }
    response = await test_client.post(
        f"{settings.API_V1_STR}/auth/login",
        json=login_payload,
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    error_data = response.json()
    assert "incorrect email or password" in error_data["detail"].lower()


async def test_user_login_nonexistent_user(test_client: AsyncClient):
    """
    Test login for a user that does not exist.
    """
    login_payload = {
        "email": "nonexistentuser@example.com",
        "password": "anypassword",
    }
    response = await test_client.post(
        f"{settings.API_V1_STR}/auth/login",
        json=login_payload,
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED # Or 404, depending on desired behavior
    error_data = response.json()
    assert "incorrect email or password" in error_data["detail"].lower() # Generic message for security


async def test_get_current_user_me(authenticated_client: AsyncClient, created_test_user: User):
    """
    Test the /users/me endpoint to get current user details.
    """
    response = await authenticated_client.get(f"{settings.API_V1_STR}/users/me")
    assert response.status_code == status.HTTP_200_OK
    user_data = response.json()
    assert user_data["email"] == created_test_user.email
    assert user_data["username"] == created_test_user.username
    assert user_data["id"] == created_test_user.id
    assert "hashed_password" not in user_data


async def test_get_current_user_me_unauthenticated(test_client: AsyncClient):
    """
    Test accessing /users/me without authentication.
    """
    response = await test_client.get(f"{settings.API_V1_STR}/users/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    error_data = response.json()
    assert error_data["detail"] == "Not authenticated" # Default from OAuth2PasswordBearer if no token


# TODO: Add tests for token refresh
# TODO: Add tests for inactive user login
# TODO: Add tests for superuser creation via FIRST_SUPERUSER_EMAIL (if logic is in register)
# (This might require more control over when the superuser is created or checking DB state)

async def test_first_superuser_creation_on_registration(
    test_client: AsyncClient,
    db_session: AsyncSession,
    test_superuser_data: dict
):
    """
    Test if the first user matching FIRST_SUPERUSER_EMAIL becomes a superuser.
    This depends on the logic in AuthService.register_user.
    """
    # Ensure no other user (especially superuser) exists yet for a clean test
    # This test is a bit tricky if other tests create users.
    # Ideally, run this in an isolated DB state or ensure FIRST_SUPERUSER_EMAIL is unique for this test.

    # For this test to be reliable, we'd need to ensure the user table is empty
    # or that no user with settings.FIRST_SUPERUSER_EMAIL exists.
    # The current db_session fixture with rollback helps, but order matters if other tests create this user.
    # A more robust way: delete the user if exists before this test, or use a unique email for this test.

    # Assuming settings.FIRST_SUPERUSER_EMAIL is unique for this test run or the DB is clean for it.
    existing_superuser = await user_repo.get_by_email(db_session, email=settings.FIRST_SUPERUSER_EMAIL)
    if existing_superuser:
        # This can happen if another test (e.g. superuser_authenticated_client fixture) already created it.
        # For simplicity, we'll just assert its state if it exists.
        # A better approach might be to ensure a truly clean state or use a unique superuser email for testing this feature.
        assert existing_superuser.is_superuser is True
        pytest.skip("Superuser already exists, skipping direct registration test for superuser creation.")
        return

    response = await test_client.post(
        f"{settings.API_V1_STR}/auth/register",
        json=test_superuser_data, # Uses FIRST_SUPERUSER_EMAIL from settings
    )
    assert response.status_code == status.HTTP_201_CREATED
    created_user_data = response.json()
    assert created_user_data["email"] == test_superuser_data["email"]

    # Verify user in database
    db_user = await user_repo.get_by_email(db_session, email=test_superuser_data["email"])
    assert db_user is not None
    assert db_user.is_superuser is True


# Test for /users/ (admin endpoint)
async def test_read_users_as_superuser(superuser_authenticated_client: AsyncClient, created_test_user: User, created_test_superuser: User):
    response = await superuser_authenticated_client.get(f"{settings.API_V1_STR}/users/")
    assert response.status_code == status.HTTP_200_OK
    users = response.json()
    assert len(users) >= 2 # At least the created_test_user and created_test_superuser
    user_emails = [user["email"] for user in users]
    assert created_test_user.email in user_emails
    assert created_test_superuser.email in user_emails

async def test_read_users_as_normal_user(authenticated_client: AsyncClient):
    response = await authenticated_client.get(f"{settings.API_V1_STR}/users/")
    assert response.status_code == status.HTTP_403_FORBIDDEN

async def test_read_users_unauthenticated(test_client: AsyncClient):
    response = await test_client.get(f"{settings.API_V1_STR}/users/")
    # This will first hit 401 Not Authenticated by reusable_oauth2, then 403 by get_current_active_superuser if token was somehow passed
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
