from datetime import date

from fastapi.testclient import TestClient
from sqlmodel import Session

from app import crud
from app.core.config import settings
from app.models import RoomCreate, UserCreate
from tests.utils.reservation import create_reservation as create_reservation_db
from tests.utils.room import create_random_room
from tests.utils.user import create_random_user, user_authentication_headers
from tests.utils.utils import random_email, random_lower_string


def test_available_rooms_invalid_date_range(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/reservations/available-rooms",
        headers=superuser_token_headers,
        params={
            "start_date": "2026-06-10",
            "end_date": "2026-06-05",
            "number_of_people": 1,
        },
    )
    assert response.status_code == 422
    assert response.json()["detail"] == "end_date must be after start_date"


def test_available_rooms_respects_capacity(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    room = create_random_room(db)
    # ensure capacity is small
    room.max_number_of_people = 2
    db.add(room)
    db.commit()
    db.refresh(room)

    response = client.get(
        f"{settings.API_V1_STR}/reservations/available-rooms",
        headers=superuser_token_headers,
        params={
            "start_date": "2026-07-01",
            "end_date": "2026-07-05",
            "number_of_people": 3,
        },
    )
    assert response.status_code == 200
    content = response.json()
    ids = {r["id"] for r in content["data"]}
    assert str(room.id) not in ids


def test_available_rooms_includes_room_when_no_conflict(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    room = create_random_room(db)

    response = client.get(
        f"{settings.API_V1_STR}/reservations/available-rooms",
        headers=superuser_token_headers,
        params={
            "start_date": "2026-08-01",
            "end_date": "2026-08-10",
            "number_of_people": 1,
        },
    )
    assert response.status_code == 200
    content = response.json()
    ids = {r["id"] for r in content["data"]}
    assert str(room.id) in ids


def test_available_rooms_excludes_overlapping_reservation(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    room = create_random_room(db)
    user = create_random_user(db)
    create_reservation_db(
        db,
        room_id=room.id,
        user_id=user.id,
        start_date=date(2026, 9, 1),
        end_date=date(2026, 9, 10),
    )

    response = client.get(
        f"{settings.API_V1_STR}/reservations/available-rooms",
        headers=superuser_token_headers,
        params={
            "start_date": "2026-09-05",
            "end_date": "2026-09-15",
            "number_of_people": 1,
        },
    )
    assert response.status_code == 200
    content = response.json()
    ids = {r["id"] for r in content["data"]}
    assert str(room.id) not in ids


def test_create_reservation_conflict(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    room = create_random_room(db)
    user = create_random_user(db)
    create_reservation_db(
        db,
        room_id=room.id,
        user_id=user.id,
        start_date=date(2026, 10, 1),
        end_date=date(2026, 10, 10),
    )

    response = client.post(
        f"{settings.API_V1_STR}/reservations/",
        headers=superuser_token_headers,
        json={
            "room_id": str(room.id),
            "start_date": "2026-10-05",
            "end_date": "2026-10-12",
        },
    )
    assert response.status_code == 409
    assert "overlapping" in response.json()["detail"].lower()


def test_create_reservation_success(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    room = create_random_room(db)

    response = client.post(
        f"{settings.API_V1_STR}/reservations/",
        headers=superuser_token_headers,
        json={
            "room_id": str(room.id),
            "start_date": "2026-11-01",
            "end_date": "2026-11-05",
        },
    )
    assert response.status_code == 200
    content = response.json()
    assert content["room_id"] == str(room.id)
    assert content["start_date"] == "2026-11-01"
    assert content["end_date"] == "2026-11-05"


def test_create_reservation_allowed_for_room_owner_non_superuser(
    client: TestClient, db: Session
) -> None:
    email = random_email()
    password = random_lower_string()
    owner = crud.create_user(
        session=db,
        user_create=UserCreate(email=email, password=password),
    )
    room = crud.create_room(
        session=db,
        room_in=RoomCreate(name="Owner room", max_number_of_people=4),
        owner_id=owner.id,
    )
    headers = user_authentication_headers(client=client, email=email, password=password)

    response = client.post(
        f"{settings.API_V1_STR}/reservations/",
        headers=headers,
        json={
            "room_id": str(room.id),
            "start_date": "2026-12-01",
            "end_date": "2026-12-05",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["user_id"] == str(owner.id)
    assert body["room_id"] == str(room.id)


def test_create_reservation_forbidden_for_another_users_room(
    client: TestClient, db: Session
) -> None:
    email = random_email()
    password = random_lower_string()
    crud.create_user(
        session=db,
        user_create=UserCreate(email=email, password=password),
    )
    other_room = create_random_room(db)
    headers = user_authentication_headers(client=client, email=email, password=password)

    response = client.post(
        f"{settings.API_V1_STR}/reservations/",
        headers=headers,
        json={
            "room_id": str(other_room.id),
            "start_date": "2026-12-01",
            "end_date": "2026-12-05",
        },
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Not enough permissions"


def test_read_reservations_empty(client: TestClient, db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    crud.create_user(
        session=db,
        user_create=UserCreate(email=email, password=password),
    )
    headers = user_authentication_headers(client=client, email=email, password=password)
    response = client.get(
        f"{settings.API_V1_STR}/reservations/",
        headers=headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["count"] == 0
    assert body["data"] == []


def test_read_reservations_includes_room_name(client: TestClient, db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    owner = crud.create_user(
        session=db,
        user_create=UserCreate(email=email, password=password),
    )
    room = crud.create_room(
        session=db,
        room_in=RoomCreate(name="List test room", max_number_of_people=3),
        owner_id=owner.id,
    )
    create_reservation_db(
        db,
        room_id=room.id,
        user_id=owner.id,
        start_date=date(2027, 1, 10),
        end_date=date(2027, 1, 15),
    )
    headers = user_authentication_headers(client=client, email=email, password=password)

    response = client.get(
        f"{settings.API_V1_STR}/reservations/",
        headers=headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["count"] == 1
    assert len(body["data"]) == 1
    row = body["data"][0]
    assert row["room_name"] == "List test room"
    assert row["room_id"] == str(room.id)
    assert row["start_date"] == "2027-01-10"


def test_read_reservations_only_current_user(client: TestClient, db: Session) -> None:
    email_a = random_email()
    password_a = random_lower_string()
    user_a = crud.create_user(
        session=db,
        user_create=UserCreate(email=email_a, password=password_a),
    )
    email_b = random_email()
    password_b = random_lower_string()
    crud.create_user(
        session=db,
        user_create=UserCreate(email=email_b, password=password_b),
    )
    room = create_random_room(db)
    create_reservation_db(
        db,
        room_id=room.id,
        user_id=user_a.id,
        start_date=date(2027, 2, 1),
        end_date=date(2027, 2, 5),
    )

    response_b = client.get(
        f"{settings.API_V1_STR}/reservations/",
        headers=user_authentication_headers(
            client=client, email=email_b, password=password_b
        ),
    )
    assert response_b.status_code == 200
    assert response_b.json()["count"] == 0

    response_a = client.get(
        f"{settings.API_V1_STR}/reservations/",
        headers=user_authentication_headers(
            client=client, email=email_a, password=password_a
        ),
    )
    assert response_a.status_code == 200
    assert response_a.json()["count"] == 1
