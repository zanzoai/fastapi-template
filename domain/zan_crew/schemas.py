from pydantic import BaseModel, ConfigDict, field_validator
from datetime import datetime, date
from typing import Optional
from domain.zan_user.schemas import ZanUserResponse
from core.validators import validate_phone_e164


class ZanCrewCreate(BaseModel):
    phone: str
    pan_id: Optional[str] = None
    adhar_id: Optional[str] = None
    birth_date: Optional[date] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    martial_status: Optional[str] = None
    status: Optional[str] = None
    radius_km: Optional[float] = None
    work_hours: Optional[str] = None
    kyc_verified: Optional[str] = None
    is_online: Optional[str] = None
    payout_beneficiary_id: Optional[str] = None
    bank_account: Optional[str] = None
    ifsc_code: Optional[str] = None
    home_lat: Optional[str] = None
    home_lng: Optional[str] = None
    idfy_refs: Optional[str] = None
    pan_name: Optional[str] = None
    pan_number_last4: Optional[str] = None
    aadhaar_verified: Optional[str] = None
    aadhaar_last4: Optional[str] = None
    aadhar_city: Optional[str] = None
    face_match_score: Optional[float] = None
    face_verified: Optional[str] = None
    selfie_img_url: Optional[str] = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        return validate_phone_e164(v)


class ZanCrewUpdate(BaseModel):
    phone: Optional[str] = None
    pan_id: Optional[str] = None
    adhar_id: Optional[str] = None
    birth_date: Optional[date] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    martial_status: Optional[str] = None
    status: Optional[str] = None
    radius_km: Optional[float] = None
    work_hours: Optional[str] = None
    kyc_verified: Optional[str] = None
    is_online: Optional[str] = None
    payout_beneficiary_id: Optional[str] = None
    bank_account: Optional[str] = None
    ifsc_code: Optional[str] = None
    home_lat: Optional[str] = None
    home_lng: Optional[str] = None
    idfy_refs: Optional[str] = None
    pan_name: Optional[str] = None
    pan_number_last4: Optional[str] = None
    aadhaar_verified: Optional[str] = None
    aadhaar_last4: Optional[str] = None
    aadhar_city: Optional[str] = None
    face_match_score: Optional[float] = None
    face_verified: Optional[str] = None
    selfie_img_url: Optional[str] = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return validate_phone_e164(v)


class ZanCrewResponse(BaseModel):
    zancrew_id: int
    phone: str
    pan_id: Optional[str] = None
    adhar_id: Optional[str] = None
    birth_date: Optional[datetime] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    martial_status: Optional[str] = None
    zan_user_id: int
    status: Optional[str] = None
    radius_km: Optional[float] = None
    work_hours: Optional[str] = None
    kyc_verified: Optional[str] = None
    is_online: Optional[str] = None
    payout_beneficiary_id: Optional[str] = None
    bank_account: Optional[str] = None
    ifsc_code: Optional[str] = None
    home_lat: Optional[str] = None
    home_lng: Optional[str] = None
    idfy_refs: Optional[str] = None
    pan_name: Optional[str] = None
    pan_number_last4: Optional[str] = None
    aadhaar_verified: Optional[str] = None
    aadhaar_last4: Optional[str] = None
    aadhar_city: Optional[str] = None
    face_match_score: Optional[float] = None
    face_verified: Optional[str] = None
    selfie_img_url: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ZanCrewWithUserResponse(BaseModel):
    zancrew_id: int
    phone: str
    pan_id: Optional[str] = None
    adhar_id: Optional[str] = None
    birth_date: Optional[datetime] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    martial_status: Optional[str] = None
    zan_user_id: int
    status: Optional[str] = None
    radius_km: Optional[float] = None
    work_hours: Optional[str] = None
    kyc_verified: Optional[str] = None
    is_online: Optional[str] = None
    payout_beneficiary_id: Optional[str] = None
    bank_account: Optional[str] = None
    ifsc_code: Optional[str] = None
    home_lat: Optional[str] = None
    home_lng: Optional[str] = None
    idfy_refs: Optional[str] = None
    pan_name: Optional[str] = None
    pan_number_last4: Optional[str] = None
    aadhaar_verified: Optional[str] = None
    aadhaar_last4: Optional[str] = None
    aadhar_city: Optional[str] = None
    face_match_score: Optional[float] = None
    face_verified: Optional[str] = None
    selfie_img_url: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    zan_user: Optional[ZanUserResponse] = None

    model_config = ConfigDict(from_attributes=True)


