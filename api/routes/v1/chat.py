from fastapi import APIRouter, Depends, HTTPException, Query

from core.dependencies import get_db, get_chat_actor, get_chat_service
from domain.chat.schemas import ChatRoomResponse, ChatMessageCreate, ChatMessageResponse, ChatMessagesPage
from domain.chat.service import ChatService, ChatActor
from domain.job.repository import JobRepository
from infrastructure.db.models import Job

router = APIRouter(prefix="/chat", tags=["Chat"])


def _get_job_or_404(db, job_id: int) -> Job:
    job = JobRepository(db).get_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.get("/jobs/{job_id}/room", response_model=ChatRoomResponse)
def get_chat_room_for_job(
    job_id: int,
    db=Depends(get_db),
    chat_service: ChatService = Depends(get_chat_service),
    actor: ChatActor = Depends(get_chat_actor),
):
    """
    Get the chat room for a job. Only available when the job is assigned.
    Only the task owner (zan_user) or assigned crew (zan_crew) can access.
    Creates the room if it does not exist yet (e.g. first access after assignment).
    """
    job = _get_job_or_404(db, job_id)
    room_response = chat_service.get_or_create_room_for_job(job)
    if not room_response:
        raise HTTPException(
            status_code=400,
            detail="Chat is only available when the job is assigned to a crew member.",
        )
    # Re-check actor is participant (get_or_create does not enforce; we enforce here)
    room = chat_service.room_repo.get_by_id(room_response.id)
    if not chat_service.room_repo.is_participant(
        room.id,
        zan_user_id=actor.zan_user_id,
        zancrew_id=actor.zancrew_id,
    ):
        raise HTTPException(status_code=403, detail="You are not a participant in this chat.")
    return room_response


@router.get("/rooms/{chat_room_id}/messages", response_model=ChatMessagesPage)
def get_chat_messages(
    chat_room_id: int,
    cursor: str | None = Query(None, description="Cursor for next page (message id)"),
    limit: int = Query(50, ge=1, le=100),
    db=Depends(get_db),
    chat_service: ChatService = Depends(get_chat_service),
    actor: ChatActor = Depends(get_chat_actor),
):
    """
    List messages in a chat room with cursor-based pagination.
    Only participants can read. Order: newest first; use next_cursor for older messages.
    """
    page = chat_service.get_messages(chat_room_id, actor, cursor=cursor, limit=limit)
    if page is None:
        raise HTTPException(status_code=403, detail="You are not a participant in this chat.")
    return page


@router.post("/rooms/{chat_room_id}/messages", response_model=ChatMessageResponse, status_code=201)
def send_chat_message(
    chat_room_id: int,
    body: ChatMessageCreate,
    db=Depends(get_db),
    chat_service: ChatService = Depends(get_chat_service),
    actor: ChatActor = Depends(get_chat_actor),
):
    """
    Send a message in a chat room. Only participants can send.
    Fails with 403 if the room is read-only (e.g. job closed).
    """
    room = chat_service.room_repo.get_by_id(chat_room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Chat room not found.")
    msg = chat_service.send_message(
        chat_room_id,
        actor,
        body.content,
        room_read_only=room.is_read_only,
    )
    if msg is None:
        if not chat_service.room_repo.is_participant(
            chat_room_id,
            zan_user_id=actor.zan_user_id,
            zancrew_id=actor.zancrew_id,
        ):
            raise HTTPException(status_code=403, detail="You are not a participant in this chat.")
        raise HTTPException(
            status_code=403,
            detail="This chat is read-only (e.g. job is closed).",
        )
    return msg
