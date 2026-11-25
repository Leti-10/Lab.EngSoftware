"""Remove a FK de reviews.book_id enquanto os livros ficam em memoria.

Revision ID: e4a1b7c93d52
Revises: c20b7e7bd31f
Create Date: 2026-11-23 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = "e4a1b7c93d52"
down_revision: Union[str, Sequence[str], None] = "c20b7e7bd31f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint("reviews_book_id_fkey", "reviews", type_="foreignkey")
    op.create_index("ix_reviews_book_id", "reviews", ["book_id"])


def downgrade() -> None:
    op.drop_index("ix_reviews_book_id", table_name="reviews")
    op.create_foreign_key(
        "reviews_book_id_fkey",
        "reviews",
        "books",
        ["book_id"],
        ["id"],
        ondelete="CASCADE",
    )
