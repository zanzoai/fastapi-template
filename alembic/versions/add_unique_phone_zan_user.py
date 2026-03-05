"""add unique constraint on phone for zan_user

Revision ID: add_unique_phone_zan_user
Revises: zan_user_serial
Create Date: 2024-01-01 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision: str = "add_unique_phone_zan_user"
down_revision: Union[str, None] = "zan_user_serial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()

    # Step 1: Remove duplicate phones - keep first occurrence (min user_id), delete the rest
    # Note: If deleted rows have FK references (zan_crew, jobs, etc.), run will fail.
    # Clean up or reassign those first if needed.
    conn.execute(text("""
        DELETE FROM zan_user
        WHERE user_id IN (
            SELECT user_id FROM (
                SELECT user_id,
                       ROW_NUMBER() OVER (PARTITION BY phone ORDER BY user_id) AS rn
                FROM zan_user
            ) ranked
            WHERE rn > 1
        )
    """))

    # Step 2: Create unique index on phone
    op.create_index(
        "ix_zan_user_phone",
        "zan_user",
        ["phone"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("ix_zan_user_phone", table_name="zan_user")
