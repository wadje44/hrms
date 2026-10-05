from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import CurrentUser, require_manager
from app.db.session import get_db
from app.models.attendance import AttendanceDay
from app.models.employee import Employee
from app.models.payroll import PayrollRecord
from app.schemas.report import MonthlyReportSummary, YtdEarningsRow
from app.services.report_service import build_monthly_summary, build_ytd_earnings

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/monthly/{month}", response_model=MonthlyReportSummary)
def monthly_report(
    month: str,
    _: CurrentUser = Depends(require_manager),
    db: Session = Depends(get_db),
):
    """Return a compact monthly report for the HR dashboard by month."""
    year, mon = (int(part) for part in month.split("-"))
    rows = (
        db.query(AttendanceDay)
        .filter(
            AttendanceDay.date >= datetime(year, mon, 1).date(),
            AttendanceDay.date
            < datetime(
                year if mon < 12 else year + 1,
                mon + 1 if mon < 12 else 1,
                1,
            ).date(),
        )
        .all()
    )
    summary = build_monthly_summary(rows)
    return MonthlyReportSummary(
        month=month,
        present=int(summary["present"]),
        absent=int(summary["absent"]),
        late=int(summary["late"]),
        leave=int(summary["leave"]),
        wfh=int(summary["wfh"]),
        avg_hours=float(summary["avg_hours"]),
    )


@router.get("/ytd-earnings", response_model=list[YtdEarningsRow])
def ytd_earnings(
    _: CurrentUser = Depends(require_manager),
    db: Session = Depends(get_db),
):
    """Return aggregate year-to-date net earnings per employee."""
    year = datetime.utcnow().year
    rows = (
        db.query(PayrollRecord, Employee)
        .join(Employee, Employee.id == PayrollRecord.employee_id)
        .filter(PayrollRecord.month.like(f"{year}-%"))
        .all()
    )
    return [
        YtdEarningsRow(
            employee_id=emp.id,
            full_name=emp.full_name,
            ytd_earnings=float(rec.net),
        )
        for rec, emp in rows
    ]


@router.get("/ytd-earnings/aggregate", response_model=list[YtdEarningsRow])
def ytd_earnings_aggregate(
    _: CurrentUser = Depends(require_manager),
    db: Session = Depends(get_db),
):
    """Aggregate year-to-date net payslip totals by employee."""
    year = datetime.utcnow().year
    rows = (
        db.query(PayrollRecord, Employee)
        .join(Employee, Employee.id == PayrollRecord.employee_id)
        .filter(PayrollRecord.month.like(f"{year}-%"))
        .all()
    )
    totals = build_ytd_earnings(
        [
            type(
                "Row",
                (),
                {
                    "employee_id": emp.id,
                    "full_name": emp.full_name,
                    "net": float(rec.net),
                },
            )()
            for rec, emp in rows
        ]
    )
    return [YtdEarningsRow(**item) for item in totals]
