from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from domain.job.schemas import JobCreate, JobResponse, JobUpdate
from core.dependencies import get_job_service

router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.post("", response_model=JobResponse, status_code=201)
def create_job(
    data: JobCreate,
    service = Depends(get_job_service)
):
    try:
        return service.create_job(
            data.user_id,
            data.task_title,
            data.polished_task,
            data.location_address,
            data.latitude,
            data.longitude,
            data.scheduled_at,
            data.duration_hours,
            data.duration_minutes,
            data.estimated_cost_pence,
            data.people_required,
            data.actions,
            data.tags,
            data.payment_mode,
            data.payment_status,
            data.currency,
            data.pickup_adress,
            data.pickup_latitude,
            data.pickup_longitude,
            data.assigned_zancrew_user_id,
            data.short_title,
            data.imp_notes,
            data.bucket,
            data.chat_room_id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("", response_model=List[JobResponse])
def get_all_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    service = Depends(get_job_service)
):
    return service.get_all_jobs(skip, limit)

@router.get("/user/{user_id}", response_model=List[JobResponse])
def get_jobs_by_user(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    service = Depends(get_job_service)
):
    """
    Get all jobs posted by a user from zan_user table.
    
    - **user_id**: The user_id from zan_user table
    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return (1-100)
    
    Returns a list of all jobs posted by the specified user.
    """
    try:
        return service.get_jobs_by_user(user_id, skip, limit)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{job_id}", response_model=JobResponse)
def get_job(
    job_id: int,
    service = Depends(get_job_service)
):
    try:
        return service.get_job(job_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.put("/{job_id}", response_model=JobResponse)
def update_job(
    job_id: int,
    data: JobUpdate,
    service = Depends(get_job_service)
):
    try:
        return service.update_job(
            job_id,
            data.task_title,
            data.polished_task,
            data.location_address,
            data.latitude,
            data.longitude,
            data.scheduled_at,
            data.duration_hours,
            data.duration_minutes,
            data.estimated_cost_pence,
            data.assigned_zancrew_user_id,
            data.short_title,
            data.people_required,
            data.imp_notes,
            data.actions,
            data.tags,
            data.bucket,
            data.payment_mode,
            data.payment_status,
            data.currency,
            data.chat_room_id,
            data.pickup_adress,
            data.pickup_latitude,
            data.pickup_longitude,
            status=data.status,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/{job_id}", status_code=204)
def delete_job(
    job_id: int,
    service = Depends(get_job_service)
):
    try:
        service.delete_job(job_id)
        return None
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
