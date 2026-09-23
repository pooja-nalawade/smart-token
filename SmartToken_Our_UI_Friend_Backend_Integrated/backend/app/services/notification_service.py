import os
import re
import smtplib
from email.mime.text import MIMEText
from typing import Optional
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BACKEND_DIR / ".env")

try:
    from twilio.rest import Client
except ImportError:
    Client = None


def _env_bool(name: str, default: bool = False) -> bool:
    val = os.getenv(name, str(default)).strip().lower()
    return val in {"1", "true", "yes", "on"}


def normalize_phone(phone: Optional[str]) -> Optional[str]:
    if not phone:
        return None
    value = re.sub(r"[\s\-().]", "", str(phone).strip())
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
        return None
    return "+91" + digits if re.fullmatch(r"[6-9]\d{9}", digits) else None


def get_twilio_client():
    if Client is None:
        return None
    sid = os.getenv("TWILIO_ACCOUNT_SID", "").strip()
    token = os.getenv("TWILIO_AUTH_TOKEN", "").strip()
    if not sid or not token:
        return None
    try:
        return Client(sid, token)
    except Exception:
        return None


def send_sms_notification(to_phone: Optional[str], message: str) -> bool:
    if not _env_bool("SMS_ENABLED", False) or not to_phone:
        return False
    destination = normalize_phone(to_phone)
    client = get_twilio_client()
    if not destination or not client:
        return False

    from_number = os.getenv("TWILIO_FROM_NUMBER", "").strip()
    messaging_service_sid = os.getenv("TWILIO_MESSAGING_SERVICE_SID", "").strip()
    if not from_number and not messaging_service_sid:
        return False

    try:
        kwargs = {"body": message, "to": destination}
        if messaging_service_sid:
            kwargs["messaging_service_sid"] = messaging_service_sid
        else:
            kwargs["from_"] = from_number
        sms = client.messages.create(**kwargs)
        print(f"[SMS SENT] {destination} | {sms.sid}")
        return True
    except Exception as exc:
        print(f"[SMS ERROR] {destination}: {getattr(exc, 'msg', str(exc))}")
        return False


def send_email_notification(to_email: Optional[str], subject: str, message: str) -> bool:
    if not _env_bool("EMAIL_ENABLED", False) or not to_email:
        return False

    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com").strip()
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_username = os.getenv("SMTP_USERNAME", "").strip()
    smtp_password = os.getenv("SMTP_PASSWORD", "").strip()
    smtp_from = os.getenv("SMTP_FROM", smtp_username).strip()

    if not smtp_username or not smtp_password or smtp_password.startswith("YOUR_"):
        print("[EMAIL ERROR] SMTP configuration is incomplete.")
        return False

    try:
        msg = MIMEText(message, "plain", "utf-8")
        msg["Subject"] = subject
        msg["From"] = smtp_from or smtp_username
        msg["To"] = to_email
        with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.sendmail(msg["From"], [to_email], msg.as_string())
        print(f"[EMAIL SENT] {to_email}")
        return True
    except Exception as exc:
        print(f"[EMAIL ERROR] {to_email}: {exc}")
        return False


def _fmt(dt):
    if isinstance(dt, datetime):
        return dt.strftime("%I:%M %p, %d %b")
    return str(dt or "-")


def format_sms_message(status, patient_name, token, specialty, appt_time, arrival_time, position, wait_min, doctor_name):
    if status == "BOOKED":
        return f"SmartToken: {token} confirmed for {patient_name}. {specialty}. Turn {appt_time}. Arrive {arrival_time}."
    if status == "CANCELLED":
        return f"SmartToken: {token} for {patient_name} is cancelled."
    if status == "SERVED":
        return f"SmartToken: {token} called. Please proceed to the doctor now."
    if status == "DOCTOR_CHANGED":
        return f"SmartToken: Doctor changed to {doctor_name}. Token {token}, pos {position}, wait {wait_min}m."
    return f"SmartToken update: {token} pos {position}, wait {wait_min}m, turn {appt_time}."


