from datetime import datetime
from typing import Optional
import re

from pydantic import BaseModel, EmailStr, Field, field_validator


def normalize_indian_phone(phone: str) -> str:
    """
    Normalize an Indian mobile number to E.164 format.

    Accepted examples:
      9876543210
      09876543210
      919876543210
      +919876543210
      +91 9876543210

    Stored/sent format:
      +919876543210
    """
    if phone is None:
        raise ValueError("Mobile number is required.")

    value = str(phone).strip()
    value = re.sub(r"[\s\-().]", "", value)

    # International India format: +91XXXXXXXXXX
    if value.startswith("+91"):
        digits = value[3:]
    elif value.startswith("0091"):
        digits = value[4:]
    elif value.startswith("91") and len(value) == 12:
        digits = value[2:]
    elif value.startswith("0") and len(value) == 11:
        digits = value[1:]
    elif len(value) == 10:
        digits = value
    else:
        raise ValueError("Enter a valid 10-digit Indian mobile number.")

    if not re.fullmatch(r"[6-9]\d{9}", digits):
        raise ValueError("Enter a valid Indian mobile number starting with 6, 7, 8, or 9.")

    return "+91" + digits


class PatientCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    phone: str = Field(min_length=7, max_length=30)

    @field_validator("phone")
    @classmethod
    def normalize_phone(cls, value: str) -> str:
        return normalize_indian_phone(value)


class PatientOut(PatientCreate):
    id: int

    class Config:
        from_attributes = True


class AppointmentCreate(BaseModel):
    patient_id: Optional[int] = None
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    phone: str = Field(min_length=7, max_length=30)
    hospital_id: int
    specialty_id: int
    # When True the booking is created with EMERGENCY priority and inserted at
    # position 1 of the queue. All other waiting patients shift down by one.
    is_emergency: bool = False

    @field_validator("phone")
    @classmethod
    def normalize_phone(cls, value: str) -> str:
        return normalize_indian_phone(value)


class AppointmentOut(BaseModel):
    id: int
    token_number: str
    hospital_id: int
    specialty_id: int
    doctor_id: int
    status: str
    priority: str
    queue_position: int
    waiting_minutes: int
    appointment_time: datetime
    estimated_arrival_time: datetime
    notification_email: bool
    notification_sms: bool


class EmergencyCreate(BaseModel):
    hospital_id: int
    specialty_id: int
    name: str = "Emergency Patient"
    minutes: int = Field(default=20, ge=1, le=240)


class CancelResponse(BaseModel):
    success: bool
    message: str
    appointment_id: int
