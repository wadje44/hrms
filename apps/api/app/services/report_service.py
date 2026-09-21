"""Report aggregations used by the HR dashboards and exports."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any


def build_monthly_summary(rows: Iterable[Any]) -> dict[str, float | int]:
    """Count attendance statuses and compute a monthly average workday length."""
    summary = {
        "present": 0,
        "absent": 0,
        "late": 0,
        "leave": 0,
        "wfh": 0,
        "avg_hours": 0.0,
    }

    hours: list[float] = []

    for row in rows:
        status = getattr(row, "status", None)
        total_hours = float(getattr(row, "total_hours", 0) or 0)
        if total_hours > 0:
            hours.append(total_hours)

        if status == "present":
            summary["present"] += 1
            if getattr(row, "is_late", False):
                summary["late"] += 1
            if getattr(row, "is_wfh", False):
                summary["wfh"] += 1
        elif status == "absent":
            summary["absent"] += 1
        elif status == "leave":
            summary["leave"] += 1

    if hours:
        summary["avg_hours"] = round(sum(hours) / len(hours), 2)

    return summary


def build_ytd_earnings(rows: Iterable[Any]) -> list[dict[str, Any]]:
    """Aggregate net payslip totals by employee for the current year."""
    totals: dict[str, dict[str, Any]] = {}

    for row in rows:
        employee_id = getattr(row, "employee_id", None)
        if not employee_id:
            continue

        full_name = getattr(row, "full_name", None) or "Unknown"
        net = float(getattr(row, "net", 0) or 0)

        if employee_id not in totals:
            totals[employee_id] = {
                "employee_id": employee_id,
                "full_name": full_name,
                "ytd_earnings": 0.0,
            }

        totals[employee_id]["ytd_earnings"] += net

    out = list(totals.values())
    out.sort(key=lambda item: (str(item["full_name"]), str(item["employee_id"])))
    for item in out:
        item["ytd_earnings"] = round(float(item["ytd_earnings"]), 2)
    return out
