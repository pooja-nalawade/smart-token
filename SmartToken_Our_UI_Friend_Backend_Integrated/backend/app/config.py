import os
from pathlib import Path
from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BACKEND_DIR / ".env")

class Settings:
    database_url = os.getenv("DATABASE_URL", "sqlite:///./smart_token.db")
    frontend_origins = [
        x.strip() for x in os.getenv("FRONTEND_ORIGIN", "http://localhost:8000").split(",") if x.strip()
    ]
    email_enabled = os.getenv("EMAIL_ENABLED", "false").lower() in {"1","true","yes","on"}
    sms_enabled = os.getenv("SMS_ENABLED", "false").lower() in {"1","true","yes","on"}

settings = Settings()
