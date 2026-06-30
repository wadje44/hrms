"""Business constants and enums derived from the requirements doc."""

from enum import StrEnum


class Category(StrEnum):
    OFFICE = "office"
    HYBRID = "hybrid"
    FIELD = "field"  # Field / Warehouse
    SERVICE = "service"


class Role(StrEnum):
    ADMIN = "admin"
    MANAGER = "manager"
    EMPLOYEE = "employee"


class AttendanceStatus(StrEnum):
    PRESENT = "present"
    ABSENT = "absent"
    LEAVE = "leave"
    HOLIDAY = "holiday"
    HALF_DAY = "half_day"


class SessionType(StrEnum):
    OFFICE = "office"
    WFH = "wfh"
    FIELD = "field"


class LeaveType(StrEnum):
    EL = "EL"  # Earned Leave (paid)
    ML = "ML"  # Medical Leave (paid)
    FL = "FL"  # Festival Leave (paid)
    DL = "DL"  # Duty Leave (paid)
    DL2 = "DL2"  # Duty Leave 2 (paid)
    UL = "UL"  # Unpaid Leave


PAID_LEAVE_TYPES = {LeaveType.EL, LeaveType.ML, LeaveType.FL, LeaveType.DL, LeaveType.DL2}
BALANCE_LEAVE_TYPES = PAID_LEAVE_TYPES  # UL has no balance

# Categories that require GPS validation against office coordinates (on office days).
GPS_VALIDATED_CATEGORIES = {Category.OFFICE, Category.HYBRID}

# Defaults for the app-level settings singleton.
DEFAULT_ALLOWED_RADIUS_M = 250.0
DEFAULT_LATE_CUTOFF = "10:20"  # HH:MM, local
DEFAULT_FREE_LATE_MARKS = 3
DEFAULT_WORKING_HOURS_PER_DAY = 8.0
DEFAULT_WORKING_DAYS_PER_MONTH = 26
LATE_MARK_DEDUCTION_HOURS = 1.0  # per late mark beyond the free allowance

EARTH_RADIUS_M = 6371000.0
