from sqlmodel import Session

from app import crud
from app.models import Room, RoomCreate
from tests.utils.user import create_random_user
from tests.utils.utils import random_lower_string


def create_random_room(db: Session) -> Room:
    user = create_random_user(db)
    owner_id = user.id
    assert owner_id is not None
    name = random_lower_string()
    room_in = RoomCreate(name=name, max_number_of_people=2)
    return crud.create_room(session=db, room_in=room_in, owner_id=owner_id)
