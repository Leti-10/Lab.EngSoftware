"""Adiciona bio, avatar e capa ao usuario.

Revision ID: b7d2e9a4c611
Revises: f2b8c1d47a90
Create Date: 2026-11-26 10:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b7d2e9a4c611"
down_revision: Union[str, Sequence[str], None] = "f2b8c1d47a90"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("bio", sa.String(length=300), nullable=True))
    op.add_column(
        "users", sa.Column("avatar_url", sa.String(length=500), nullable=True)
    )
    op.add_column("users", sa.Column("cover_url", sa.String(length=500), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "cover_url")
    op.drop_column("users", "avatar_url")
    op.drop_column("users", "bio")
