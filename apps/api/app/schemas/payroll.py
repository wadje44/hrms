from pydantic import BaseModel, ConfigDict


class PayslipOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    month: str
    employee_id: str
    gross: float
    deductions_total: float
    net: float
    breakdown: dict


class RateOverrideIn(BaseModel):
    employee_id: str
    hourly_rate: float


class PayrollSummaryRow(BaseModel):
    employee_id: str
    full_name: str
    department: str
    present_days: int
    late_marks: int
    worked_hours: float
    gross: float
    deductions_total: float
    net: float
