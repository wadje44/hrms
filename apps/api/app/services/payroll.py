"""Payroll calculation engine (doc §11). Pure functions.

Net Pay = (Hourly Rate × Paid Hours) + Fixed Components − Deductions

Pay is driven by *paid hours*, so absences and unpaid leave reduce pay
pro-rata naturally (those days contribute zero worked hours and are not
credited as paid leave). Paid leave days are credited as a normal working day.
Excess late marks deduct one hour each from paid hours.
"""

from dataclasses import dataclass, field

from app.services.latemark import late_deduction_hours


@dataclass
class PayrollInput:
    employee_id: str
    full_name: str
    designation: str
    department: str
    month: str  # YYYY-MM

    monthly_salary: float
    explicit_hourly_rate: float | None  # employee.hourly_rate
    override_rate: float | None  # per employee-month override (doc §11.4)
    fixed_components: list[dict] = field(default_factory=list)  # [{name, amount}]
    deductions: list[dict] = field(default_factory=list)  # [{name, amount}]

    # Standard divisor for deriving an hourly rate from monthly salary.
    standard_monthly_hours: float = 208.0  # e.g. 26 days × 8h
    working_hours_per_day: float = 8.0

    # Aggregated attendance for the month.
    working_days_in_month: int = 0
    present_days: int = 0
    worked_hours: float = 0.0  # sum of actual session durations
    paid_leave_days: int = 0
    ul_days: int = 0
    absent_days: int = 0
    late_marks: int = 0
    free_late_marks: int = 3
    leave_breakdown: dict = field(default_factory=dict)  # {leave_type: days}


def resolve_hourly_rate(inp: PayrollInput) -> float:
    """Override > explicit per-employee rate > derived from monthly salary."""
    if inp.override_rate is not None:
        return float(inp.override_rate)
    if inp.explicit_hourly_rate is not None:
        return float(inp.explicit_hourly_rate)
    if inp.standard_monthly_hours > 0:
        return float(inp.monthly_salary) / inp.standard_monthly_hours
    return 0.0


def compute_payslip(inp: PayrollInput) -> dict:
    rate = resolve_hourly_rate(inp)

    paid_leave_hours = inp.paid_leave_days * inp.working_hours_per_day
    late_deduct_hours = late_deduction_hours(inp.late_marks, inp.free_late_marks)

    paid_hours = max(0.0, inp.worked_hours + paid_leave_hours - late_deduct_hours)

    gross = round(rate * paid_hours, 2)
    fixed_total = round(sum(float(c.get("amount", 0)) for c in inp.fixed_components), 2)
    deductions_total = round(sum(float(d.get("amount", 0)) for d in inp.deductions), 2)
    net = round(gross + fixed_total - deductions_total, 2)

    return {
        "employee_id": inp.employee_id,
        "full_name": inp.full_name,
        "designation": inp.designation,
        "department": inp.department,
        "month": inp.month,
        "working_days_in_month": inp.working_days_in_month,
        "present_days": inp.present_days,
        "absent_days": inp.absent_days,
        "paid_leave_days": inp.paid_leave_days,
        "ul_days": inp.ul_days,
        "leave_breakdown": inp.leave_breakdown,
        "worked_hours": round(inp.worked_hours, 2),
        "paid_leave_hours": round(paid_leave_hours, 2),
        "late_marks": inp.late_marks,
        "late_mark_deduction_hours": round(late_deduct_hours, 2),
        "paid_hours": round(paid_hours, 2),
        "hourly_rate": round(rate, 2),
        "gross": gross,
        "fixed_components": inp.fixed_components,
        "fixed_components_total": fixed_total,
        "deductions": inp.deductions,
        "deductions_total": deductions_total,
        "net": net,
    }
