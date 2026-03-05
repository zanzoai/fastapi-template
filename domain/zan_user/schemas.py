from pydantic import BaseModel, ConfigDict, EmailStr, field_validator
from datetime import datetime
from typing import Optional

from core.validators import validate_phone_e164


class ZanUserCreate(BaseModel):
    phone: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    is_zancrew: Optional[str] = "false"
    zancrew_id: Optional[int] = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        return validate_phone_e164(v)

class ZanUserUpdate(BaseModel):
    phone: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    is_zancrew: Optional[str] = None
    zancrew_id: Optional[int] = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return validate_phone_e164(v)

class ZanUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: int
    phone: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    is_zancrew: Optional[str] = None
    zancrew_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


