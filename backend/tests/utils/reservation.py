from datetime import date
from uuid import UUID

from sqlmodel import Session

from app import crud
from app.models import Reservation, ReservationCreate


def create_reservation(
    db: Session,
    *,
    room_id: UUID,
    user_id: UUID,
    start_date: date,
    end_date: date,
) -> Reservation:
    res_in = ReservationCreate(
        room_id=room_id,
        start_date=start_date,
        end_date=end_date,
    )
    return crud.create_reservation(session=db, reservation_in=res_in, user_id=user_id)
