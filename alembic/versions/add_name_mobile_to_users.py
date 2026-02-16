"""add name and mobile to users table

Revision ID: add_name_mobile_users
Revises: 
Create Date: 2024-01-01 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_name_mobile_users'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add name and mobile only if they don't exist (e.g. table was created by create_all)
    conn = op.get_bind()
    insp = sa.inspect(conn)
    cols = {c["name"] for c in insp.get_columns("users")}
    if "name" not in cols:
        op.add_column("users", sa.Column("name", sa.String(), nullable=True))
    if "mobile" not in cols:
        op.add_column("users", sa.Column("mobile", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "mobile")
    op.drop_column("users", "name")

