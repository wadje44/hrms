"""Leave workflow: request, approve/reject, balances, attendance auto-mark (doc §10)."""

from datetime import UTC, date, datetime, timedelta

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.constants import BALANCE_LEAVE_TYPES, AttendanceStatus, LeaveType
from app.models.leave import LeaveBalance, LeaveRequest
from app.services.attendance_service import get_or_create_day


def _date_range(start: date, end: date):
    cur = start
    while cur <= end:
        yield cur
        cur += timedelta(days=1)


def _days_inclusive(start: date, end: date) -> int:
    return (end - start).days + 1


def create_request(db: Session, employee_id: str, payload) -> LeaveRequest:
    if payload.date_to < payload.date_from:
        raise HTTPException(status_code=400, detail="date_to must not precede date_from")
    req = LeaveRequest(
        employee_id=employee_id,
        date_from=payload.date_from,
        date_to=payload.date_to,
        leave_type=payload.leave_type,
        reason=payload.reason,
        status="pending",
    )
    db.add(req)
    db.commit()
    db.refresh(req)
    return req


def get_balance(db: Session, employee_id: str, leave_type: LeaveType) -> LeaveBalance | None:
    return (
        db.query(LeaveBalance)
        .filter(LeaveBalance.employee_id == employee_id, LeaveBalance.leave_type == leave_type)
        .one_or_none()
    )


def review_request(
    db: Session, req: LeaveRequest, reviewer_id: str, approve: bool, comment: str
) -> LeaveRequest:
    if req.status != "pending":
        raise HTTPException(status_code=409, detail="Leave request already reviewed")

    req.reviewed_by = reviewer_id
    req.review_date = datetime.now(UTC)
    req.comment = comment

    if not approve:
        req.status = "rejected"
        db.commit()
        db.refresh(req)
        return req

    lt = LeaveType(req.leave_type)
    days = _days_inclusive(req.date_from, req.date_to)

    # Decrement balance for paid leave types (UL has no balance) — doc §10.3.
    if lt in BALANCE_LEAVE_TYPES:
        bal = get_balance(db, req.employee_id, lt)
        if bal is None or bal.balance < days:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient {lt} balance ({0 if bal is None else bal.balance} < {days})",
            )
        bal.balance -= days

    # Auto-mark attendance for each date as Leave (doc §10.2).
    for d in _date_range(req.date_from, req.date_to):
        day = get_or_create_day(db, req.employee_id, d)
        day.status = AttendanceStatus.LEAVE
        day.leave_type = lt
        day.manual_override = True

    req.status = "approved"
    db.commit()
    db.refresh(req)
    return req
