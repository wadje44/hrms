"""Import all models here so Alembic autogenerate + Base.metadata see them."""

from app.models.attendance import AttendanceDay, AttendanceSession
from app.models.employee import Employee
from app.models.leave import LeaveBalance, LeaveRequest
from app.models.payroll import HourlyRateOverride, PayrollRecord
from app.models.settings import AppSettings

__all__ = [
    "Employee",
    "AttendanceDay",
    "AttendanceSession",
    "LeaveRequest",
    "LeaveBalance",
    "PayrollRecord",
    "HourlyRateOverride",
    "AppSettings",
]
