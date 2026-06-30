"""GPS / location enforcement (acceptance criteria 3, 4, 5)."""

from app.core.constants import Category, SessionType
from app.services.gps import evaluate_punch, haversine_m

# Office reference point.
OFFICE = (19.0760, 72.8777)  # Mumbai-ish


def test_haversine_zero_distance():
    assert haversine_m(*OFFICE, *OFFICE) == 0.0


def test_haversine_known_distance():
    # ~111.2 km per degree of latitude.
    d = haversine_m(0.0, 0.0, 1.0, 0.0)
    assert 110_000 < d < 112_000


def _eval(**kw):
    base = dict(
        free_punch=False,
        gps_available=True,
        lat=OFFICE[0],
        lng=OFFICE[1],
        office_lat=OFFICE[0],
        office_lng=OFFICE[1],
        allowed_radius_m=250.0,
        wfh_used=0,
        wfh_limit=5,
    )
    base.update(kw)
    return evaluate_punch(category=base.pop("category"), **base)


def test_office_within_radius_allowed():
    res = _eval(category=Category.OFFICE)
    assert res.allowed and res.session_type == SessionType.OFFICE


def test_office_outside_radius_blocked():
    # ~0.01 deg lat ≈ 1.1km away -> blocked (criterion 3).
    res = _eval(category=Category.OFFICE, lat=OFFICE[0] + 0.01)
    assert not res.allowed
    assert "from office" in res.reason


def test_free_punch_always_allowed_even_far():
    # Deepak Nimbekar case (criterion 4).
    res = _eval(category=Category.OFFICE, free_punch=True, lat=OFFICE[0] + 0.5)
    assert res.allowed


def test_office_gps_denied_blocked():
    res = _eval(category=Category.OFFICE, gps_available=False, lat=None, lng=None)
    assert not res.allowed


def test_field_employee_not_validated():
    res = _eval(category=Category.FIELD, lat=OFFICE[0] + 1.0)
    assert res.allowed and res.is_field_duty


def test_hybrid_outside_radius_tagged_wfh():
    # criterion 5
    res = _eval(category=Category.HYBRID, lat=OFFICE[0] + 0.01)
    assert res.allowed and res.is_wfh and res.session_type == SessionType.WFH


def test_hybrid_wfh_blocked_when_limit_reached():
    res = _eval(category=Category.HYBRID, lat=OFFICE[0] + 0.01, wfh_used=5, wfh_limit=5)
    assert not res.allowed and "limit" in res.reason.lower()
