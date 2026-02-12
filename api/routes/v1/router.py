from fastapi import APIRouter
from api.routes.v1.users import router as user_router
from api.routes.v1.health import router as health_router
from api.routes.v1.blogs import router as blog_router
from api.routes.v1.jobs import router as job_router

router = APIRouter(prefix="/api/v1")

router.include_router(user_router)
router.include_router(health_router)
router.include_router(blog_router)
router.include_router(job_router)
