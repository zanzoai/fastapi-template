from typing import Optional

from infrastructure.db.models import Job
from domain.chat.schemas import ChatRoomResponse, ChatMessageResponse, ChatMessagesPage
from domain.chat.repository import ChatRoomRepository, ChatMessageRepository


class ChatActor:
    """Current requester: either zan_user or zan_crew. Enforced by auth layer."""

    def __init__(
        self,
        participant_type: str,
        zan_user_id: Optional[int] = None,
        zancrew_id: Optional[int] = None,
    ):
        assert participant_type in ("zan_user", "zan_crew")
        self.participant_type = participant_type
        self.zan_user_id = zan_user_id
        self.zancrew_id = zancrew_id


class ChatService:
    def __init__(
        self,
        room_repo: ChatRoomRepository,
        message_repo: ChatMessageRepository,
        db,
    ):
        self.room_repo = room_repo
        self.message_repo = message_repo
        self.db = db

    def get_or_create_room_for_job(self, job: Job) -> Optional[ChatRoomResponse]:
        """Returns chat room for job if job is assigned; else None. Creates room if missing."""
        if not job.assigned_zancrew_user_id:
            return None
        room = self.room_repo.get_by_job_id(job.job_id)
        if room:
            return ChatRoomResponse.model_validate(room)
        room = self.room_repo.create_for_job(
            job_id=job.job_id,
            zan_user_id=job.user_id,
            zancrew_id=job.assigned_zancrew_user_id,
        )
        return ChatRoomResponse.model_validate(room)

    def get_room_for_job(self, job_id: int, actor: ChatActor) -> Optional[ChatRoomResponse]:
        """Returns chat room for job iff job is assigned and actor is a participant."""
        room = self.room_repo.get_by_job_id(job_id)
        if not room:
            return None
        if not self.room_repo.is_participant(
            room.id,
            zan_user_id=actor.zan_user_id,
            zancrew_id=actor.zancrew_id,
        ):
            return None
        return ChatRoomResponse.model_validate(room)

    def get_messages(
        self,
        chat_room_id: int,
        actor: ChatActor,
        cursor: Optional[str] = None,
        limit: int = 50,
    ) -> Optional[ChatMessagesPage]:
        if not self.room_repo.is_participant(
            chat_room_id,
            zan_user_id=actor.zan_user_id,
            zancrew_id=actor.zancrew_id,
        ):
            return None
        messages, next_cursor, has_more = self.message_repo.get_messages_cursor(
            chat_room_id, cursor=cursor, limit=min(limit, 100)
        )
        return ChatMessagesPage(
            messages=[ChatMessageResponse.model_validate(m) for m in messages],
            next_cursor=next_cursor,
            has_more=has_more,
        )

    def send_message(
        self,
        chat_room_id: int,
        actor: ChatActor,
        content: str,
        room_read_only: bool,
    ) -> Optional[ChatMessageResponse]:
        if room_read_only:
            return None
        if not self.room_repo.is_participant(
            chat_room_id,
            zan_user_id=actor.zan_user_id,
            zancrew_id=actor.zancrew_id,
        ):
            return None
        if actor.participant_type not in ("zan_user", "zan_crew"):
            return None
        msg = self.message_repo.create(
            chat_room_id=chat_room_id,
            sender_type=actor.participant_type,
            content=content.strip(),
            sender_zan_user_id=actor.zan_user_id,
            sender_zancrew_id=actor.zancrew_id,
        )
        return ChatMessageResponse.model_validate(msg)
