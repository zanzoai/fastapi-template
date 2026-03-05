"""Make zan_user.user_id auto-increment (SERIAL) so INSERT without user_id works

Revision ID: zan_user_serial
Revises: add_chat_tables
Create Date: 2025-02-15

On Railway (and when using Alembic), the zan_user table was created with
user_id INTEGER NOT NULL and no default, so create_zan_user API failed or
did not persist. This migration adds a sequence and default so new rows
get user_id automatically.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "zan_user_serial"
down_revision: Union[str, None] = "add_chat_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # PostgreSQL: create sequence and set as default for user_id so INSERT can omit it
    op.execute(sa.text(
        "CREATE SEQUENCE IF NOT EXISTS zan_user_user_id_seq AS integer OWNED BY zan_user.user_id"
    ))
    op.alter_column(
        "zan_user",
        "user_id",
        existing_type=sa.Integer(),
        server_default=sa.text("nextval('zan_user_user_id_seq'::regclass)"),
    )
    op.execute(sa.text(
        "SELECT setval('zan_user_user_id_seq', COALESCE((SELECT MAX(user_id) FROM zan_user), 1))"
    ))


def downgrade() -> None:
    op.alter_column(
        "zan_user",
        "user_id",
        existing_type=sa.Integer(),
        server_default=None,
    )
    op.execute(sa.text("DROP SEQUENCE IF EXISTS zan_user_user_id_seq CASCADE"))
