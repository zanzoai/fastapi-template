from fastapi import APIRouter, Depends, HTTPException
from domain.user.schemas import UserCreate, UserResponse
from core.dependencies import get_user_service

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("", response_model="schemas.UserResponse")
def create_user(
    data: UserCreate,
    service = Depends(get_user_service)
):
    try:
        return service.create_user(data.email)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
