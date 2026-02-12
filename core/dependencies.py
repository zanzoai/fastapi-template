from fastapi import Depends
from infrastructure.db.session import SessionLocal
from domain.user.repository import UserRepository
from domain.user.service import UserService
from domain.blog.repository import BlogRepository
from domain.blog.service import BlogService
from domain.job.repository import JobRepository
from domain.job.service import JobService

def get_db():
    db = SessionLocal()
    try:
        yield db
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
    return JobService(repo)
