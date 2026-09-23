from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from ..database import get_db
from ..models import Appointment, Doctor, Patient, Hospital
from ..schemas import EmergencyCreate
from ..services.prediction_service import recalculate_queue
from ..services.notification_service import notify_patient

router = APIRouter()


def _row(a):
    return {
        "id": a.id,
        "token_number": a.token_number,
        "queue_position": a.queue_position,
        "status": a.status,
        "priority": a.priority,
        "waiting_minutes": a.waiting_minutes,
        "appointment_time": a.appointment_time,
        "estimated_arrival_time": a.estimated_arrival_time,
    }


@router.get("/hospital/{hospital_id}/specialty/{specialty_id}")
def live_queue(hospital_id: int, specialty_id: int, db: Session = Depends(get_db)):
    from ..services.prediction_service import _priority_order
    return [
        _row(a)
        for a in db.query(Appointment)
        .filter(
            Appointment.hospital_id == hospital_id,
            Appointment.specialty_id == specialty_id,
            Appointment.status == "WAITING",
        )
        .order_by(_priority_order, Appointment.created_at.asc())
        .all()
    ]


@router.get("/appointment/{appointment_id}")
def live_appointment_status(appointment_id: int, db: Session = Depends(get_db)):
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(404, "Appointment not found")
    return _row(appointment)


@router.post("/emergency")
def insert_emergency(payload: EmergencyCreate, db: Session = Depends(get_db)):
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
        raise HTTPException(409, "No available doctor for this specialty")

    existing_count = db.query(Appointment).filter(
        Appointment.hospital_id == payload.hospital_id,
        Appointment.specialty_id == payload.specialty_id,
    ).count()

    emergency_patient = Patient(
        name=payload.name or "Walk-in Emergency",
        email="emergency@local.test",
        phone="0000000000",
    )
    db.add(emergency_patient)
    db.flush()

    now = datetime.now()
    emergency = Appointment(
        token_number=f"E-{existing_count + 1:03d}",
        patient_id=emergency_patient.id,
        hospital_id=payload.hospital_id,
        specialty_id=payload.specialty_id,
        doctor_id=doctor.id,
        status="WAITING",
        priority="EMERGENCY",
        queue_position=1,
        waiting_minutes=0,
        appointment_time=now,
        estimated_arrival_time=now,
        manual_offset_minutes=0,
    )
    db.add(emergency)
    db.commit()

    # The admin-provided emergency duration is added to every normal patient
    # currently waiting in this department, because the emergency consumes doctor time.
    normal = db.query(Appointment).filter(
        Appointment.hospital_id == payload.hospital_id,
        Appointment.specialty_id == payload.specialty_id,
        Appointment.status == "WAITING",
        Appointment.priority == "NORMAL",
    ).all()
    for a in normal:
        a.manual_offset_minutes = (a.manual_offset_minutes or 0) + max(1, payload.minutes)

    active = recalculate_queue(db, payload.hospital_id, payload.specialty_id)
    hospital = db.query(Hospital).filter(Hospital.id == payload.hospital_id).first()

    if hospital:
        for a in active:
            if a.id == emergency.id:
                continue
            patient = db.query(Patient).filter(Patient.id == a.patient_id).first()
            if patient:
                notify_patient(patient, a, hospital.name, "UPDATED")

    return {
        "success": True,
        "message": f"Emergency inserted and {payload.minutes}-minute delay re-forecasted.",
        "appointment_id": emergency.id,
        "token_number": emergency.token_number,
    }
