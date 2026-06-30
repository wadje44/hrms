from pydantic import BaseModel

from app.core.constants import LeaveType


class EmployeeRef(BaseModel):
    employee_id: str
    full_name: str
    detail: str = ""  # e.g. punch-in time, leave type


class DashboardSummary(BaseModel):
    date: str
    present: list[EmployeeRef]
    absent: list[EmployeeRef]
    late: list[EmployeeRef]
    on_leave: list[EmployeeRef]
    currently_in: list[EmployeeRef]


class OnLeaveRef(EmployeeRef):
    leave_type: LeaveType | None = None
