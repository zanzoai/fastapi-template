"""Add chat tables and job status for task-based chat

Revision ID: add_chat_tables
Revises: modify_jobs_table
Create Date: 2025-02-15

Design:
- One chat_room per job (job-centric, not user-to-user).
- chat_participants: explicit membership with participant_type for future multi-crew.
- chat_messages: job-scoped; authorization via chat_participants.
- Optional message_reads: trade-off documented in CHAT_DESIGN.md.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "add_chat_tables"
down_revision: Union[str, None] = "modify_jobs_table"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists(inspector: sa.Inspector, name: str) -> bool:
    return name in inspector.get_table_names()


def _index_exists(inspector: sa.Inspector, table: str, index_name: str) -> bool:
    if table not in inspector.get_table_names():
        return False
    return any(idx["name"] == index_name for idx in inspector.get_indexes(table))


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    # --- Job status: used to make chat read-only when job is closed ---
    if "jobs" in inspector.get_table_names():
        cols = [c["name"] for c in inspector.get_columns("jobs")]
        if "status" not in cols:
            op.add_column(
                "jobs",
                sa.Column(
                    "status",
                    sa.String(32),
                    nullable=True,
                    server_default="open",
                ),
            )

    # --- chat_rooms: 1 per job ---
    if not _table_exists(inspector, "chat_rooms"):
        op.create_table(
            "chat_rooms",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("job_id", sa.Integer(), sa.ForeignKey("jobs.job_id", ondelete="CASCADE"), nullable=False),
            sa.Column("is_read_only", sa.Boolean(), nullable=False, server_default="false"),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now()),
        )
    if not _index_exists(inspector, "chat_rooms", "ix_chat_rooms_job_id"):
        op.create_index("ix_chat_rooms_job_id", "chat_rooms", ["job_id"], unique=True)

    # --- chat_participants ---
    if not _table_exists(inspector, "chat_participants"):
        op.create_table(
            "chat_participants",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("chat_room_id", sa.Integer(), sa.ForeignKey("chat_rooms.id", ondelete="CASCADE"), nullable=False),
            sa.Column("participant_type", sa.String(16), nullable=False),
            sa.Column("zan_user_id", sa.Integer(), sa.ForeignKey("zan_user.user_id", ondelete="CASCADE"), nullable=True),
            sa.Column("zancrew_id", sa.Integer(), sa.ForeignKey("zan_crew.zancrew_id", ondelete="CASCADE"), nullable=True),
            sa.Column("joined_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.CheckConstraint(
                "(participant_type = 'zan_user' AND zan_user_id IS NOT NULL AND zancrew_id IS NULL) OR "
                "(participant_type = 'zan_crew' AND zancrew_id IS NOT NULL AND zan_user_id IS NULL)",
                name="ck_chat_participants_type_ref",
            ),
        )
    for idx_name in ("ix_chat_participants_chat_room_id", "ix_chat_participants_zan_user_id", "ix_chat_participants_zancrew_id",
                     "uq_chat_participants_room_zan_user", "uq_chat_participants_room_zancrew"):
        if not _index_exists(inspector, "chat_participants", idx_name):
            if idx_name == "ix_chat_participants_chat_room_id":
                op.create_index(idx_name, "chat_participants", ["chat_room_id"])
            elif idx_name == "ix_chat_participants_zan_user_id":
                op.create_index(idx_name, "chat_participants", ["zan_user_id"], postgresql_where=sa.text("zan_user_id IS NOT NULL"))
            elif idx_name == "ix_chat_participants_zancrew_id":
                op.create_index(idx_name, "chat_participants", ["zancrew_id"], postgresql_where=sa.text("zancrew_id IS NOT NULL"))
            elif idx_name == "uq_chat_participants_room_zan_user":
                op.create_index(idx_name, "chat_participants", ["chat_room_id", "zan_user_id"], unique=True, postgresql_where=sa.text("zan_user_id IS NOT NULL"))
            else:
                op.create_index(idx_name, "chat_participants", ["chat_room_id", "zancrew_id"], unique=True, postgresql_where=sa.text("zancrew_id IS NOT NULL"))

    # --- chat_messages ---
    if not _table_exists(inspector, "chat_messages"):
        op.create_table(
            "chat_messages",
            sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
            sa.Column("chat_room_id", sa.Integer(), sa.ForeignKey("chat_rooms.id", ondelete="CASCADE"), nullable=False),
            sa.Column("sender_type", sa.String(16), nullable=False),
            sa.Column("sender_zan_user_id", sa.Integer(), nullable=True),
            sa.Column("sender_zancrew_id", sa.Integer(), nullable=True),
            sa.Column("content", sa.Text(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.CheckConstraint(
                "(sender_type = 'zan_user' AND sender_zan_user_id IS NOT NULL AND sender_zancrew_id IS NULL) OR "
                "(sender_type = 'zan_crew' AND sender_zancrew_id IS NOT NULL AND sender_zan_user_id IS NULL) OR "
                "(sender_type = 'system' AND sender_zan_user_id IS NULL AND sender_zancrew_id IS NULL)",
                name="ck_chat_messages_sender_ref",
            ),
        )
    if not _index_exists(inspector, "chat_messages", "ix_chat_messages_chat_room_id"):
        op.create_index("ix_chat_messages_chat_room_id", "chat_messages", ["chat_room_id"])
    if not _index_exists(inspector, "chat_messages", "ix_chat_messages_chat_room_created"):
        op.create_index("ix_chat_messages_chat_room_created", "chat_messages", ["chat_room_id", "created_at"])

    # --- message_reads ---
    if not _table_exists(inspector, "message_reads"):
        op.create_table(
            "message_reads",
            sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
            sa.Column("message_id", sa.BigInteger(), sa.ForeignKey("chat_messages.id", ondelete="CASCADE"), nullable=False),
            sa.Column("participant_id", sa.Integer(), sa.ForeignKey("chat_participants.id", ondelete="CASCADE"), nullable=False),
            sa.Column("read_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.UniqueConstraint("message_id", "participant_id", name="uq_message_reads_message_participant"),
        )
    if not _index_exists(inspector, "message_reads", "ix_message_reads_message_id"):
        op.create_index("ix_message_reads_message_id", "message_reads", ["message_id"])
    if not _index_exists(inspector, "message_reads", "ix_message_reads_participant_id"):
        op.create_index("ix_message_reads_participant_id", "message_reads", ["participant_id"])


def downgrade() -> None:
    op.drop_table("message_reads")
    op.drop_table("chat_messages")
    op.drop_table("chat_participants")
    op.drop_table("chat_rooms")
    # Optionally drop job.status; leave in place to avoid data loss
    # op.drop_column("jobs", "status")
