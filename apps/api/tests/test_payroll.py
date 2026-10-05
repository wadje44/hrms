"""Payroll engine (acceptance criteria 7, 11, 12, 13)."""

from app.services.payroll import PayrollInput, compute_payslip, resolve_hourly_rate


def _input(**kw) -> PayrollInput:
    base = dict(
        employee_id="EMP001",
        full_name="Test User",
        designation="Worker",
        department="Office",
        month="2026-06",
        monthly_salary=52000.0,
        explicit_hourly_rate=None,
        override_rate=None,
        fixed_components=[],
        deductions=[],
        standard_monthly_hours=208.0,  # 26 × 8
        working_hours_per_day=8.0,
        working_days_in_month=26,
        present_days=26,
        worked_hours=208.0,
        paid_leave_days=0,
        ul_days=0,
        absent_days=0,
        late_marks=0,
        free_late_marks=3,
    )
    base.update(kw)
    return PayrollInput(**base)


def test_derived_hourly_rate_from_salary():
    # 52000 / 208 = 250/hr
    assert resolve_hourly_rate(_input()) == 250.0


def test_override_takes_precedence():
    # criterion 13
    assert resolve_hourly_rate(_input(override_rate=300.0, explicit_hourly_rate=275.0)) == 300.0


def test_explicit_rate_used_when_no_override():
    assert resolve_hourly_rate(_input(explicit_hourly_rate=275.0)) == 275.0


def test_full_month_net_equals_formula():
    # criterion 11: net = rate*paid_hours + fixed - deductions
    slip = compute_payslip(
        _input(
            fixed_components=[{"name": "HRA", "amount": 5000}],
            deductions=[{"name": "PF", "amount": 1800}],
        )
    )
    assert slip["hourly_rate"] == 250.0
    assert slip["paid_hours"] == 208.0
    assert slip["gross"] == 52000.0
    assert slip["net"] == 52000.0 + 5000 - 1800


def test_unpaid_leave_reduces_net_proportionally():
    # criterion 12: 2 UL days -> 2*8 fewer paid hours -> -2*8*250 = -4000
    full = compute_payslip(_input())
    with_ul = compute_payslip(_input(worked_hours=208.0, ul_days=2, present_days=26))
    assert with_ul["ul_deduction_hours"] == 16.0
    assert with_ul["paid_hours"] == 192.0
    assert full["net"] - with_ul["net"] == 250.0 * 16


def test_paid_leave_counts_as_present():
    slip = compute_payslip(_input(worked_hours=192.0, paid_leave_days=2, present_days=24))
    # 192 worked + 2*8 paid leave = 208 paid hours
    assert slip["paid_hours"] == 208.0
    assert slip["gross"] == 52000.0


def test_absent_days_reduce_net_proportionally():
    full = compute_payslip(_input())
    with_absence = compute_payslip(_input(worked_hours=160.0, present_days=20, absent_days=2))
    assert with_absence["absent_days"] == 2
    assert with_absence["paid_hours"] == 144.0
    assert full["net"] - with_absence["net"] == 250.0 * 64


def test_excess_late_marks_deduct_hours():
    # criterion 7 end-to-end: 5 late marks -> 2 billable -> -2 paid hours
    slip = compute_payslip(_input(late_marks=5))
    assert slip["late_mark_deduction_hours"] == 2.0
    assert slip["paid_hours"] == 206.0


def test_ytd_earnings_aggregate_net_by_employee():
    from types import SimpleNamespace

    from app.services.report_service import build_ytd_earnings

    rows = [
        SimpleNamespace(employee_id="EMP001", full_name="Alice", net=1200.0),
        SimpleNamespace(employee_id="EMP001", full_name="Alice", net=1800.0),
        SimpleNamespace(employee_id="EMP002", full_name="Bob", net=2400.0),
    ]

    out = build_ytd_earnings(rows)
    assert out == [
        {"employee_id": "EMP001", "full_name": "Alice", "ytd_earnings": 3000.0},
        {"employee_id": "EMP002", "full_name": "Bob", "ytd_earnings": 2400.0},
    ]
