import uuid
from datetime import date, datetime, timezone

from pydantic import EmailStr, model_validator
from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, SQLModel


def get_datetime_utc() -> datetime:
    return datetime.now(timezone.utc)


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=128)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    rooms: list["Room"] = Relationship(back_populates="owner", cascade_delete=True)
    reservations: list["Reservation"] = Relationship(
        back_populates="user", cascade_delete=True
    )


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID
    created_at: datetime | None = None


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Shared properties
class RoomBase(SQLModel):
    name: str = Field(min_length=1, max_length=255)
    max_number_of_people: int = Field(ge=1)


class RoomCreate(RoomBase):
    pass


class RoomUpdate(SQLModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    max_number_of_people: int | None = Field(default=None, ge=1)


class Room(RoomBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="rooms")
    reservations: list["Reservation"] = Relationship(
        back_populates="room", cascade_delete=True
    )


class ReservationBase(SQLModel):
    start_date: date
    end_date: date
    status: str = Field(default="active", max_length=20)


class ReservationCreate(SQLModel):
    room_id: uuid.UUID
    start_date: date
    end_date: date

    @model_validator(mode="after")
    def end_after_start(self) -> "ReservationCreate":
        if self.end_date <= self.start_date:
            raise ValueError("end_date must be after start_date")
        return self


class ReservationPublic(ReservationBase):
    id: uuid.UUID
    room_id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime | None = None
    room_name: str | None = None


class ReservationsPublic(SQLModel):
    data: list[ReservationPublic]
    count: int


class Reservation(ReservationBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    room_id: uuid.UUID = Field(
        foreign_key="room.id", nullable=False, ondelete="CASCADE"
    )
    user_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    room: Room | None = Relationship(back_populates="reservations")
    user: User | None = Relationship(back_populates="reservations")


class RoomPublic(RoomBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    created_at: datetime | None = None


class RoomsPublic(SQLModel):
    data: list[RoomPublic]
    count: int


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)
