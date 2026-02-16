from fastapi import Depends, Header, HTTPException

from infrastructure.db.session import SessionLocal
from domain.user.repository import UserRepository
from domain.user.service import UserService
from domain.blog.repository import BlogRepository
from domain.blog.service import BlogService
from domain.job.repository import JobRepository
from domain.job.service import JobService
from domain.zan_user.repository import ZanUserRepository
from domain.zan_user.service import ZanUserService
from domain.zan_crew.repository import ZanCrewRepository
from domain.zan_crew.service import ZanCrewService
from domain.chat.repository import ChatRoomRepository, ChatMessageRepository
from domain.chat.service import ChatService, ChatActor

def get_db():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def get_user_service(db=Depends(get_db)):
    repo = UserRepository(db)
    return UserService(repo)

def get_blog_service(db=Depends(get_db)):
    repo = BlogRepository(db)
    return BlogService(repo)

def get_job_service(db=Depends(get_db)):
    repo = JobRepository(db)
    zan_user_repo = ZanUserRepository(db)
    chat_room_repo = ChatRoomRepository(db)
    return JobService(repo, zan_user_repo, chat_room_repo)

def get_zan_user_service(db=Depends(get_db)):
    repo = ZanUserRepository(db)
    zan_crew_repo = ZanCrewRepository(db)
    return ZanUserService(repo, zan_crew_repo)

def get_zan_crew_service(db=Depends(get_db)):
    zan_crew_repo = ZanCrewRepository(db)
    zan_user_repo = ZanUserRepository(db)
    return ZanCrewService(zan_crew_repo, zan_user_repo)


# --- Chat: actor from headers (replace with JWT + zan_user/zan_crew lookup in production) ---
def get_chat_actor(
    x_zan_user_id: int | None = Header(None, alias="X-Zan-User-Id"),
    x_zan_actor_type: str | None = Header(None, alias="X-Zan-Actor-Type"),
    x_zancrew_id: int | None = Header(None, alias="X-Zancrew-Id"),
) -> ChatActor:
    """Resolve current chat actor. Production: decode JWT and resolve zan_user/zan_crew from DB."""
    if x_zan_actor_type == "zan_user" and x_zan_user_id is not None:
        return ChatActor(participant_type="zan_user", zan_user_id=x_zan_user_id, zancrew_id=None)
    if x_zan_actor_type == "zan_crew" and x_zancrew_id is not None:
        return ChatActor(participant_type="zan_crew", zan_user_id=None, zancrew_id=x_zancrew_id)
    raise HTTPException(
        status_code=401,
        detail="Chat requires identity headers: X-Zan-User-Id + X-Zan-Actor-Type=zan_user, or X-Zancrew-Id + X-Zan-Actor-Type=zan_crew",
    )


def get_chat_service(db=Depends(get_db)):
    room_repo = ChatRoomRepository(db)
    message_repo = ChatMessageRepository(db)
    return ChatService(room_repo, message_repo, db)
