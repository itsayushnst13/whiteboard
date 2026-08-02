from httpx import AsyncClient


async def test_register_creates_account_and_returns_token(db_client: AsyncClient) -> None:
    response = await db_client.post(
        "/auth/register",
        json={"email": "ada@example.com", "password": "supersecret", "display_name": "Ada"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["access_token"]
    assert body["data"]["user"]["email"] == "ada@example.com"
    assert body["data"]["user"]["display_name"] == "Ada"


async def test_register_rejects_duplicate_email(db_client: AsyncClient) -> None:
    payload = {"email": "dupe@example.com", "password": "supersecret", "display_name": "Dupe"}
    await db_client.post("/auth/register", json=payload)

    response = await db_client.post("/auth/register", json=payload)

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "CONFLICT"


async def test_register_rejects_short_password(db_client: AsyncClient) -> None:
    response = await db_client.post(
        "/auth/register",
        json={"email": "short@example.com", "password": "short", "display_name": "Short"},
    )

    assert response.status_code == 422


async def test_login_succeeds_with_correct_credentials(db_client: AsyncClient) -> None:
    await db_client.post(
        "/auth/register",
        json={"email": "grace@example.com", "password": "supersecret", "display_name": "Grace"},
    )

    response = await db_client.post(
        "/auth/login", json={"email": "grace@example.com", "password": "supersecret"}
    )

    assert response.status_code == 200
    assert response.json()["data"]["access_token"]


async def test_login_rejects_wrong_password(db_client: AsyncClient) -> None:
    await db_client.post(
        "/auth/register",
        json={"email": "hedy@example.com", "password": "supersecret", "display_name": "Hedy"},
    )

    response = await db_client.post(
        "/auth/login", json={"email": "hedy@example.com", "password": "wrongpassword"}
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


async def test_login_rejects_unknown_email(db_client: AsyncClient) -> None:
    response = await db_client.post(
        "/auth/login", json={"email": "nobody@example.com", "password": "supersecret"}
    )

    assert response.status_code == 401


async def test_me_requires_authentication(db_client: AsyncClient) -> None:
    response = await db_client.get("/auth/me")

    assert response.status_code == 401


async def test_me_returns_current_user_with_valid_token(db_client: AsyncClient) -> None:
    register = await db_client.post(
        "/auth/register",
        json={"email": "linus@example.com", "password": "supersecret", "display_name": "Linus"},
    )
    token = register.json()["data"]["access_token"]

    response = await db_client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json()["data"]["email"] == "linus@example.com"


async def test_me_rejects_garbage_token(db_client: AsyncClient) -> None:
    response = await db_client.get("/auth/me", headers={"Authorization": "Bearer not-a-real-token"})

    assert response.status_code == 401
