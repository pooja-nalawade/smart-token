from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Appointment, Hospital, Specialty, Patient, Doctor
from ..services.prediction_service import recalculate_queue
from ..services.notification_service import notify_patient, get_sms_diagnostics

router = APIRouter()


def queue_row(db: Session, a: Appointment) -> dict:
    patient = db.query(Patient).filter(Patient.id == a.patient_id).first()
    doctor = db.query(Doctor).filter(Doctor.id == a.doctor_id).first()
    return {
        "id": a.id,
        "token_number": a.token_number,
        "patient_name": patient.name if patient else "Unknown",
        "patient_phone": patient.phone if patient else "",
        "patient_email": patient.email if patient else "",
        "hospital_id": a.hospital_id,
        "specialty_id": a.specialty_id,
        "doctor_id": a.doctor_id,
        "doctor_name": doctor.name if doctor else "OPD Doctor",
        "status": a.status,
        "priority": a.priority,
        "queue_position": a.queue_position,
        "waiting_minutes": a.waiting_minutes,
        "appointment_time": a.appointment_time,
        "estimated_arrival_time": a.estimated_arrival_time,
    }


def _notify_queue(db, hospital_id, specialty_id, event="UPDATED"):
    hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    active = recalculate_queue(db, hospital_id, specialty_id)
    if hospital:
        for a in active:
            patient = db.query(Patient).filter(Patient.id == a.patient_id).first()
            if patient and patient.email != "emergency@local.test":
                notify_patient(patient, a, hospital.name, event)
    return active


@router.get("/dashboard")
def dashboard(specialty_id: int | None = None, db: Session = Depends(get_db)):
    from ..services.prediction_service import _priority_order
    specialties = db.query(Specialty).order_by(Specialty.id.asc()).all()
    hospital = db.query(Hospital).filter(Hospital.active == True).order_by(Hospital.id.asc()).first()

    query = db.query(Appointment).filter(Appointment.status == "WAITING")
    if hospital:
        query = query.filter(Appointment.hospital_id == hospital.id)
    if specialty_id:
        query = query.filter(Appointment.specialty_id == specialty_id)

    appointments = query.order_by(
        Appointment.specialty_id.asc(), _priority_order, Appointment.queue_position.asc()
    ).all()

    return {
        "hospital": {"id": hospital.id, "name": hospital.name} if hospital else None,
        "specialties": [{"id": s.id, "name": s.name} for s in specialties],
        "appointments": [queue_row(db, a) for a in appointments],
    }


@router.get("/stats")
def stats(db: Session = Depends(get_db)):
    hospital = db.query(Hospital).filter(Hospital.active == True).order_by(Hospital.id.asc()).first()
    if not hospital:
        return {"waiting": 0, "emergency_waiting": 0, "normal_waiting": 0, "served_today": 0, "eta_updates": 0}

    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    q = db.query(Appointment).filter(Appointment.hospital_id == hospital.id, Appointment.status == "WAITING")
    served = db.query(Appointment).filter(
        Appointment.hospital_id == hospital.id,
        Appointment.status == "SERVED",
        Appointment.served_at >= today
    ).count()
    return {
        "waiting": q.count(),
        "emergency_waiting": q.filter(Appointment.priority == "EMERGENCY").count(),
        "normal_waiting": q.filter(Appointment.priority == "NORMAL").count(),
        "served_today": served,
    }


@router.get("/sms-diagnostics")
def sms_diagnostics():
    return get_sms_diagnostics()


@router.post("/appointments/{appointment_id}/cancel")
def admin_cancel(appointment_id: int, db: Session = Depends(get_db)):
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment or appointment.status != "WAITING":
        raise HTTPException(404, "Waiting appointment not found")

    patient = db.query(Patient).filter(Patient.id == appointment.patient_id).first()
    hospital = db.query(Hospital).filter(Hospital.id == appointment.hospital_id).first()
    appointment.status = "CANCELLED"
    appointment.cancelled_at = datetime.now()
    db.commit()

    if patient and hospital:
        notify_patient(patient, appointment, hospital.name, "CANCELLED")

    active = _notify_queue(db, appointment.hospital_id, appointment.specialty_id, "UPDATED")
    return {"success": True, "queue": [queue_row(db, a) for a in active]}


