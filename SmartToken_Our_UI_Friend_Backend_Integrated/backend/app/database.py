from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from .config import settings

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def ensure_schema():
    # create_all handles fresh installations.
    Base.metadata.create_all(bind=engine)

    # Small compatibility migration for the SQLite DB from the previous ZIP.
    # It adds the manual time-shift field without deleting old records.
    if settings.database_url.startswith("sqlite"):
        with engine.begin() as conn:
            columns = conn.execute(text("PRAGMA table_info(appointments)")).fetchall()
            names = {row[1] for row in columns}
            if "manual_offset_minutes" not in names:
                conn.execute(text(
                    "ALTER TABLE appointments ADD COLUMN manual_offset_minutes INTEGER NOT NULL DEFAULT 0"
                ))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
