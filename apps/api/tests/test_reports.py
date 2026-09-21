from datetime import date

from app.core.constants import AttendanceStatus
from app.services.report_service import build_monthly_summary


class DummyDay:
    def __init__(self, d, status, total_hours=0.0, is_wfh=False, is_late=False):
        self.date = d
        self.status = status
        self.total_hours = total_hours
        self.is_wfh = is_wfh
        self.is_late = is_late


def test_build_monthly_summary_aggregates_statuses_and_hours():
    rows = [
        DummyDay(date(2026, 9, 1), AttendanceStatus.PRESENT, total_hours=8.5, is_wfh=True, is_late=False),
        DummyDay(date(2026, 9, 2), AttendanceStatus.PRESENT, total_hours=9.0, is_wfh=False, is_late=True),
        DummyDay(date(2026, 9, 3), AttendanceStatus.LEAVE, total_hours=0.0),
        DummyDay(date(2026, 9, 4), AttendanceStatus.ABSENT, total_hours=0.0),
    ]

    summary = build_monthly_summary(rows)
    assert summary["present"] == 2
    assert summary["late"] == 1
    assert summary["wfh"] == 1
    assert summary["leave"] == 1
    assert summary["absent"] == 1
    assert summary["avg_hours"] == 8.75
