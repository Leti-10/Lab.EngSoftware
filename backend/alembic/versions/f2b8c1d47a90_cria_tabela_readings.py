"""Cria a tabela de status de leitura.

Revision ID: f2b8c1d47a90
Revises: e4a1b7c93d52
Create Date: 2026-11-23 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f2b8c1d47a90"
down_revision: Union[str, Sequence[str], None] = "e4a1b7c93d52"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "readings",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("book_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "book_id", name="uq_readings_user_book"),
    )
    op.create_index("ix_readings_book_id", "readings", ["book_id"])


def downgrade() -> None:
    op.drop_index("ix_readings_book_id", table_name="readings")
    op.drop_table("readings")
