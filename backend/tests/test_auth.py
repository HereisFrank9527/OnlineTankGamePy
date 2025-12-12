import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_duplicate_username_fails(client: AsyncClient):
    payload_1 = {
        "username": "testuser",
        "email": "test1@example.com",
        "password": "password123",
    }
    payload_2 = {
        "username": "testuser",
        "email": "test2@example.com",
        "password": "password123",
    }

    r1 = await client.post("/api/v1/auth/register", json=payload_1)
    assert r1.status_code == 201

    r2 = await client.post("/api/v1/auth/register", json=payload_2)
    assert r2.status_code == 409


@pytest.mark.asyncio
async def test_login_requires_valid_credentials_and_me_works(client: AsyncClient):
    payload = {
        "username": "testuser2",
        "email": "testuser2@example.com",
        "password": "password123",
    }
    r = await client.post("/api/v1/auth/register", json=payload)
    assert r.status_code == 201

    bad_login = await client.post(
        "/api/v1/auth/login",
        json={"username": "testuser2", "password": "wrongpassword"},
    )
    assert bad_login.status_code == 401

    login = await client.post(
        "/api/v1/auth/login",
        json={"username": "testuser2", "password": "password123"},
    )
    assert login.status_code == 200
    data = login.json()
    assert data["access_token"]
    assert data["refresh_token"]
    assert data["token_type"] == "bearer"

    unauth_me = await client.get("/api/v1/auth/me")
    assert unauth_me.status_code == 401

    me = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {data['access_token']}"},
    )
    assert me.status_code == 200
    me_data = me.json()
    assert me_data["username"] == "testuser2"
    assert me_data["login_count"] == 1
    assert me_data["last_login_at"] is not None