def format_email_message(status, hospital_name, patient_name, token, specialty, appt_time, arrival_time, position, wait_min, doctor_name):
    if status == "BOOKED":
        subject = f"{hospital_name} - OPD Appointment Confirmed (#{token})"
        body = (
            f"{hospital_name} - Smart Token\n\nDear {patient_name},\n\n"
            "Your OPD appointment is confirmed.\n\n"
            f"Token: #{token}\nDepartment: {specialty}\nDoctor: {doctor_name}\n"
            f"Expected Consultation Time: {appt_time}\nRecommended Arrival Time: {arrival_time}\n\n"
            "Live queue changes will be sent automatically by email/SMS.\n\nThank you.\nSmartToken OPD"
        )
    elif status == "CANCELLED":
        subject = f"{hospital_name} - OPD Appointment Cancelled (#{token})"
        body = (
            f"{hospital_name} - Appointment Update\n\nDear {patient_name},\n\n"
            f"Your OPD token #{token} has been cancelled.\n\nThank you.\nSmartToken OPD"
        )
    elif status == "SERVED":
        subject = f"{hospital_name} - OPD Consultation Call (#{token})"
        body = (
            f"{hospital_name} - Turn Called\n\nDear {patient_name},\n\n"
            f"Token #{token} has been called. Please proceed to the doctor consultation room now.\n\n"
            "Thank you.\nSmartToken OPD"
        )
    elif status == "DOCTOR_CHANGED":
        subject = f"{hospital_name} - Doctor Change for Token #{token}"
        body = (
            f"{hospital_name} - Doctor Availability Update\n\nDear {patient_name},\n\n"
            f"The doctor for token #{token} has changed to {doctor_name}.\n\n"
            f"Current Queue Position: #{position}\nEstimated Waiting Time: {wait_min} minutes\n"
            f"Estimated Turn: {appt_time}\n\nThank you for your patience.\nSmartToken OPD"
        )
    else:
        subject = f"{hospital_name} - OPD Queue Update (#{token})"
        body = (
            f"{hospital_name} - Live Queue Update\n\nDear {patient_name},\n\n"
            f"Your token #{token} queue status has changed.\n\n"
            f"Current Queue Position: #{position}\nEstimated Waiting Time: {wait_min} minutes\n"
            f"Estimated Turn: {appt_time}\nRecommended Arrival: {arrival_time}\n\n"
            "This update was generated automatically by SmartToken.\n\nThank you.\nSmartToken OPD"
        )
    return subject, body


def notify_patient(patient, appointment, hospital_name="Government Hospital", status="BOOKED"):
    patient_name = getattr(patient, "name", "Patient")
    patient_email = getattr(patient, "email", None)
    patient_phone = getattr(patient, "phone", None)
    token = getattr(appointment, "token_number", "T-000")
    position = int(getattr(appointment, "queue_position", 1) or 1)
    wait_min = int(getattr(appointment, "waiting_minutes", 0) or 0)
    appt_str = _fmt(getattr(appointment, "appointment_time", None))
    arrival_str = _fmt(getattr(appointment, "estimated_arrival_time", None))
    specialty = getattr(getattr(appointment, "specialty", None), "name", "General Medicine")
    doctor = getattr(getattr(appointment, "doctor", None), "name", "OPD Doctor")

    sms = format_sms_message(status, patient_name, str(token), specialty, appt_str, arrival_str, position, wait_min, doctor)
    subject, body = format_email_message(
        status, hospital_name, patient_name, str(token), specialty, appt_str, arrival_str, position, wait_min, doctor
    )

    email_ok = False if patient_email == "emergency@local.test" else send_email_notification(patient_email, subject, body)
    sms_ok = False if patient_phone in {"0000000000", ""} else send_sms_notification(patient_phone, sms)
    return email_ok, sms_ok


def get_sms_diagnostics():
    sid = os.getenv("TWILIO_ACCOUNT_SID", "").strip()
    token = os.getenv("TWILIO_AUTH_TOKEN", "").strip()
    enabled = _env_bool("SMS_ENABLED", False)
    diag = {
        "sms_enabled": enabled,
        "twilio_module_installed": Client is not None,
        "account_sid_present": bool(sid),
        "from_number": os.getenv("TWILIO_FROM_NUMBER", "").strip(),
        "messaging_service_sid": os.getenv("TWILIO_MESSAGING_SERVICE_SID", "").strip(),
        "connected": False,
        "account_name": None,
        "balance": None,
        "account_phone_numbers": [],
        "verified_caller_ids": [],
        "issues": [],
    }
    if not enabled:
        diag["issues"].append("SMS_ENABLED is false in backend/.env.")
        return diag
    if Client is None:
        diag["issues"].append("Twilio package is not installed.")
        return diag
    if not sid or not token:
        diag["issues"].append("Twilio credentials are missing.")
        return diag
    try:
        client = Client(sid, token)
        account = client.api.accounts(sid).fetch()
        diag["connected"] = True
        diag["account_name"] = account.friendly_name
        try:
            bal = client.balance.fetch()
            diag["balance"] = f"{bal.balance} {bal.currency}"
        except Exception:
            pass
        diag["account_phone_numbers"] = [p.phone_number for p in client.incoming_phone_numbers.list(limit=10)]
        diag["verified_caller_ids"] = [c.phone_number for c in client.outgoing_caller_ids.list(limit=10)]
    except Exception as exc:
        diag["issues"].append(getattr(exc, "msg", str(exc)))
    return diag
