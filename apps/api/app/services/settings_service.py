from sqlalchemy.orm import Session

from app.models.settings import AppSettings


def get_settings(db: Session) -> AppSettings:
    """Return the settings singleton, creating it with defaults if missing."""
    s = db.get(AppSettings, 1)
    if s is None:
        s = AppSettings(id=1)
        db.add(s)
        db.commit()
        db.refresh(s)
    return s