@router.post("/appointments/{appointment_id}/serve")
def serve_appointment(appointment_id: int, db: Session = Depends(get_db)):
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment or appointment.status != "WAITING":
        raise HTTPException(404, "Waiting appointment not found")
    patient = db.query(Patient).filter(Patient.id == appointment.patient_id).first()
    hospital = db.query(Hospital).filter(Hospital.id == appointment.hospital_id).first()
    appointment.status = "SERVED"
    appointment.served_at = datetime.now()
    db.commit()
    if patient and hospital:
        notify_patient(patient, appointment, hospital.name, "SERVED")
    active = _notify_queue(db, appointment.hospital_id, appointment.specialty_id, "UPDATED")
    return {"success": True, "queue": [queue_row(db, a) for a in active]}


@router.post("/appointments/{appointment_id}/shift")
def shift_appointment(appointment_id: int, minutes: int, db: Session = Depends(get_db)):
    if minutes == 0 or minutes < -120 or minutes > 120:
        raise HTTPException(400, "Shift must be between -120 and +120 minutes and not zero.")
    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id, Appointment.status == "WAITING"
    ).first()
    if not appointment:
        raise HTTPException(404, "Waiting appointment not found")
    appointment.manual_offset_minutes = (appointment.manual_offset_minutes or 0) + minutes
    db.commit()
    active = _notify_queue(db, appointment.hospital_id, appointment.specialty_id, "UPDATED")
    return {"success": True, "queue": [queue_row(db, a) for a in active]}


@router.post("/appointments/{appointment_id}/priority")
def toggle_priority(appointment_id: int, db: Session = Depends(get_db)):
    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id, Appointment.status == "WAITING"
    ).first()
    if not appointment:
        raise HTTPException(404, "Waiting appointment not found")
    appointment.priority = "EMERGENCY" if appointment.priority == "NORMAL" else "NORMAL"
    db.commit()
    active = _notify_queue(db, appointment.hospital_id, appointment.specialty_id, "UPDATED")
    return {"success": True, "queue": [queue_row(db, a) for a in active]}


@router.post("/doctor-unavailable")
def doctor_unavailable(
    hospital_id: int,
    specialty_id: int,
    alternative_doctor: str,
    db: Session = Depends(get_db),
):
    current = (
        db.query(Doctor)
        .filter(
            Doctor.hospital_id == hospital_id,
            Doctor.specialty_id == specialty_id,
            Doctor.available == True,
        )
        .order_by(Doctor.id.asc())
        .first()
    )
    if not current:
        raise HTTPException(404, "No currently available doctor found.")

    alternative = (
        db.query(Doctor)
        .filter(
            Doctor.hospital_id == hospital_id,
            Doctor.specialty_id == specialty_id,
            Doctor.id != current.id,
            Doctor.name == alternative_doctor,
        )
        .first()
    )
    if not alternative:
        alternative = (
            db.query(Doctor)
            .filter(
                Doctor.hospital_id == hospital_id,
                Doctor.specialty_id == specialty_id,
                Doctor.id != current.id,
            )
            .order_by(Doctor.id.asc())
            .first()
        )
    if not alternative:
        raise HTTPException(409, "No alternative doctor is configured for this department.")

    current.available = False
    alternative.available = True

    active = db.query(Appointment).filter(
        Appointment.hospital_id == hospital_id,
        Appointment.specialty_id == specialty_id,
        Appointment.status == "WAITING",
    ).all()
    for a in active:
        a.doctor_id = alternative.id
    db.commit()

    active = recalculate_queue(db, hospital_id, specialty_id)
    hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()

    if hospital:
        for a in active:
            patient = db.query(Patient).filter(Patient.id == a.patient_id).first()
            if patient and patient.email != "emergency@local.test":
                notify_patient(patient, a, hospital.name, "DOCTOR_CHANGED")

    return {
        "success": True,
        "previous_doctor": current.name,
        "new_doctor": alternative.name,
        "queue": [queue_row(db, a) for a in active],
    }


@router.post("/reforecast-all")
def reforecast_all(db: Session = Depends(get_db)):
    hospital = db.query(Hospital).filter(Hospital.active == True).order_by(Hospital.id.asc()).first()
    if not hospital:
        return {"success": True, "updated": 0}
    specialties = db.query(Specialty).all()
    updated = 0
    for s in specialties:
        active = _notify_queue(db, hospital.id, s.id, "UPDATED")
        updated += len(active)
    return {"success": True, "updated": updated}
