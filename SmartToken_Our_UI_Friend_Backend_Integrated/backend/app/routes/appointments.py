from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from ..database import get_db
from ..models import Patient, Hospital, Specialty, Doctor, Appointment
from ..schemas import AppointmentCreate, AppointmentOut
from ..services.prediction_service import calculate_queue_estimate, recalculate_queue
from ..services.notification_service import notify_patient

router = APIRouter()


def next_token_number(db: Session, hospital_id: int, specialty_id: int, is_emergency: bool = False):
    count = (
        db.query(Appointment)
        .filter(
            Appointment.hospital_id == hospital_id,
            Appointment.specialty_id == specialty_id,
        )
        .count()
    )
    prefix = "E" if is_emergency else "T"
    return f"{prefix}-{count + 1:03d}"


def appointment_payload(appointment, email_ok=False, sms_ok=False):
    return {
        "id": appointment.id,
        "token_number": appointment.token_number,
        "hospital_id": appointment.hospital_id,
        "specialty_id": appointment.specialty_id,
        "doctor_id": appointment.doctor_id,
        "status": appointment.status,
        "priority": appointment.priority,
        "queue_position": appointment.queue_position,
        "waiting_minutes": appointment.waiting_minutes,
        "appointment_time": appointment.appointment_time,
        "estimated_arrival_time": appointment.estimated_arrival_time,
        "notification_email": email_ok,
        "notification_sms": sms_ok,
    }


@router.post("", response_model=AppointmentOut)
def create_appointment(payload: AppointmentCreate, db: Session = Depends(get_db)):
    hospital = db.query(Hospital).filter(Hospital.id == payload.hospital_id, Hospital.active == True).first()
    specialty = db.query(Specialty).filter(Specialty.id == payload.specialty_id).first()
    if not hospital:
        raise HTTPException(404, "Hospital not found")
    if not specialty:
        raise HTTPException(404, "Specialty not found")

    # Upsert patient.
    patient = db.query(Patient).filter(Patient.id == payload.patient_id).first() if payload.patient_id else None
    if not patient:
        patient = Patient(
            name=payload.name,
            email=payload.email,
            phone=payload.phone,
        )
        db.add(patient)
        db.flush()
    else:
        patient.name = payload.name
        patient.email = payload.email
        patient.phone = payload.phone

    doctor = (
        db.query(Doctor)
        .filter(
            Doctor.hospital_id == payload.hospital_id,
            Doctor.specialty_id == payload.specialty_id,
            Doctor.available == True,
        )
        .order_by(Doctor.id.asc())
        .first()
    )
    if not doctor:
        raise HTTPException(409, "No doctor is currently available for this specialty")

    # For emergency bookings, position and waiting are resolved by recalculate_queue
    # immediately after insert (they'll be set to 1 and 0). For normal bookings
    # we pre-calculate so the response is accurate before recalculate_queue runs.
    priority = "EMERGENCY" if payload.is_emergency else "NORMAL"
    position, waiting, appointment_time, arrival = calculate_queue_estimate(
        db, payload.hospital_id, payload.specialty_id, doctor.id
    )

    # Emergency patients jump straight to position 1 in waiting/time estimates.
    if payload.is_emergency:
        position = 1
        waiting = 0
        now = datetime.now()
        appointment_time = now
        arrival = now

    appointment = Appointment(
        token_number=next_token_number(db, payload.hospital_id, payload.specialty_id, payload.is_emergency),
        patient_id=patient.id,
        hospital_id=payload.hospital_id,
        specialty_id=payload.specialty_id,
        doctor_id=doctor.id,
        status="WAITING",
        priority=priority,
        queue_position=position,
        waiting_minutes=waiting,
        appointment_time=appointment_time,
        estimated_arrival_time=arrival,
        manual_offset_minutes=0,
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)

    # Recalculate the full queue — this enforces correct ordering for everyone.
    active = recalculate_queue(db, appointment.hospital_id, appointment.specialty_id)
    db.refresh(appointment)

    # Notify the newly booked patient.
    event = "BOOKED"
    email_ok, sms_ok = notify_patient(patient, appointment, hospital.name, event)

    # Notify every other waiting patient whose position/ETA changed.
    for other in active:
        if other.id == appointment.id:
            continue
        other_patient = db.query(Patient).filter(Patient.id == other.patient_id).first()
        if other_patient:
            notify_patient(other_patient, other, hospital.name, "UPDATED")

    return appointment_payload(appointment, email_ok, sms_ok)


@router.get("/{appointment_id}", response_model=AppointmentOut)
def get_appointment(appointment_id: int, db: Session = Depends(get_db)):
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(404, "Appointment not found")
    return appointment_payload(appointment)


@router.post("/{appointment_id}/cancel")
def cancel_appointment(appointment_id: int, db: Session = Depends(get_db)):
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(404, "Appointment not found")
    if appointment.status != "WAITING":
        raise HTTPException(409, f"Appointment cannot be cancelled from '{appointment.status}' state")

    patient = db.query(Patient).filter(Patient.id == appointment.patient_id).first()
    hospital = db.query(Hospital).filter(Hospital.id == appointment.hospital_id).first()
    specialty_id = appointment.specialty_id
    hospital_id = appointment.hospital_id

    appointment.status = "CANCELLED"
    appointment.cancelled_at = datetime.now()
    db.commit()

    if patient and hospital:
        notify_patient(patient, appointment, hospital.name, "CANCELLED")

    active = recalculate_queue(db, hospital_id, specialty_id)

    if hospital:
        for other in active:
            other_patient = db.query(Patient).filter(Patient.id == other.patient_id).first()
            if other_patient:
                notify_patient(other_patient, other, hospital.name, "UPDATED")

    return {
        "success": True,
        "message": "Appointment cancelled and queue recalculated",
        "appointment_id": appointment.id,
    }
