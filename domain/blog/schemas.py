from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class BlogCreate(BaseModel):
    title: str
    content: str
    author_id: int

class BlogUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

class BlogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    content: str
    author_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

