"""GPS distance + punch-location enforcement (doc §7, §9).

Pure functions — no DB or framework dependencies — so the rules are trivially testable.
"""

from dataclasses import dataclass
from math import asin, cos, radians, sin, sqrt

from app.core.constants import (
    EARTH_RADIUS_M,
    Category,
    SessionType,
)


def haversine_m(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Great-circle distance in metres (doc §9.2)."""
    dlat = radians(lat2 - lat1)
    dlng = radians(lng2 - lng1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlng / 2) ** 2
    return 2 * EARTH_RADIUS_M * asin(sqrt(a))


@dataclass
class PunchEvaluation:
    allowed: bool
    session_type: SessionType
    is_wfh: bool = False
    is_field_duty: bool = False
    distance_m: float | None = None
    reason: str = ""


def evaluate_punch(
    *,
    category: Category,
    free_punch: bool,
    gps_available: bool,
    lat: float | None,
    lng: float | None,
    office_lat: float | None,
    office_lng: float | None,
    allowed_radius_m: float,
    wfh_used: int,
    wfh_limit: int,
) -> PunchEvaluation:
    """Decide whether a punch is allowed and how to tag it.

    Rules (doc §7, §9):
      - Free-punch employees always succeed (GPS captured if available).
      - Field / Service: GPS captured but not validated -> always allowed, field duty.
      - Office: must be within radius; otherwise blocked. GPS required.
      - Hybrid: inside radius -> office; outside radius -> WFH (if under monthly limit),
        else blocked. GPS required.
    """
    distance = None
    if (
        gps_available
        and lat is not None
        and lng is not None
        and office_lat is not None
        and office_lng is not None
    ):
        distance = haversine_m(lat, lng, office_lat, office_lng)

    # Free-punch bypass (e.g. Deepak Nimbekar) — doc §9.4.
    if free_punch:
        return PunchEvaluation(
            allowed=True,
            session_type=SessionType.FIELD,
            distance_m=distance,
            reason="Free-punch employee — GPS not enforced.",
        )

    # Field / Service — capture only, never validate (doc §7).
    if category in (Category.FIELD, Category.SERVICE):
        return PunchEvaluation(
            allowed=True,
            session_type=SessionType.FIELD,
            is_field_duty=True,
            distance_m=distance,
            reason="Location captured (no validation).",
        )

    # Office / Hybrid require GPS.
    if not gps_available or lat is None or lng is None:
        return PunchEvaluation(
            allowed=False,
            session_type=SessionType.OFFICE,
            distance_m=distance,
            reason="GPS unavailable or permission denied. Punch blocked.",
        )
    if office_lat is None or office_lng is None:
        return PunchEvaluation(
            allowed=False,
            session_type=SessionType.OFFICE,
            distance_m=distance,
            reason="Office coordinates not configured. Contact admin.",
        )

    within = distance is not None and distance <= allowed_radius_m

    if category == Category.OFFICE:
        if within:
            return PunchEvaluation(
                allowed=True, session_type=SessionType.OFFICE, distance_m=distance
            )
        return PunchEvaluation(
            allowed=False,
            session_type=SessionType.OFFICE,
            distance_m=distance,
            reason=(
                f"You are {distance:.0f}m from office. Must be within {allowed_radius_m:.0f}m."
            ),
        )

    # Hybrid
    if within:
        return PunchEvaluation(allowed=True, session_type=SessionType.OFFICE, distance_m=distance)
    # Outside radius -> WFH if under monthly limit (doc §7.2).
    if wfh_used >= wfh_limit:
        return PunchEvaluation(
            allowed=False,
            session_type=SessionType.WFH,
            distance_m=distance,
            reason=(
                f"WFH limit reached ({wfh_used}/{wfh_limit} this month). "
                "Outside-office punch blocked."
            ),
        )
    return PunchEvaluation(
        allowed=True,
        session_type=SessionType.WFH,
        is_wfh=True,
        distance_m=distance,
        reason="Outside office radius — tagged as WFH.",
    )
