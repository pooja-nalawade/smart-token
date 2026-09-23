from sqlalchemy.orm import Session
from .models import Specialty, Hospital, HospitalSpecialty, Doctor

SPECIALTIES = [
    ("Gynaecology", "Women’s health & reproductive care"),
    ("Physiotherapy", "Movement, rehabilitation & pain care"),
    ("Psychology", "Mental wellbeing & counselling"),
    ("General Medicine", "General health & common conditions"),
    ("Paediatrics", "Healthcare for children"),
    ("Orthopaedics", "Bones, joints & mobility"),
    ("Dermatology", "Skin, hair & nail care"),
    ("ENT", "Ear, nose & throat care"),
]

HOSPITALS = [
    (1,"Shivaji Government Hospital","Dr Babasaheb Ambedkar Road, Dadar East, Mumbai","Mumbai","400014",19.0178,72.8478),
    (2,"Lokmanya Tilak Municipal Hospital","Sion, Mumbai","Mumbai","400022",19.0433,72.8610),
    (3,"Rajawadi Government Hospital","Rajawadi, Ghatkopar East, Mumbai","Mumbai","400077",19.0896,72.9081),
    (4,"Kalyan District Hospital","Kalyan West, Thane District, Maharashtra","Kalyan","421301",19.2437,73.1355),
    (5,"Civil Hospital Thane","Civil Hospital Road, Thane West, Maharashtra","Thane","400601",19.1970,72.9708),
    (6,"K.E.M. Hospital","Acharya Donde Marg, Parel, Mumbai","Mumbai","400012",18.9992,72.8408),
    (7,"B.Y.L. Nair Hospital","Dr Anandrao Nair Marg, Mumbai Central, Mumbai","Mumbai","400008",18.9767,72.8236),
    (8,"Dr. R.N. Cooper Municipal General Hospital","JVPD Scheme, Juhu, Mumbai","Mumbai","400056",19.1075,72.8360),
    (9,"K.B. Bhabha Municipal General Hospital","Waterfield Road, Bandra West, Mumbai","Mumbai","400050",19.0615,72.8332),
    (10,"V.N. Desai Municipal General Hospital","Road No. 11, Golibar, Santacruz East, Mumbai","Mumbai","400055",19.0795,72.8505),
    (11,"Sant Muktabai Municipal General Hospital","S.G. Barve Marg, Ghatkopar West, Mumbai","Mumbai","400084",19.0864,72.9046),
    (12,"K.M.J. Phule Municipal General Hospital","Vikhroli East, Mumbai","Mumbai","400083",19.1114,72.9270),
    (13,"Siddharth Municipal General Hospital","Goregaon West, Mumbai","Mumbai","400104",19.1663,72.8499),
    (14,"Shatabdi Hospital","Kandivali, Mumbai","Mumbai","400067",19.2047,72.8377),
    (15,"Shatabdi Hospital","Govandi East, Mumbai","Mumbai","400043",19.0554,72.9189),
    (16,"S.K. Patil Municipal General Hospital","Malad, Mumbai","Mumbai","400064",19.1872,72.8487),
    (17,"H.B.T. Trauma Care Hospital","Jogeshwari, Mumbai","Mumbai","400102",19.1378,72.8334),
    (18,"K.B. Bhabha Municipal General Hospital","Kurla West, Mumbai","Mumbai","400070",19.0726,72.8826),
    (19,"M.W. Desai Municipal General Hospital","Malad, Mumbai","Mumbai","400064",19.1870,72.8480),
]

