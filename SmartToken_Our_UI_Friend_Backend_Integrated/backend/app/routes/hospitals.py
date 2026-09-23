from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Hospital, HospitalSpecialty, Doctor

router = APIRouter()


@router.get("/search")
def search_hospitals(
    specialty_id: int,
    q: str = Query("", max_length=100),
    db: Session = Depends(get_db),
):
    """Return hospitals for a specialty. No GPS/location permission is used."""
    query = (
        db.query(Hospital)
        .join(HospitalSpecialty, HospitalSpecialty.hospital_id == Hospital.id)
        .filter(
            Hospital.active == True,
            HospitalSpecialty.specialty_id == specialty_id,
        )
    )

    if q.strip():
        term = f"%{q.strip()}%"
        query = query.filter(
            (Hospital.name.ilike(term))
            | (Hospital.address.ilike(term))
            | (Hospital.city.ilike(term))
        )

    hospitals = query.distinct().all()
    results = []

    for hospital in hospitals:
        doctor_count = (
            db.query(Doctor)
            .filter(
                Doctor.hospital_id == hospital.id,
                Doctor.specialty_id == specialty_id,
                Doctor.available == True,
            )
            .count()
        )

        results.append({
            "id": hospital.id,
            "name": hospital.name,
            "address": hospital.address,
            "city": hospital.city,
            "phone": hospital.phone,
            "available_doctors": doctor_count,
        })

    return sorted(results, key=lambda x: x["name"].lower())
