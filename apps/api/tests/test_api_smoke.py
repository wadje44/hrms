"""End-to-end API smoke test against a live DB (requires DATABASE_URL + applied migrations).

Skipped automatically if the database is unreachable, so unit tests still run anywhere.
"""

import os

import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.skipif(
    os.getenv("RUN_DB_TESTS") != "1", reason="set RUN_DB_TESTS=1 to run DB-backed API tests"
)


@pytest.fixture(scope="module", autouse=True)
def _seed_db():
    """Seed employees before the DB-backed tests (idempotent)."""
    from app.seed import seed

    seed()


@pytest.fixture(scope="module")
def client():
    from app.main import app

    return TestClient(app)


def _login(client, emp_id, pin):
    r = client.post("/api/v1/auth/login", json={"employee_id": emp_id, "pin": pin})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_admin_login_and_dashboard(client):
    # criterion 1
    h = _login(client, "EMP008", "1234")
    r = client.get("/api/v1/dashboard/today", headers=h)
    assert r.status_code == 200
    assert "present" in r.json()


def test_wrong_pin_rejected(client):
    r = client.post("/api/v1/auth/login", json={"employee_id": "EMP008", "pin": "9999"})
    assert r.status_code == 401


def test_employee_cannot_list_employees(client):
    h = _login(client, "EMP001", "0000")
    r = client.get("/api/v1/employees", headers=h)
    assert r.status_code == 403  # role guard (doc §4)


def test_field_employee_punch_in_out(client):
    # Field employee: GPS not validated -> punch always allowed (criterion 2/4 flavor)
    h = _login(client, "EMP010", "0000")
    r = client.post(
        "/api/v1/attendance/punch-in",
        headers=h,
        json={"lat": 0.0, "lng": 0.0, "gps_available": True},
    )
    assert r.status_code == 200, r.text
    assert r.json()["allowed"] is True
    r2 = client.post("/api/v1/attendance/punch-out", headers=h)
    assert r2.status_code == 200, r2.text


def test_leave_apply_and_approve_flow(client):
    # criteria 9, 10
    emp = _login(client, "EMP002", "0000")
    r = client.post(
        "/api/v1/leaves",
        headers=emp,
        json={
            "date_from": "2026-07-01",
            "date_to": "2026-07-02",
            "leave_type": "EL",
            "reason": "trip",
        },
    )
    assert r.status_code == 201, r.text
    leave_id = r.json()["id"]

    admin = _login(client, "EMP008", "1234")
    r2 = client.post(
        f"/api/v1/leaves/{leave_id}/review", headers=admin, json={"approve": True, "comment": "ok"}
    )
    assert r2.status_code == 200, r2.text
    assert r2.json()["status"] == "approved"

    # attendance auto-marked as leave
    r3 = client.get("/api/v1/attendance/me?date_from=2026-07-01&date_to=2026-07-02", headers=emp)
    statuses = {d["status"] for d in r3.json()}
    assert "leave" in statuses


def test_payroll_run_and_summary(client):
    # criterion 11
    admin = _login(client, "EMP008", "1234")
    r = client.post("/api/v1/payroll/run/2026-07", headers=admin)
    assert r.status_code == 200, r.text
    assert len(r.json()) > 0
    r2 = client.get("/api/v1/payroll/summary/2026-07", headers=admin)
    assert r2.status_code == 200
