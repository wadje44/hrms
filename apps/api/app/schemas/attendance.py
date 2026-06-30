from datetime import date as date_type
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.core.constants import AttendanceStatus, LeaveType, SessionType


class PunchRequest(BaseModel):
    lat: float | None = None
    lng: float | None = None
    gps_available: bool = True


class PunchResult(BaseModel):
    allowed: bool
    session_type: SessionType
    is_wfh: bool = False
    is_field_duty: bool = False
    distance_m: float | None = None
    reason: str = ""
    day_status: AttendanceStatus | None = None


class SessionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    punch_in: datetime
    punch_out: datetime | None
    lat: float | None
    lng: float | None
    type: SessionType


class AttendanceDayOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    employee_id: str
    date: date_type
    status: AttendanceStatus
    leave_type: LeaveType | None
    total_hours: float
    paid_hours: float
    is_wfh: bool
    is_field_duty: bool
    is_late: bool
    manual_override: bool
    sessions: list[SessionOut] = []


class ManualAttendanceUpdate(BaseModel):
    status: AttendanceStatus
    leave_type: LeaveType | None = None
    total_hours: float | None = None
