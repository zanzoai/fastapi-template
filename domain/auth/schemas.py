from pydantic import BaseModel, Field, field_validator
from typing import Optional

from core.validators import validate_phone_e164


class SendOTPRequest(BaseModel):
    phone: str = Field(..., description="Phone number in E.164 format (e.g., +1234567890)")

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        return validate_phone_e164(v)


class VerifyOTPRequest(BaseModel):
    phone: str = Field(..., description="Phone number in E.164 format (e.g., +1234567890)")
    token: str = Field(..., description="OTP token received via SMS")

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        return validate_phone_e164(v)

class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    user: dict
    expires_in: Optional[int] = None
    token_type: str = "bearer"

class SendOTPResponse(BaseModel):
    message: str
    phone: str

