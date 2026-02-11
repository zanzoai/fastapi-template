from fastapi import Depends
from infrastructure.db.session import SessionLocal
from domain.user.repository import UserRepository
from domain.user.service import UserService

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_user_service(db=Depends(get_db)):
    repo = UserRepository(db)
    return UserService(repo)