# Hospital IDs deliberately match the IDs already used by the unchanged patient UI.
# Each hospital supports the specialties listed in the original frontend.
HOSPITAL_SPECIALTIES = {
    1: set(x[0] for x in SPECIALTIES),
    2: {"Gynaecology","Physiotherapy","General Medicine","Paediatrics","Orthopaedics","ENT"},
    3: {"Gynaecology","Psychology","General Medicine","Paediatrics","Dermatology"},
    4: {"Gynaecology","Physiotherapy","General Medicine","Orthopaedics","ENT"},
    5: {"Gynaecology","Psychology","General Medicine","Paediatrics","Dermatology","ENT"},
    6: set(x[0] for x in SPECIALTIES),
    7: set(x[0] for x in SPECIALTIES),
    8: set(x[0] for x in SPECIALTIES),
    9: set(x[0] for x in SPECIALTIES),
    10:set(x[0] for x in SPECIALTIES),
    11:{"Gynaecology","Psychology","General Medicine","Paediatrics","Dermatology"},
    12:{"Gynaecology","Physiotherapy","General Medicine","Paediatrics","Orthopaedics","ENT"},
    13:{"Gynaecology","Psychology","General Medicine","Paediatrics","Dermatology","ENT"},
    14:{"Gynaecology","Physiotherapy","General Medicine","Paediatrics","Orthopaedics","ENT"},
    15:{"Gynaecology","Psychology","General Medicine","Paediatrics","Dermatology"},
    16:{"Gynaecology","Physiotherapy","General Medicine","Paediatrics","Orthopaedics","ENT"},
    17:{"General Medicine","Orthopaedics","ENT"},
    18:{"Gynaecology","Physiotherapy","General Medicine","Paediatrics","Orthopaedics","ENT"},
    19:{"Gynaecology","General Medicine","Paediatrics","Dermatology"},
}

DOCTOR_NAMES = {
    "Gynaecology": ("Dr. Meera Joshi", "Dr. Aisha Desai"),
    "Physiotherapy": ("Dr. Arjun Rao", "Dr. Rahul Mehta"),
    "Psychology": ("Dr. Nidhi Mehta", "Dr. Kavya Shah"),
    "General Medicine": ("Dr. Vikram Shah", "Dr. Neel Deshmukh"),
    "Paediatrics": ("Dr. Ananya Kulkarni", "Dr. Rohan Patil"),
    "Orthopaedics": ("Dr. Sameer Joshi", "Dr. Priya Shah"),
    "Dermatology": ("Dr. Riya Mehta", "Dr. Kunal Rao"),
    "ENT": ("Dr. Amit Desai", "Dr. Sneha Kulkarni"),
}

def seed_database(db: Session):
    # Exact specialty names are aligned with the existing SmartToken frontend.
    for idx, (name, description) in enumerate(SPECIALTIES, start=1):
        s = db.query(Specialty).filter(Specialty.id == idx).first()
        if not s:
            s = Specialty(id=idx, name=name, description=description)
            db.add(s)
        else:
            s.name, s.description = name, description
    db.flush()

    for hid, name, address, city, pin, lat, lon in HOSPITALS:
        hospital = db.query(Hospital).filter(Hospital.id == hid).first()
        if not hospital:
            hospital = Hospital(id=hid, name=name, address=address, city=city, phone="", active=True)
            db.add(hospital)
        else:
            hospital.name, hospital.address, hospital.city, hospital.active = name, address, city, True
    db.flush()

    spec_by_name = {s.name: s for s in db.query(Specialty).all()}

    for hid, _, _, _, _, _, _ in HOSPITALS:
        hospital = db.query(Hospital).filter(Hospital.id == hid).first()
        supported = HOSPITAL_SPECIALTIES.get(hid, set())
        for name, spec in spec_by_name.items():
            link = db.query(HospitalSpecialty).filter(
                HospitalSpecialty.hospital_id == hid,
                HospitalSpecialty.specialty_id == spec.id
            ).first()
            if name in supported and not link:
                db.add(HospitalSpecialty(hospital_id=hid, specialty_id=spec.id))
            elif name not in supported and link:
                db.delete(link)

            if name in supported:
                docs = db.query(Doctor).filter(
                    Doctor.hospital_id == hid,
                    Doctor.specialty_id == spec.id
                ).order_by(Doctor.id.asc()).all()
                names = DOCTOR_NAMES.get(name, ("Dr. Primary", "Dr. Alternative"))
                if not docs:
                    db.add(Doctor(hospital_id=hid, specialty_id=spec.id, name=names[0],
                                  average_consultation_minutes=max(10, 15), available=True))
                    db.add(Doctor(hospital_id=hid, specialty_id=spec.id, name=names[1],
                                  average_consultation_minutes=max(10, 15), available=True))
                else:
                    docs[0].name = names[0]
                    docs[0].available = True
                    if len(docs) == 1:
                        db.add(Doctor(hospital_id=hid, specialty_id=spec.id, name=names[1],
                                      average_consultation_minutes=15, available=True))
                    else:
                        docs[1].name = names[1]
                        docs[1].available = True
    db.commit()
