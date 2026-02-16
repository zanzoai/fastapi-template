"""create zan_user table

Revision ID: create_zan_user
Revises: add_name_mobile_users
Create Date: 2024-01-01 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'create_zan_user'
down_revision: Union[str, None] = 'add_name_mobile_users'  # Set to None if this is your first migration
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    insp = sa.inspect(conn)
    tables = insp.get_table_names()

    if "zan_user" not in tables:
        op.create_table(
            "zan_user",
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("first_name", sa.String(), nullable=False),
            sa.Column("last_name", sa.String(), nullable=False),
            sa.Column("email", sa.String(), nullable=False),
            sa.Column("phone", sa.String(), nullable=True),
            sa.Column("address", sa.Text(), nullable=True),
            sa.Column("is_zancrew", sa.String(), nullable=False, server_default="false"),
            sa.Column("zancrew_id", sa.Integer(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.PrimaryKeyConstraint("user_id"),
        )
    # Create unique index on email only if table was just created or index missing
    indexes = {idx["name"] for idx in insp.get_indexes("zan_user")} if "zan_user" in tables else set()
    if "ix_zan_user_email" not in indexes:
        op.create_index("ix_zan_user_email", "zan_user", ["email"], unique=True)


def downgrade() -> None:
    insp = sa.inspect(op.get_bind())
    if "zan_user" in insp.get_table_names():
        indexes = {idx["name"] for idx in insp.get_indexes("zan_user")}
        if "ix_zan_user_email" in indexes:
            op.drop_index("ix_zan_user_email", table_name="zan_user")
        op.drop_table("zan_user")

