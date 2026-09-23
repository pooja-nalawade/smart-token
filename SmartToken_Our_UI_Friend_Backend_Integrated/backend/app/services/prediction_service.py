from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import case
from ..models import Appointment, Doctor


def _doctor_average(db: Session, hospital_id: int, specialty_id: int):
    doctors = (
        db.query(Doctor)
        .filter(
            Doctor.hospital_id == hospital_id,
            Doctor.specialty_id == specialty_id,
            Doctor.available == True,
        )
        .all()
    )
    count = max(len(doctors), 1)
    avg = round(sum(d.average_consultation_minutes for d in doctors) / count) if doctors else 10
    return count, max(avg, 1)


# Priority ordering: EMERGENCY = 0 (first), NORMAL = 1 (after).
# SQLAlchemy CASE expression so the DB always returns the correct sort
# regardless of string alphabetical order ("NORMAL" > "EMERGENCY" alphabetically
# which was the original bug — emergencies went to the BOTTOM).
_priority_order = case(
    (Appointment.priority == "EMERGENCY", 0),
    else_=1,
)


def calculate_queue_estimate(db: Session, hospital_id: int, specialty_id: int, doctor_id: int):
    active = (
        db.query(Appointment)
        .filter(
            Appointment.hospital_id == hospital_id,
            Appointment.specialty_id == specialty_id,
            Appointment.status == "WAITING",
        )
        .order_by(_priority_order, Appointment.created_at.asc())
        .all()
    )
    _, avg = _doctor_average(db, hospital_id, specialty_id)
    position = len(active) + 1
    waiting = int(round(len(active) * avg))
    now = datetime.now()
    appointment_time = now + timedelta(minutes=waiting)
    estimated_arrival = appointment_time - timedelta(minutes=15)
    return position, waiting, appointment_time, estimated_arrival


def recalculate_queue(db: Session, hospital_id: int, specialty_id: int):
    """
    Re-assign queue_position and waiting_minutes for all WAITING appointments
    in this specialty. EMERGENCY appointments always occupy the front of the
    queue regardless of when they were created.
    """
    active = (
        db.query(Appointment)
        .filter(
            Appointment.hospital_id == hospital_id,
            Appointment.specialty_id == specialty_id,
            Appointment.status == "WAITING",
        )
        .order_by(_priority_order, Appointment.created_at.asc())
        .all()
    )

    doctor_count, avg = _doctor_average(db, hospital_id, specialty_id)
    now = datetime.now()

    for index, appt in enumerate(active):
        base_wait = int(round(index * avg / doctor_count))
        wait = max(0, base_wait + (appt.manual_offset_minutes or 0))
        appt.queue_position = index + 1
        appt.waiting_minutes = wait
        appt.appointment_time = now + timedelta(minutes=wait)
        appt.estimated_arrival_time = appt.appointment_time - timedelta(minutes=15)

    db.commit()
    return active
