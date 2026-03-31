import uuid
from datetime import date
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlalchemy import and_, exists
from sqlmodel import Session, col, func, select

from app import crud
from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Reservation,
    ReservationCreate,
    ReservationPublic,
    ReservationsPublic,
    Room,
    RoomsPublic,
)

ACTIVE_RESERVATION = "active"

router = APIRouter(prefix="/reservations", tags=["reservations"])


def _assert_date_range(start: date, end: date) -> None:
    if end <= start:
        raise HTTPException(
            status_code=422,
            detail="end_date must be after start_date",
        )


def _reservation_conflicts(
    *,
    session: Session,
    room_id: uuid.UUID,
    start_q: date,
    end_q: date,
) -> bool:
    stmt = select(Reservation.id).where(
        Reservation.room_id == room_id,
        Reservation.status == ACTIVE_RESERVATION,
        col(Reservation.start_date) < end_q,
        col(Reservation.end_date) > start_q,
    )
    return session.exec(stmt).first() is not None


@router.get("/available-rooms", response_model=RoomsPublic)
def read_available_rooms(
    session: SessionDep,
    current_user: CurrentUser,
    start_date: date,
    end_date: date,
    number_of_people: int,
) -> Any:
    """
    Rooms that fit the party size and have no overlapping active reservation
    in [start_date, end_date) (half-open interval).
    """
    _assert_date_range(start_date, end_date)

    conflict_exists = exists(
        select(Reservation.id).where(
            Reservation.room_id == Room.id,
            Reservation.status == ACTIVE_RESERVATION,
            col(Reservation.start_date) < end_date,
            col(Reservation.end_date) > start_date,
        )
    )

    room_filters = and_(
        col(Room.max_number_of_people) >= number_of_people,
        ~conflict_exists,
    )
    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(Room).where(room_filters)
        statement = (
            select(Room).where(room_filters).order_by(col(Room.created_at).desc())
        )
    else:
        count_statement = (
            select(func.count())
            .select_from(Room)
            .where(
                room_filters,
                Room.owner_id == current_user.id,
            )
        )
        statement = (
            select(Room)
            .where(room_filters, Room.owner_id == current_user.id)
            .order_by(col(Room.created_at).desc())
        )

    count = session.exec(count_statement).one()
    rooms = session.exec(statement).all()
    return RoomsPublic(data=rooms, count=count)


@router.get("/", response_model=ReservationsPublic)
def read_reservations(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Reservations created by the current user, newest stays first.
    """
    user_filter = Reservation.user_id == current_user.id
    count_statement = select(func.count()).select_from(Reservation).where(user_filter)
    count = session.exec(count_statement).one()
    statement = (
        select(Reservation, Room.name)
        .join(Room, col(Reservation.room_id) == col(Room.id))
        .where(user_filter)
        .order_by(col(Reservation.start_date).desc())
        .offset(skip)
        .limit(limit)
    )
    rows = session.exec(statement).all()
    data = [
        ReservationPublic(
            id=res.id,
            start_date=res.start_date,
            end_date=res.end_date,
            status=res.status,
            room_id=res.room_id,
            user_id=res.user_id,
            created_at=res.created_at,
            room_name=name,
        )
        for res, name in rows
    ]
    return ReservationsPublic(data=data, count=count)


@router.post("/", response_model=ReservationPublic)
def create_reservation(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    reservation_in: ReservationCreate,
) -> Any:
    """
    Create a reservation for a room. Any authenticated user may do this for rooms
    they own; superusers may create reservations for any room.
    """
    room = session.get(Room, reservation_in.room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    if not current_user.is_superuser and room.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    _assert_date_range(reservation_in.start_date, reservation_in.end_date)

    if _reservation_conflicts(
        session=session,
        room_id=reservation_in.room_id,
        start_q=reservation_in.start_date,
        end_q=reservation_in.end_date,
    ):
        raise HTTPException(
            status_code=409,
            detail="Room is already reserved for overlapping dates",
        )

    return crud.create_reservation(
        session=session,
        reservation_in=reservation_in,
        user_id=current_user.id,
    )
