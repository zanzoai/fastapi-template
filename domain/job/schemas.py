from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class JobCreate(BaseModel):
    user_id: int
    job_description: str
    assigned_amount: int
    job_loc: Optional[str] = None
    job_status: Optional[str] = None

class JobUpdate(BaseModel):
    job_description: Optional[str] = None
    assigned_amount: Optional[int] = None
    job_loc: Optional[str] = None
    job_status: Optional[str] = None

class JobResponse(BaseModel):
    job_id: int
    user_id: int
    job_description: str
    assigned_amount: int
    job_loc: Optional[str] = None
    job_status: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

