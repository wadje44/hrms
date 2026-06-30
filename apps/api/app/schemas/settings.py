from pydantic import BaseModel, ConfigDict


class SettingsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    office_lat: float | None
    office_lng: float | None
    allowed_radius_m: float
    late_cutoff: str
    free_late_marks: int
    working_hours_per_day: float
    working_days_per_month: int
    holidays: list[str]


class SettingsUpdate(BaseModel):
    office_lat: float | None = None
    office_lng: float | None = None
    allowed_radius_m: float | None = None
    late_cutoff: str | None = None
    free_late_marks: int | None = None
    working_hours_per_day: float | None = None
    working_days_per_month: int | None = None
    holidays: list[str] | None = None
