"""Monthly payroll run: aggregate attendance -> PayrollInput -> store payslip (doc §11.3)."""

import calendar
from datetime import date

from sqlalchemy import extract
from sqlalchemy.orm import Session

from app.core.constants import PAID_LEAVE_TYPES, AttendanceStatus, LeaveType
from app.models.attendance import AttendanceDay
from app.models.employee import Employee
from app.models.payroll import HourlyRateOverride, PayrollRecord
from app.services.payroll import PayrollInput, compute_payslip
from app.services.settings_service import get_settings


def _parse_month(month: str) -> tuple[int, int]:
    year, mon = month.split("-")
    return int(year), int(mon)


def _weekdays_in_month(year: int, mon: int, holidays: set[str]) -> int:
    days = calendar.monthrange(year, mon)[1]
    count = 0
    for d in range(1, days + 1):
        dt = date(year, mon, d)
        if dt.weekday() < 5 and dt.isoformat() not in holidays:  # Mon-Fri, not a holiday
            count += 1
    return count


def build_input(db: Session, employee: Employee, month: str) -> PayrollInput:
    year, mon = _parse_month(month)
    settings = get_settings(db)

    days = (
        db.query(AttendanceDay)
        .filter(
            AttendanceDay.employee_id == employee.id,
            extract("year", AttendanceDay.date) == year,
            extract("month", AttendanceDay.date) == mon,
        )
        .all()
    )

    present_days = worked_hours = late_marks = 0
    paid_leave_days = ul_days = absent_days = 0
    worked_hours = 0.0
    leave_breakdown: dict[str, int] = {}

    for day in days:
        if day.status == AttendanceStatus.PRESENT:
            present_days += 1
            worked_hours += float(day.total_hours or 0)
            if day.is_late:
                late_marks += 1
        elif day.status == AttendanceStatus.ABSENT:
            absent_days += 1
        elif day.status == AttendanceStatus.LEAVE and day.leave_type:
            lt = LeaveType(day.leave_type)
            leave_breakdown[lt] = leave_breakdown.get(lt, 0) + 1
            if lt in PAID_LEAVE_TYPES:
                paid_leave_days += 1
            elif lt == LeaveType.UL:
                ul_days += 1

    override = (
        db.query(HourlyRateOverride)
        .filter(HourlyRateOverride.month == month, HourlyRateOverride.employee_id == employee.id)
        .one_or_none()
    )

    standard_monthly_hours = settings.working_days_per_month * settings.working_hours_per_day

    return PayrollInput(
        employee_id=employee.id,
        full_name=employee.full_name,
        designation=employee.designation,
        department=employee.department,
        month=month,
        monthly_salary=float(employee.monthly_salary or 0),
        explicit_hourly_rate=float(employee.hourly_rate) if employee.hourly_rate else None,
        override_rate=float(override.hourly_rate) if override else None,
        fixed_components=list(employee.fixed_components or []),
        deductions=list(employee.deductions or []),
        standard_monthly_hours=standard_monthly_hours,
        working_hours_per_day=settings.working_hours_per_day,
        working_days_in_month=_weekdays_in_month(year, mon, set(settings.holidays or [])),
        present_days=present_days,
        worked_hours=worked_hours,
        paid_leave_days=paid_leave_days,
        ul_days=ul_days,
        absent_days=absent_days,
        late_marks=late_marks,
        free_late_marks=settings.free_late_marks,
        leave_breakdown=leave_breakdown,
    )


def run_for_employee(db: Session, employee: Employee, month: str) -> PayrollRecord:
    slip = compute_payslip(build_input(db, employee, month))

    rec = (
        db.query(PayrollRecord)
        .filter(PayrollRecord.month == month, PayrollRecord.employee_id == employee.id)
        .one_or_none()
    )
    if rec is None:
        rec = PayrollRecord(month=month, employee_id=employee.id)
        db.add(rec)
    rec.gross = slip["gross"]
    rec.deductions_total = slip["deductions_total"]
    rec.net = slip["net"]
    rec.breakdown = slip
    return rec


def run_for_all(db: Session, month: str) -> list[PayrollRecord]:
    employees = db.query(Employee).filter(Employee.active.is_(True)).all()
    records = [run_for_employee(db, emp, month) for emp in employees]
    db.commit()
    for r in records:
        db.refresh(r)
    return records
