from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(30), nullable=False)
    # Location/GPS fields intentionally removed. Patient registration is location-free.
    created_at = Column(DateTime, default=datetime.utcnow)


class Specialty(Base):
    __tablename__ = "specialties"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(255), nullable=True)


class Hospital(Base):
    __tablename__ = "hospitals"

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    address = Column(String(300), nullable=False)
    city = Column(String(100), nullable=False)
    phone = Column(String(30), nullable=True)
    active = Column(Boolean, default=True)


class HospitalSpecialty(Base):
    __tablename__ = "hospital_specialties"

    id = Column(Integer, primary_key=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=False)
    specialty_id = Column(Integer, ForeignKey("specialties.id"), nullable=False)


class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=False)
    specialty_id = Column(Integer, ForeignKey("specialties.id"), nullable=False)
    name = Column(String(150), nullable=False)
    average_consultation_minutes = Column(Integer, default=10)
    available = Column(Boolean, default=True)


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True)
    token_number = Column(String(30), nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=False)
    specialty_id = Column(Integer, ForeignKey("specialties.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    status = Column(String(30), default="WAITING")
    priority = Column(String(30), default="NORMAL")
    queue_position = Column(Integer, nullable=False)
    waiting_minutes = Column(Integer, nullable=False)
    appointment_time = Column(DateTime, nullable=False)
    estimated_arrival_time = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    cancelled_at = Column(DateTime, nullable=True)
    served_at = Column(DateTime, nullable=True)
    manual_offset_minutes = Column(Integer, default=0, nullable=False)
    specialty = relationship("Specialty", lazy="joined")
    doctor = relationship("Doctor", lazy="joined")
