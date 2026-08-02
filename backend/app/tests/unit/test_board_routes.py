from httpx import AsyncClient


async def _register_and_get_token(client: AsyncClient, email: str = "owner@example.com") -> str:
    response = await client.post(
        "/auth/register",
        json={"email": email, "password": "supersecret", "display_name": "Owner"},
    )
    return str(response.json()["data"]["access_token"])


async def test_list_boards_requires_authentication(db_client: AsyncClient) -> None:
    response = await db_client.get("/boards")

    assert response.status_code == 401


async def test_create_and_list_boards(db_client: AsyncClient) -> None:
    token = await _register_and_get_token(db_client)
    headers = {"Authorization": f"Bearer {token}"}

    create_response = await db_client.post(
        "/boards", json={"name": "Sprint planning"}, headers=headers
    )
    assert create_response.status_code == 201
    created = create_response.json()["data"]
    assert created["name"] == "Sprint planning"
    assert created["room_id"]

    list_response = await db_client.get("/boards", headers=headers)
    assert list_response.status_code == 200
    boards = list_response.json()["data"]
    assert len(boards) == 1
    assert boards[0]["room_id"] == created["room_id"]


async def test_create_board_defaults_name_when_omitted(db_client: AsyncClient) -> None:
    token = await _register_and_get_token(db_client)
    headers = {"Authorization": f"Bearer {token}"}

    response = await db_client.post("/boards", json={}, headers=headers)

    assert response.status_code == 201
    assert response.json()["data"]["name"] == "Untitled board"


async def test_get_board_by_id(db_client: AsyncClient) -> None:
    token = await _register_and_get_token(db_client)
    headers = {"Authorization": f"Bearer {token}"}
    create_response = await db_client.post("/boards", json={"name": "Roadmap"}, headers=headers)
    created = create_response.json()["data"]

    response = await db_client.get(f"/boards/{created['id']}", headers=headers)

    assert response.status_code == 200
    assert response.json()["data"]["name"] == "Roadmap"


async def test_get_missing_board_returns_404(db_client: AsyncClient) -> None:
    token = await _register_and_get_token(db_client)
    headers = {"Authorization": f"Bearer {token}"}

    response = await db_client.get("/boards/999999", headers=headers)

    assert response.status_code == 404


async def test_cannot_access_another_users_board(db_client: AsyncClient) -> None:
    owner_token = await _register_and_get_token(db_client, "owner2@example.com")
    other_token = await _register_and_get_token(db_client, "other@example.com")

    created = (
        await db_client.post(
            "/boards", json={"name": "Private"}, headers={"Authorization": f"Bearer {owner_token}"}
        )
    ).json()["data"]

    response = await db_client.get(
        f"/boards/{created['id']}", headers={"Authorization": f"Bearer {other_token}"}
    )

    assert response.status_code == 404


async def test_delete_board_removes_it(db_client: AsyncClient) -> None:
    token = await _register_and_get_token(db_client)
    headers = {"Authorization": f"Bearer {token}"}
    create_response = await db_client.post("/boards", json={"name": "Temp"}, headers=headers)
    created = create_response.json()["data"]

    delete_response = await db_client.delete(f"/boards/{created['id']}", headers=headers)
    assert delete_response.status_code == 200

    get_response = await db_client.get(f"/boards/{created['id']}", headers=headers)
    assert get_response.status_code == 404


async def test_rename_board(db_client: AsyncClient) -> None:
    token = await _register_and_get_token(db_client)
    headers = {"Authorization": f"Bearer {token}"}
    create_response = await db_client.post("/boards", json={"name": "Old name"}, headers=headers)
    created = create_response.json()["data"]

    rename_response = await db_client.patch(
        f"/boards/{created['id']}", json={"name": "New name"}, headers=headers
    )

    assert rename_response.status_code == 200
    assert rename_response.json()["data"]["name"] == "New name"

    get_response = await db_client.get(f"/boards/{created['id']}", headers=headers)
    assert get_response.json()["data"]["name"] == "New name"


async def test_rename_board_rejects_empty_name(db_client: AsyncClient) -> None:
    token = await _register_and_get_token(db_client)
    headers = {"Authorization": f"Bearer {token}"}
    create_response = await db_client.post("/boards", json={"name": "Old name"}, headers=headers)
    created = create_response.json()["data"]

    response = await db_client.patch(f"/boards/{created['id']}", json={"name": ""}, headers=headers)

    assert response.status_code == 422


async def test_cannot_rename_another_users_board(db_client: AsyncClient) -> None:
    owner_token = await _register_and_get_token(db_client, "renameowner@example.com")
    other_token = await _register_and_get_token(db_client, "renameother@example.com")
    created = (
        await db_client.post(
            "/boards", json={"name": "Private"}, headers={"Authorization": f"Bearer {owner_token}"}
        )
    ).json()["data"]

    response = await db_client.patch(
        f"/boards/{created['id']}",
        json={"name": "Hijacked"},
        headers={"Authorization": f"Bearer {other_token}"},
    )

    assert response.status_code == 404
