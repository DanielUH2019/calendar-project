import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import col, func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import Message, Room, RoomCreate, RoomPublic, RoomsPublic, RoomUpdate

router = APIRouter(prefix="/rooms", tags=["rooms"])


@router.get("/", response_model=RoomsPublic)
def read_rooms(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve rooms.
    """

    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(Room)
        count = session.exec(count_statement).one()
        statement = (
            select(Room).order_by(col(Room.created_at).desc()).offset(skip).limit(limit)
        )
        rooms = session.exec(statement).all()
    else:
        count_statement = (
            select(func.count())
            .select_from(Room)
            .where(Room.owner_id == current_user.id)
        )
        count = session.exec(count_statement).one()
        statement = (
            select(Room)
            .where(Room.owner_id == current_user.id)
            .order_by(col(Room.created_at).desc())
            .offset(skip)
            .limit(limit)
        )
        rooms = session.exec(statement).all()

    return RoomsPublic(data=rooms, count=count)


@router.get("/{id}", response_model=RoomPublic)
def read_room(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get room by ID.
    """
    room = session.get(Room, id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    if not current_user.is_superuser and (room.owner_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return room


@router.post("/", response_model=RoomPublic)
def create_room(
    *, session: SessionDep, current_user: CurrentUser, room_in: RoomCreate
) -> Any:
    """
    Create new room.
    """
    room = Room.model_validate(room_in, update={"owner_id": current_user.id})
    session.add(room)
    session.commit()
    session.refresh(room)
    return room


@router.put("/{id}", response_model=RoomPublic)
def update_room(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    room_in: RoomUpdate,
) -> Any:
    """
    Update a room.
    """
    room = session.get(Room, id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    if not current_user.is_superuser and (room.owner_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    update_dict = room_in.model_dump(exclude_unset=True)
    room.sqlmodel_update(update_dict)
    session.add(room)
    session.commit()
    session.refresh(room)
    return room


@router.delete("/{id}")
def delete_room(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete a room.
    """
    room = session.get(Room, id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    if not current_user.is_superuser and (room.owner_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    session.delete(room)
    session.commit()
    return Message(message="Room deleted successfully")
