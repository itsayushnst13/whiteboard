from typing import Any

from httpx import AsyncClient


async def _register(client: AsyncClient, email: str, display_name: str = "User") -> dict[str, Any]:
    response = await client.post(
        "/auth/register",
        json={"email": email, "password": "supersecret", "display_name": display_name},
    )
    data: dict[str, Any] = response.json()["data"]
    return data


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


async def _create_board(
    client: AsyncClient, token: str, name: str = "Shared board"
) -> dict[str, Any]:
    response = await client.post("/boards", json={"name": name}, headers=_auth(token))
    data: dict[str, Any] = response.json()["data"]
    return data


async def test_owner_can_invite_collaborator_by_email(db_client: AsyncClient) -> None:
    owner = await _register(db_client, "owner@example.com", "Owner")
    await _register(db_client, "friend@example.com", "Friend")
    board = await _create_board(db_client, owner["access_token"])

    response = await db_client.post(
        f"/boards/{board['id']}/share",
        json={"email": "friend@example.com", "role": "editor"},
        headers=_auth(owner["access_token"]),
    )

    assert response.status_code == 201
    data = response.json()["data"]
    assert data["email"] == "friend@example.com"
    assert data["role"] == "editor"


async def test_invited_collaborator_can_open_the_board(db_client: AsyncClient) -> None:
    owner = await _register(db_client, "owner2@example.com", "Owner")
    friend = await _register(db_client, "friend2@example.com", "Friend")
    board = await _create_board(db_client, owner["access_token"])

    await db_client.post(
        f"/boards/{board['id']}/share",
        json={"email": "friend2@example.com", "role": "editor"},
        headers=_auth(owner["access_token"]),
    )

    response = await db_client.get(f"/boards/{board['id']}", headers=_auth(friend["access_token"]))

    assert response.status_code == 200
    assert response.json()["data"]["role"] == "editor"


async def test_shared_board_appears_in_collaborators_board_list(db_client: AsyncClient) -> None:
    owner = await _register(db_client, "owner3@example.com", "Owner")
    friend = await _register(db_client, "friend3@example.com", "Friend")
    board = await _create_board(db_client, owner["access_token"], "Team board")

    await db_client.post(
        f"/boards/{board['id']}/share",
        json={"email": "friend3@example.com", "role": "viewer"},
        headers=_auth(owner["access_token"]),
    )

    response = await db_client.get("/boards", headers=_auth(friend["access_token"]))

    assert response.status_code == 200
    boards = response.json()["data"]
    assert len(boards) == 1
    assert boards[0]["id"] == board["id"]
    assert boards[0]["role"] == "viewer"


async def test_uninvited_user_gets_403_not_404(db_client: AsyncClient) -> None:
    owner = await _register(db_client, "owner4@example.com", "Owner")
    stranger = await _register(db_client, "stranger4@example.com", "Stranger")
    board = await _create_board(db_client, owner["access_token"])

    response = await db_client.get(
        f"/boards/{board['id']}", headers=_auth(stranger["access_token"])
    )

    assert response.status_code == 403


async def test_only_owner_can_invite(db_client: AsyncClient) -> None:
    owner = await _register(db_client, "owner5@example.com", "Owner")
    editor = await _register(db_client, "editor5@example.com", "Editor")
    await _register(db_client, "outsider5@example.com", "Outsider")
    board = await _create_board(db_client, owner["access_token"])
    await db_client.post(
        f"/boards/{board['id']}/share",
        json={"email": "editor5@example.com", "role": "editor"},
        headers=_auth(owner["access_token"]),
    )

    response = await db_client.post(
        f"/boards/{board['id']}/share",
        json={"email": "outsider5@example.com", "role": "editor"},
        headers=_auth(editor["access_token"]),
    )

    assert response.status_code == 403


async def test_invite_unknown_email_returns_404(db_client: AsyncClient) -> None:
    owner = await _register(db_client, "owner6@example.com", "Owner")
    board = await _create_board(db_client, owner["access_token"])

    response = await db_client.post(
        f"/boards/{board['id']}/share",
        json={"email": "nobody@example.com", "role": "editor"},
        headers=_auth(owner["access_token"]),
    )

    assert response.status_code == 404


async def test_invite_self_is_rejected(db_client: AsyncClient) -> None:
    owner = await _register(db_client, "owner7@example.com", "Owner")
    board = await _create_board(db_client, owner["access_token"])

    response = await db_client.post(
        f"/boards/{board['id']}/share",
        json={"email": "owner7@example.com", "role": "editor"},
        headers=_auth(owner["access_token"]),
    )

    assert response.status_code == 409


async def test_reinviting_updates_role(db_client: AsyncClient) -> None:
    owner = await _register(db_client, "owner8@example.com", "Owner")
    await _register(db_client, "friend8@example.com", "Friend")
    board = await _create_board(db_client, owner["access_token"])

    await db_client.post(
        f"/boards/{board['id']}/share",
        json={"email": "friend8@example.com", "role": "viewer"},
        headers=_auth(owner["access_token"]),
    )
    response = await db_client.post(
        f"/boards/{board['id']}/share",
        json={"email": "friend8@example.com", "role": "editor"},
        headers=_auth(owner["access_token"]),
    )

    assert response.status_code == 201
    assert response.json()["data"]["role"] == "editor"

    list_response = await db_client.get(
        f"/boards/{board['id']}/collaborators", headers=_auth(owner["access_token"])
    )
    collaborators = list_response.json()["data"]
    assert len(collaborators) == 1
    assert collaborators[0]["role"] == "editor"


async def test_owner_can_remove_collaborator(db_client: AsyncClient) -> None:
    owner = await _register(db_client, "owner9@example.com", "Owner")
    friend = await _register(db_client, "friend9@example.com", "Friend")
    board = await _create_board(db_client, owner["access_token"])
    await db_client.post(
        f"/boards/{board['id']}/share",
        json={"email": "friend9@example.com", "role": "editor"},
        headers=_auth(owner["access_token"]),
    )

    remove_response = await db_client.delete(
        f"/boards/{board['id']}/collaborators/{friend['user']['id']}",
        headers=_auth(owner["access_token"]),
    )
    assert remove_response.status_code == 200

    access_response = await db_client.get(
        f"/boards/{board['id']}", headers=_auth(friend["access_token"])
    )
    assert access_response.status_code == 403


async def test_collaborator_cannot_remove_collaborators(db_client: AsyncClient) -> None:
    owner = await _register(db_client, "owner10@example.com", "Owner")
    editor = await _register(db_client, "editor10@example.com", "Editor")
    board = await _create_board(db_client, owner["access_token"])
    await db_client.post(
        f"/boards/{board['id']}/share",
        json={"email": "editor10@example.com", "role": "editor"},
        headers=_auth(owner["access_token"]),
    )

    response = await db_client.delete(
        f"/boards/{board['id']}/collaborators/{owner['user']['id']}",
        headers=_auth(editor["access_token"]),
    )

    assert response.status_code == 403


async def test_collaborator_cannot_delete_board(db_client: AsyncClient) -> None:
    owner = await _register(db_client, "owner11@example.com", "Owner")
    editor = await _register(db_client, "editor11@example.com", "Editor")
    board = await _create_board(db_client, owner["access_token"])
    await db_client.post(
        f"/boards/{board['id']}/share",
        json={"email": "editor11@example.com", "role": "editor"},
        headers=_auth(owner["access_token"]),
    )

    response = await db_client.delete(
        f"/boards/{board['id']}", headers=_auth(editor["access_token"])
    )

    assert response.status_code == 403
