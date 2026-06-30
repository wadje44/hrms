from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import CurrentUser, get_current_user, require_admin
from app.db.session import get_db
from app.schemas.settings import SettingsOut, SettingsUpdate
from app.services.settings_service import get_settings

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("", response_model=SettingsOut)
def read_settings(_: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)):
    return get_settings(db)


@router.patch("", response_model=SettingsOut)
def update_settings(
    payload: SettingsUpdate,
    _: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    s = get_settings(db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(s, field, value)
    db.commit()
    db.refresh(s)
    return s
