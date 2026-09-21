from datetime import date as date_type
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class WfhCreate(BaseModel):
    date_from: date_type
    date_to: date_type
    reason: str = ""


class WfhReview(BaseModel):
    approve: bool
    comment: str = ""


class WfhOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    employee_id: str
    date_from: date_type
    date_to: date_type
    reason: str
    status: str
    reviewed_by: str | None
    review_date: datetime | None
    comment: str
    created_at: datetime
