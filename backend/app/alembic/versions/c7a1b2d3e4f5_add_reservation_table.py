"""Add reservation table

Revision ID: c7a1b2d3e4f5
Revises: b4c8e2a1f903
Create Date: 2026-03-31

"""

import sqlalchemy as sa
from alembic import op

revision = "c7a1b2d3e4f5"
down_revision = "b4c8e2a1f903"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "reservation",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("room_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["room_id"], ["room.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_reservation_room_id"), "reservation", ["room_id"], unique=False
    )
    op.create_index(
        op.f("ix_reservation_user_id"), "reservation", ["user_id"], unique=False
    )
    op.create_index(
        "ix_reservation_range_status",
        "reservation",
        ["room_id", "start_date", "end_date", "status"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_reservation_range_status", table_name="reservation")
    op.drop_index(op.f("ix_reservation_user_id"), table_name="reservation")
    op.drop_index(op.f("ix_reservation_room_id"), table_name="reservation")
    op.drop_table("reservation")
