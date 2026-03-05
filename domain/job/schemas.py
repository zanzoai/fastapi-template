from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime, date
from typing import Optional

class JobCreate(BaseModel):
    user_id: int
    task_title: str
    polished_task: str
    location_address: str
    latitude: str
    longitude: str
    scheduled_at: datetime
    duration_hours: int
    duration_minutes: int
    estimated_cost_pence: int
    assigned_zancrew_user_id: Optional[int] = None
    short_title: Optional[str] = None
    people_required: int
    imp_notes: Optional[str] = None
    actions: str
    tags: str
    bucket: Optional[str] = None
    payment_mode: str
    payment_status: str
    currency: str
    chat_room_id: Optional[str] = None
    pickup_adress: str
    pickup_latitude: str
    pickup_longitude: str

class JobUpdate(BaseModel):
    status: Optional[str] = None  # open | in_progress | closed
    task_title: Optional[str] = None
    polished_task: Optional[str] = None
    location_address: Optional[str] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    duration_hours: Optional[int] = None
    duration_minutes: Optional[int] = None
    estimated_cost_pence: Optional[int] = None
    assigned_zancrew_user_id: Optional[int] = None
    short_title: Optional[str] = None
    people_required: Optional[int] = None
    imp_notes: Optional[str] = None
    actions: Optional[str] = None
    tags: Optional[str] = None
    bucket: Optional[str] = None
    payment_mode: Optional[str] = None
    payment_status: Optional[str] = None
    currency: Optional[str] = None
    chat_room_id: Optional[str] = None
    pickup_adress: Optional[str] = None
    pickup_latitude: Optional[str] = None
    pickup_longitude: Optional[str] = None

class JobResponse(BaseModel):
    job_id: int
    user_id: int
    status: Optional[str] = None
    task_title: str
    polished_task: str
    location_address: str
    latitude: str
    longitude: str
    scheduled_at: datetime
    duration_hours: int
    duration_minutes: int
    estimated_cost_pence: int
    assigned_zancrew_user_id: Optional[int] = None
    short_title: Optional[str] = None
    people_required: int
    imp_notes: Optional[str] = None
    actions: str
    tags: str
    bucket: Optional[str] = None
    payment_mode: str
    payment_status: str
    currency: str
    chat_room_id: Optional[str] = None
    pickup_adress: str
    pickup_latitude: str
    pickup_longitude: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

