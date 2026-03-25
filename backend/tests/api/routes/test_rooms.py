import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from tests.utils.room import create_random_room


def test_create_room(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    data = {"name": "Suite A", "max_number_of_people": 4}
    response = client.post(
        f"{settings.API_V1_STR}/rooms/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == data["name"]
    assert content["max_number_of_people"] == data["max_number_of_people"]
    assert "id" in content
    assert "owner_id" in content


def test_read_room(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    room = create_random_room(db)
    response = client.get(
        f"{settings.API_V1_STR}/rooms/{room.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == room.name
    assert content["max_number_of_people"] == room.max_number_of_people
    assert content["id"] == str(room.id)
    assert content["owner_id"] == str(room.owner_id)


def test_read_room_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/rooms/{uuid.uuid4()}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Room not found"


def test_read_room_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    room = create_random_room(db)
    response = client.get(
        f"{settings.API_V1_STR}/rooms/{room.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 403
    content = response.json()
    assert content["detail"] == "Not enough permissions"


def test_read_rooms(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    create_random_room(db)
    create_random_room(db)
    response = client.get(
        f"{settings.API_V1_STR}/rooms/",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content["data"]) >= 2


def test_update_room(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    room = create_random_room(db)
    data = {"name": "Updated name", "max_number_of_people": 6}
    response = client.put(
        f"{settings.API_V1_STR}/rooms/{room.id}",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == data["name"]
    assert content["max_number_of_people"] == data["max_number_of_people"]
    assert content["id"] == str(room.id)
    assert content["owner_id"] == str(room.owner_id)


def test_update_room_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    data = {"name": "Updated name", "max_number_of_people": 3}
    response = client.put(
        f"{settings.API_V1_STR}/rooms/{uuid.uuid4()}",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Room not found"


def test_update_room_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    room = create_random_room(db)
    data = {"name": "Updated name", "max_number_of_people": 3}
    response = client.put(
        f"{settings.API_V1_STR}/rooms/{room.id}",
        headers=normal_user_token_headers,
        json=data,
    )
    assert response.status_code == 403
    content = response.json()
    assert content["detail"] == "Not enough permissions"


def test_delete_room(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    room = create_random_room(db)
    response = client.delete(
        f"{settings.API_V1_STR}/rooms/{room.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["message"] == "Room deleted successfully"


def test_delete_room_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.delete(
        f"{settings.API_V1_STR}/rooms/{uuid.uuid4()}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Room not found"


def test_delete_room_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    room = create_random_room(db)
    response = client.delete(
        f"{settings.API_V1_STR}/rooms/{room.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 403
    content = response.json()
    assert content["detail"] == "Not enough permissions"
