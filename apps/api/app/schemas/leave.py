from datetime import date as date_type
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.core.constants import LeaveType


class LeaveCreate(BaseModel):
    date_from: date_type
    date_to: date_type
    leave_type: LeaveType
    reason: str = ""


class LeaveReview(BaseModel):
    approve: bool
    comment: str = ""


class LeaveOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    employee_id: str
    date_from: date_type
    date_to: date_type
    leave_type: LeaveType
    reason: str
    status: str
    reviewed_by: str | None
    review_date: datetime | None
    comment: str
    created_at: datetime


class LeaveBalanceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    leave_type: LeaveType
    balance: int


class LeaveBalanceAdjust(BaseModel):
    leave_type: LeaveType
    balance: int
