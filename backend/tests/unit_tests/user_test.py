from uuid import UUID

import pytest


@pytest.mark.asyncio
async def test_register_user(client):
    """
    Test successful user registration.
    """
    response = await client.post("/register", json={"username": "testuser", "password": "Mubeen2@@2"})
    assert response.status_code == 200
    user = response.json()
    assert user["username"] == "testuser"
    assert "user_id" in user
    assert isinstance(UUID(user["user_id"]), UUID)
    assert "hashed_password" not in user


@pytest.mark.asyncio
async def test_register_user_duplicate_username(client):
    """
    Test user registration with a duplicate username.
    """
    # First registration
    await client.post("/register", json={"username": "duplicateuser", "password": "Mubeen2@@2"})

    # Attempt duplicate registration
    response = await client.post("/register", json={"username": "duplicateuser", "password": "Mubeen2@@2"})
    assert response.status_code == 500
    error_response = response.json()
    assert "detail" in error_response
    assert error_response["detail"]["detail"] == "User already exists"
    assert error_response["detail"]["status_code"] == 500


@pytest.mark.asyncio
async def test_register_user_invalid_username(client):
    """
    Test user registration with an invalid username.
    """
    response = await client.post("/register", json={"username": "", "password": "Mubeen2@@2"})
    assert response.status_code == 422
    error_response = response.json()
    assert "detail" in error_response


@pytest.mark.asyncio
async def test_register_user_weak_password(client):
    """
    Test user registration with a weak password.
    """
    response = await client.post("/register", json={"username": "weakpassworduser", "password": "123"})
    assert response.status_code == 422
    error_response = response.json()
    assert "detail" in error_response


@pytest.mark.asyncio
async def test_login_success(client):
    """
    Test successful login.
    """
    # First, register a user
    register_response = await client.post("/register", json={"username": "loginuser", "password": "Mubeenaftab2@@2"})
    assert register_response.status_code == 200, f"User registration failed: {register_response.json()}"

    # Now, attempt to login
    login_response = await client.post(
        "/login",
        data={"username": "loginuser", "password": "Mubeenaftab2@@2"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert login_response.status_code == 200, f"Login failed: {login_response.json()}"
    data = login_response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_credentials(client):
    """
    Test login with invalid credentials.
    """
    response = await client.post(
        "/login",
        data={"username": "nonexistentuser", "password": "Mubeen2@@2"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 401, f"Expected 401, got {response.status_code}. Response: {response.text}"

    error_response = response.json()
    assert "detail" in error_response, f"Expected 'detail' in response, got: {error_response}"
    assert (
        error_response["detail"]["detail"] == "Credentials are invalid"
    ), f"Expected 'Invalid credentials', got: {error_response['detail']['detail']}"
    assert (
        error_response["detail"]["status_code"] == 401
    ), f"Expected status code 401, got: {error_response['detail']['status_code']}"


@pytest.mark.asyncio
async def test_login_missing_fields(client):
    """
    Test login with missing fields (e.g., missing password).
    """
    response = await client.post(
        "/login",
        data={"username": "someuser"},  # Missing password field
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 422  # Unprocessable Entity
    error_response = response.json()
    assert "detail" in error_response


@pytest.mark.asyncio
async def test_login_missing_username(client):
    """
    Test login with missing username.
    """
    response = await client.post(
        "/login",
        data={"password": "somepassword"},  # Missing username field
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 422  # Unprocessable Entity
    error_response = response.json()
    assert "detail" in error_response


@pytest.mark.asyncio
async def test_register_missing_password(client):
    """
    Test user registration with missing password.
    """
    response = await client.post(
        "/register",
        json={"username": "testusermissingpassword"},  # Missing password
    )
    assert response.status_code == 422
    error_response = response.json()
    assert "detail" in error_response
