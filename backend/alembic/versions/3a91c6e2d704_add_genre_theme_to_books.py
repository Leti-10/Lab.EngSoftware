"""Add genre and theme to books.

Revision ID: 3a91c6e2d704
Revises: 10e4eb701ae0
Create Date: 2026-12-03 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "3a91c6e2d704"
down_revision: Union[str, Sequence[str], None] = "10e4eb701ae0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "books",
        sa.Column(
            "genre",
            postgresql.ARRAY(sa.String()),
            server_default=sa.text("'{}'"),
            nullable=False,
        ),
    )
    op.add_column(
        "books",
        sa.Column(
            "theme",
            postgresql.ARRAY(sa.String()),
            server_default=sa.text("'{}'"),
            nullable=False,
        ),
    )
    op.alter_column("books", "genre", server_default=None)
    op.alter_column("books", "theme", server_default=None)


def downgrade() -> None:
    op.drop_column("books", "theme")
    op.drop_column("books", "genre")
