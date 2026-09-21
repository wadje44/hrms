from datetime import date

from app.services.wfh_service import can_approve, count_approved_days


class DummyRequest:
    def __init__(self, date_from, date_to, status="approved"):
        self.date_from = date_from
        self.date_to = date_to
        self.status = status


def test_count_approved_days_for_month():
    requests = [
        DummyRequest(date(2026, 9, 1), date(2026, 9, 2)),
        DummyRequest(date(2026, 9, 4), date(2026, 9, 4)),
        DummyRequest(date(2026, 9, 15), date(2026, 9, 16), status="pending"),
    ]

    assert count_approved_days(requests, date(2026, 9, 1)) == 3


def test_can_approve_checks_monthly_limit():
    existing = [
        DummyRequest(date(2026, 9, 1), date(2026, 9, 2)),
        DummyRequest(date(2026, 9, 4), date(2026, 9, 4)),
    ]

    assert can_approve(existing, date(2026, 9, 8), date(2026, 9, 10), 3) is False
    assert can_approve(existing, date(2026, 9, 8), date(2026, 9, 8), 3) is False
    assert can_approve(existing, date(2026, 9, 8), date(2026, 9, 8), 4) is True
