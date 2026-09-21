from datetime import date, timedelta

from fastapi import HTTPException


def _days_inclusive(start: date, end: date) -> int:
    return (end - start).days + 1


def _month_bounds(month_anchor: date) -> tuple[date, date]:
    first = date(month_anchor.year, month_anchor.month, 1)
    if month_anchor.month == 12:
        last = date(month_anchor.year + 1, 1, 1) - timedelta(days=1)
    else:
        last = date(month_anchor.year, month_anchor.month + 1, 1) - timedelta(days=1)
    return first, last


def count_approved_days(requests, month_anchor: date) -> int:
    first, last = _month_bounds(month_anchor)
    total = 0
    for req in requests:
        if getattr(req, "status", "") != "approved":
            continue
        if req.date_to < first or req.date_from > last:
            continue
        overlap_start = max(req.date_from, first)
        overlap_end = min(req.date_to, last)
        total += _days_inclusive(overlap_start, overlap_end)
    return total


def can_approve(existing_requests, date_from: date, date_to: date, monthly_limit: int) -> bool:
    if monthly_limit <= 0:
        return False
    requested = _days_inclusive(date_from, date_to)
    months = set()
    cur = date_from
    while cur <= date_to:
        months.add((cur.year, cur.month))
        cur += timedelta(days=1)

    for year, month in months:
        month_anchor = date(year, month, 1)
        first, last = _month_bounds(month_anchor)
        overlap_start = max(date_from, first)
        overlap_end = min(date_to, last)
        requested_days = _days_inclusive(overlap_start, overlap_end)
        current_used = count_approved_days(existing_requests, month_anchor)
        if current_used + requested_days > monthly_limit:
            return False
    return True


def assert_approval_allowed(db, employee_id: str, date_from: date, date_to: date, limit: int, model):
    existing = (
        db.query(model)
        .filter(
            model.employee_id == employee_id,
            model.status == "approved",
        )
        .all()
    )
    if not can_approve(existing, date_from, date_to, limit):
        raise HTTPException(
            status_code=400,
            detail=f"WFH request exceeds monthly limit ({limit} days).",
        )
