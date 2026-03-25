"""Rename item table to room; name and max_number_of_people

Revision ID: b4c8e2a1f903
Revises: fe56fa70289e
Create Date: 2026-03-25

"""
import sqlalchemy as sa
from alembic import op

revision = "b4c8e2a1f903"
down_revision = "fe56fa70289e"
branch_labels = None
depends_on = None


def upgrade():
    op.rename_table("item", "room")
    op.execute('ALTER TABLE room RENAME COLUMN title TO name')
    op.drop_column("room", "description")
    op.add_column(
        "room",
        sa.Column(
            "max_number_of_people",
            sa.Integer(),
            nullable=False,
            server_default="1",
        ),
    )
    op.alter_column("room", "max_number_of_people", server_default=None)


def downgrade():
    op.add_column(
        "room",
        sa.Column("description", sa.String(), nullable=True),
    )
    op.drop_column("room", "max_number_of_people")
    op.execute("ALTER TABLE room RENAME COLUMN name TO title")
    op.rename_table("room", "item")
