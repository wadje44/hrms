from pydantic import BaseModel


class MonthlyReportSummary(BaseModel):
    month: str
    present: int = 0
    absent: int = 0
    late: int = 0
    leave: int = 0
    wfh: int = 0
    avg_hours: float = 0.0


class YtdEarningsRow(BaseModel):
    employee_id: str
    full_name: str
    ytd_earnings: float = 0.0
