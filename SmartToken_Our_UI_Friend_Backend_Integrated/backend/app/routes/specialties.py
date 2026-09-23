from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Specialty

router = APIRouter()

@router.get("")
def list_specialties(db: Session = Depends(get_db)):
    return db.query(Specialty).order_by(Specialty.name.asc()).all()
