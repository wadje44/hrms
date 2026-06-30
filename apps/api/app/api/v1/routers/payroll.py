from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import (
    CurrentUser,
    get_current_user,
    get_employee_or_404,
    require_admin,
)
from app.db.session import get_db
from app.models.employee import Employee
from app.models.payroll import HourlyRateOverride, PayrollRecord
from app.schemas.payroll import PayrollSummaryRow, PayslipOut, RateOverrideIn
from app.services import payroll_service

router = APIRouter(prefix="/payroll", tags=["payroll"])


@router.post("/run/{month}", response_model=list[PayslipOut])
def run_payroll(month: str, _: CurrentUser = Depends(require_admin), db: Session = Depends(get_db)):
    """Run (or re-run) payroll for all active employees for YYYY-MM (doc §11.3)."""
    return payroll_service.run_for_all(db, month)


@router.get("/summary/{month}", response_model=list[PayrollSummaryRow])
def payroll_summary(
    month: str, _: CurrentUser = Depends(require_admin), db: Session = Depends(get_db)
):
    rows = (
        db.query(PayrollRecord, Employee)
        .join(Employee, Employee.id == PayrollRecord.employee_id)
        .filter(PayrollRecord.month == month)
        .all()
    )
    out = []
    for rec, emp in rows:
        b = rec.breakdown or {}
        out.append(
            PayrollSummaryRow(
                employee_id=emp.id,
                full_name=emp.full_name,
                department=emp.department,
                present_days=b.get("present_days", 0),
                late_marks=b.get("late_marks", 0),
                worked_hours=b.get("worked_hours", 0),
                gross=float(rec.gross),
                deductions_total=float(rec.deductions_total),
                net=float(rec.net),
            )
        )
    return out


@router.get("/payslip/me/{month}", response_model=PayslipOut)
def my_payslip(
    month: str, user: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)
):
    rec = (
        db.query(PayrollRecord)
        .filter(PayrollRecord.month == month, PayrollRecord.employee_id == user.employee_id)
        .one_or_none()
    )
    if rec is None:
        raise HTTPException(status_code=404, detail="Payslip not found for that month")
    return rec


@router.get("/payslip/{employee_id}/{month}", response_model=PayslipOut)
def employee_payslip(
    employee_id: str,
    month: str,
    _: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    rec = (
        db.query(PayrollRecord)
        .filter(PayrollRecord.month == month, PayrollRecord.employee_id == employee_id)
        .one_or_none()
    )
    if rec is None:
        raise HTTPException(status_code=404, detail="Payslip not found")
    return rec


@router.put("/overrides/{month}", status_code=204)
def set_rate_override(
    month: str,
    payload: RateOverrideIn,
    _: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Set a per-employee, per-month hourly rate override (doc §11.4)."""
    get_employee_or_404(db, payload.employee_id)
    rec = (
        db.query(HourlyRateOverride)
        .filter(
            HourlyRateOverride.month == month,
            HourlyRateOverride.employee_id == payload.employee_id,
        )
        .one_or_none()
    )
    if rec is None:
        rec = HourlyRateOverride(month=month, employee_id=payload.employee_id)
        db.add(rec)
    rec.hourly_rate = payload.hourly_rate
    db.commit()
