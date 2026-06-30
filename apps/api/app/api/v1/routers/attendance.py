from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import (
    CurrentUser,
    get_current_user,
    get_employee_or_404,
    require_admin,
    require_manager,
)
from app.db.session import get_db
from app.models.attendance import AttendanceDay
from app.schemas.attendance import (
    AttendanceDayOut,
    ManualAttendanceUpdate,
    PunchRequest,
    PunchResult,
)
from app.services import attendance_service

router = APIRouter(prefix="/attendance", tags=["attendance"])


def _query_range(db: Session, employee_id: str, date_from: date | None, date_to: date | None):
    q = db.query(AttendanceDay).filter(AttendanceDay.employee_id == employee_id)
    if date_from:
        q = q.filter(AttendanceDay.date >= date_from)
    if date_to:
        q = q.filter(AttendanceDay.date <= date_to)
    return q.order_by(AttendanceDay.date).all()


@router.post("/punch-in", response_model=PunchResult)
def punch_in(
    payload: PunchRequest,
    user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    emp = get_employee_or_404(db, user.employee_id)
    res = attendance_service.punch_in(db, emp, payload.lat, payload.lng, payload.gps_available)
    return PunchResult(
        allowed=res.allowed,
        session_type=res.session_type,
        is_wfh=res.is_wfh,
        is_field_duty=res.is_field_duty,
        distance_m=res.distance_m,
        reason=res.reason,
    )


@router.post("/punch-out", response_model=AttendanceDayOut)
def punch_out(
    user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    emp = get_employee_or_404(db, user.employee_id)
    return attendance_service.punch_out(db, emp)


@router.get("/me", response_model=list[AttendanceDayOut])
def my_attendance(
    date_from: date | None = None,
    date_to: date | None = None,
    user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return _query_range(db, user.employee_id, date_from, date_to)


@router.get("/{employee_id}", response_model=list[AttendanceDayOut])
def employee_attendance(
    employee_id: str,
    date_from: date | None = None,
    date_to: date | None = None,
    _: CurrentUser = Depends(require_manager),
    db: Session = Depends(get_db),
):
    return _query_range(db, employee_id, date_from, date_to)


@router.put("/{employee_id}/{day}", response_model=AttendanceDayOut)
def manual_override(
    employee_id: str,
    day: date,
    payload: ManualAttendanceUpdate,
    _: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Admin manually sets a day's status (doc §8.5)."""
    get_employee_or_404(db, employee_id)
    rec = attendance_service.get_or_create_day(db, employee_id, day)
    rec.status = payload.status
    rec.leave_type = payload.leave_type
    rec.manual_override = True
    if payload.total_hours is not None:
        rec.total_hours = payload.total_hours
        rec.paid_hours = payload.total_hours
    db.commit()
    db.refresh(rec)
    return rec
