from datetime import UTC, date, datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.constants import AttendanceStatus
from app.core.deps import CurrentUser, require_manager
from app.db.session import get_db
from app.models.attendance import AttendanceDay, AttendanceSession
from app.models.employee import Employee
from app.schemas.dashboard import DashboardSummary, EmployeeRef

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/today", response_model=DashboardSummary)
def today_summary(
    on: date | None = None,
    _: CurrentUser = Depends(require_manager),
    db: Session = Depends(get_db),
):
    """Real-time stat cards with drill-down lists (doc §12.1)."""
    day = on or datetime.now(UTC).date()

    active = {e.id: e for e in db.query(Employee).filter(Employee.active.is_(True)).all()}
    days = (
        db.query(AttendanceDay)
        .filter(AttendanceDay.date == day, AttendanceDay.employee_id.in_(active.keys()))
        .all()
    )
    by_emp = {d.employee_id: d for d in days}

    open_ids = {
        row[0]
        for row in (
            db.query(AttendanceDay.employee_id)
            .join(AttendanceSession)
            .filter(AttendanceDay.date == day, AttendanceSession.punch_out.is_(None))
            .all()
        )
    }

    def ref(emp_id: str, detail: str = "") -> EmployeeRef:
        return EmployeeRef(employee_id=emp_id, full_name=active[emp_id].full_name, detail=detail)

    present, absent, late, on_leave, currently_in = [], [], [], [], []

    for emp_id in active:
        rec = by_emp.get(emp_id)
        if rec is None or rec.status == AttendanceStatus.ABSENT:
            absent.append(ref(emp_id))
            continue
        if rec.status == AttendanceStatus.LEAVE:
            on_leave.append(ref(emp_id, rec.leave_type or ""))
            continue
        if rec.status == AttendanceStatus.PRESENT:
            present.append(ref(emp_id, "WFH" if rec.is_wfh else "office"))
            if rec.is_late:
                late.append(ref(emp_id))

    for emp_id in open_ids:
        if emp_id in active:
            currently_in.append(ref(emp_id))

    return DashboardSummary(
        date=day.isoformat(),
        present=present,
        absent=absent,
        late=late,
        on_leave=on_leave,
        currently_in=currently_in,
    )
