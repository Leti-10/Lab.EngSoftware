"""Cria comentarios, seguidores, notificacoes e preferencias.

Revision ID: c3e5a7b9d014
Revises: b7d2e9a4c611
Create Date: 2026-11-27 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c3e5a7b9d014"
down_revision: Union[str, Sequence[str], None] = "b7d2e9a4c611"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "comments",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("text", sa.String(length=500), nullable=False),
        sa.Column("review_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["review_id"], ["reviews.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_comments_review_id", "comments", ["review_id"])

    op.create_table(
        "follows",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("follower_id", sa.Integer(), nullable=False),
        sa.Column("target_type", sa.String(length=20), nullable=False),
        sa.Column("target_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["follower_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "follower_id", "target_type", "target_id", name="uq_follows_target"
        ),
    )
    op.create_index("ix_follows_target_id", "follows", ["target_id"])

    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("type", sa.String(length=20), nullable=False),
        sa.Column("actor_id", sa.Integer(), nullable=False),
        sa.Column("review_id", sa.Integer(), nullable=True),
        sa.Column("book_id", sa.Integer(), nullable=True),
        sa.Column("read", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["actor_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_notifications_user_id", "notifications", ["user_id"])

    op.create_table(
        "notification_preferences",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("likes", sa.Boolean(), nullable=False),
        sa.Column("comments", sa.Boolean(), nullable=False),
        sa.Column("follows", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id"),
    )


def downgrade() -> None:
    op.drop_table("notification_preferences")
    op.drop_index("ix_notifications_user_id", table_name="notifications")
    op.drop_table("notifications")
    op.drop_index("ix_follows_target_id", table_name="follows")
    op.drop_table("follows")
    op.drop_index("ix_comments_review_id", table_name="comments")
    op.drop_table("comments")
