from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from domain.zan_user.schemas import ZanUserCreate, ZanUserResponse, ZanUserUpdate
from core.dependencies import get_zan_user_service

router = APIRouter(prefix="/zan-users", tags=["ZanUsers"])

@router.post("", response_model=ZanUserResponse, status_code=201)
def create_zan_user(
    data: ZanUserCreate,
    service = Depends(get_zan_user_service)
):
    try:
        return service.create_zan_user(
            data.phone,
            data.first_name,
            data.last_name,
            data.email,
            data.address,
            data.is_zancrew,
            data.zancrew_id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("", response_model=List[ZanUserResponse])
def get_all_zan_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    service = Depends(get_zan_user_service)
):
    return service.get_all_zan_users(skip, limit)

# IMPORTANT: More specific routes must come BEFORE the generic /{user_id} route
# FastAPI matches routes in order, so /{user_id} would match /zancrew/1 if defined first
@router.get("/email/{email}", response_model=ZanUserResponse)
def get_zan_user_by_email(
    email: str,
    service = Depends(get_zan_user_service)
):
    try:
        return service.get_zan_user_by_email(email)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/zancrew/{user_id}", response_model=List[ZanUserResponse])
def get_zan_users_by_zancrew(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    service = Depends(get_zan_user_service)
):
    # Get the user by user_id to find their zancrew_id
    try:
        user = service.get_zan_user(user_id)
        if not user.user_id:
            return []
        # Get all users with the same zancrew_id
        users = service.get_zan_users_by_zancrew(user.user_id, skip, limit)
        return list(users) if users is not None else []
    except ValueError:
        # User not found
        return []

@router.get("/{user_id}", response_model=ZanUserResponse)
def get_zan_user(
    user_id: int,
    service = Depends(get_zan_user_service)
):
    try:
        return service.get_zan_user(user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.put("/{user_id}", response_model=ZanUserResponse)
def update_zan_user(
    user_id: int,
    data: ZanUserUpdate,
    service = Depends(get_zan_user_service)
):
    try:
        return service.update_zan_user(
            user_id,
            data.first_name,
            data.last_name,
            data.email,
            data.phone,
            data.address,
            data.is_zancrew,
            data.zancrew_id
        )
    except ValueError as e:
        msg = str(e)
        # 400 for duplicate phone/email, 404 for not found
        if "already exists" in msg.lower():
            raise HTTPException(status_code=400, detail=msg)
        raise HTTPException(status_code=404, detail=msg)

@router.delete("/{user_id}", status_code=204)
def delete_zan_user(
    user_id: int,
    service = Depends(get_zan_user_service)
):
    try:
        service.delete_zan_user(user_id)
        return None
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

