from typing import Optional

from sqlalchemy import and_, desc
from sqlalchemy.orm import Session

from infrastructure.db.models import (
    Job,
    ChatRoom,
    ChatParticipant,
    ChatMessage,
)


class ChatRoomRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, chat_room_id: int) -> Optional[ChatRoom]:
        return self.db.query(ChatRoom).filter(ChatRoom.id == chat_room_id).first()

    def get_by_job_id(self, job_id: int) -> Optional[ChatRoom]:
        return self.db.query(ChatRoom).filter(ChatRoom.job_id == job_id).first()

    def create_for_job(
        self,
        job_id: int,
        zan_user_id: int,
        zancrew_id: int,
    ) -> ChatRoom:
        room = ChatRoom(job_id=job_id, is_read_only=False)
        self.db.add(room)
        self.db.flush()
        for participant_type, zuid, zcid in [
            ("zan_user", zan_user_id, None),
            ("zan_crew", None, zancrew_id),
        ]:
            p = ChatParticipant(
                chat_room_id=room.id,
                participant_type=participant_type,
                zan_user_id=zuid,
                zancrew_id=zcid,
            )
            self.db.add(p)
        self.db.commit()
        self.db.refresh(room)
        return room

    def is_participant(
        self,
        chat_room_id: int,
        *,
        zan_user_id: Optional[int] = None,
        zancrew_id: Optional[int] = None,
    ) -> bool:
        q = self.db.query(ChatParticipant).filter(ChatParticipant.chat_room_id == chat_room_id)
        if zan_user_id is not None:
            q = q.filter(ChatParticipant.participant_type == "zan_user", ChatParticipant.zan_user_id == zan_user_id)
        elif zancrew_id is not None:
            q = q.filter(ChatParticipant.participant_type == "zan_crew", ChatParticipant.zancrew_id == zancrew_id)
        else:
            return False
        return q.first() is not None


class ChatMessageRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        chat_room_id: int,
        sender_type: str,
        content: str,
        *,
        sender_zan_user_id: Optional[int] = None,
        sender_zancrew_id: Optional[int] = None,
    ) -> ChatMessage:
        msg = ChatMessage(
            chat_room_id=chat_room_id,
            sender_type=sender_type,
            sender_zan_user_id=sender_zan_user_id,
            sender_zancrew_id=sender_zancrew_id,
            content=content,
        )
        self.db.add(msg)
        self.db.commit()
        self.db.refresh(msg)
        return msg

    def get_messages_cursor(
        self,
        chat_room_id: int,
        cursor: Optional[str] = None,
        limit: int = 50,
    ) -> tuple[list[ChatMessage], Optional[str], bool]:
        q = (
            self.db.query(ChatMessage)
            .filter(ChatMessage.chat_room_id == chat_room_id)
            .order_by(desc(ChatMessage.created_at), desc(ChatMessage.id))
        )
        if cursor:
            try:
                cursor_id = int(cursor)
                q = q.filter(ChatMessage.id < cursor_id)
            except ValueError:
                pass
        rows = q.limit(limit + 1).all()
        has_more = len(rows) > limit
        messages = rows[:limit]
        next_cursor = str(messages[-1].id) if messages and has_more else None
        return messages, next_cursor, has_more
