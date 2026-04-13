"""add users table

Revision ID: 20260413_0002
Revises: 20260406_0001
Create Date: 2026-04-13 12:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260413_0002"
down_revision: Union[str, Sequence[str], None] = "20260406_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("username", sa.String(length=100), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(length=64), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("users")
