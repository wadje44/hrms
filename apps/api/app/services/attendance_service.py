"""Attendance orchestration: punch in/out, day recompute (doc §8)."""

from datetime import UTC, date, datetime

from fastapi import HTTPException
from sqlalchemy import extract
from sqlalchemy.orm import Session

from app.core.constants import AttendanceStatus, Category, SessionType
from app.models.attendance import AttendanceDay, AttendanceSession
from app.models.employee import Employee
from app.services import gps, latemark
from app.services.settings_service import get_settings


def _now() -> datetime:
    return datetime.now(UTC)


def session_hours(s: AttendanceSession) -> float:
    if s.punch_out is None:
        return 0.0
    return (s.punch_out - s.punch_in).total_seconds() / 3600.0


def recompute_day(day: AttendanceDay) -> None:
    total = sum(session_hours(s) for s in day.sessions)
    day.total_hours = round(total, 2)
    # Day-level paid hours = worked hours; monthly late deductions applied at payroll.
    if not day.manual_override:
        day.paid_hours = round(total, 2)


def get_or_create_day(db: Session, employee_id: str, day: date) -> AttendanceDay:
    rec = (
        db.query(AttendanceDay)
        .filter(AttendanceDay.employee_id == employee_id, AttendanceDay.date == day)
        .one_or_none()
    )
    if rec is None:
        rec = AttendanceDay(employee_id=employee_id, date=day)
        db.add(rec)
        db.flush()
    return rec


def _wfh_used_this_month(db: Session, employee_id: str, day: date) -> int:
    return (
        db.query(AttendanceDay)
        .filter(
            AttendanceDay.employee_id == employee_id,
            AttendanceDay.is_wfh.is_(True),
            extract("year", AttendanceDay.date) == day.year,
            extract("month", AttendanceDay.date) == day.month,
        )
        .count()
    )


def open_session(db: Session, employee_id: str, day: date) -> AttendanceSession | None:
    return (
        db.query(AttendanceSession)
        .join(AttendanceDay)
        .filter(
            AttendanceDay.employee_id == employee_id,
            AttendanceDay.date == day,
            AttendanceSession.punch_out.is_(None),
        )
        .one_or_none()
    )


def punch_in(
    db: Session, employee: Employee, lat: float | None, lng: float | None, gps_available: bool
) -> gps.PunchEvaluation:
    now = _now()
    today = now.date()

    if open_session(db, employee.id, today) is not None:
        raise HTTPException(status_code=409, detail="Already punched in. Punch out first.")

    settings = get_settings(db)
    wfh_used = _wfh_used_this_month(db, employee.id, today)

    result = gps.evaluate_punch(
        category=Category(employee.category),
        free_punch=employee.free_punch,
        gps_available=gps_available,
        lat=lat,
        lng=lng,
        office_lat=settings.office_lat,
        office_lng=settings.office_lng,
        allowed_radius_m=settings.allowed_radius_m,
        wfh_used=wfh_used,
        wfh_limit=employee.wfh_limit,
    )
    if not result.allowed:
        return result

    day = get_or_create_day(db, employee.id, today)
    first_session = len(day.sessions) == 0

    db.add(
        AttendanceSession(
            day_id=day.id,
            punch_in=now,
            lat=lat,
            lng=lng,
            type=result.session_type,
        )
    )

    if not day.manual_override:
        day.status = AttendanceStatus.PRESENT
        if result.is_wfh:
            day.is_wfh = True
        if result.is_field_duty:
            day.is_field_duty = True
        if first_session:
            # Late mark evaluated on the first punch-in of the day (office/hybrid-office).
            if result.session_type == SessionType.OFFICE and latemark.is_late(
                now.time(), settings.late_cutoff
            ):
                day.is_late = True

    db.flush()
    db.refresh(day)
    recompute_day(day)
    db.commit()
    return result


def punch_out(db: Session, employee: Employee) -> AttendanceDay:
    now = _now()
    today = now.date()
    sess = open_session(db, employee.id, today)
    if sess is None:
        raise HTTPException(status_code=409, detail="No active punch-in session today.")
    sess.punch_out = now
    db.flush()
    day = db.get(AttendanceDay, sess.day_id)
    db.refresh(day)
    recompute_day(day)
    db.commit()
    db.refresh(day)
    return day
