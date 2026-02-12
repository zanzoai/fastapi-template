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
        return service.create_job(data.user_id, data.job_description, data.assigned_amount, data.job_loc, data.job_status)
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
    return service.get_jobs_by_user(user_id, skip, limit)

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
        return service.update_job(job_id, data.job_description, data.assigned_amount, data.job_loc, data.job_status)
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

