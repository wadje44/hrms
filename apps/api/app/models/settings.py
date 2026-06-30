from sqlalchemy import JSON, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.constants import (
    DEFAULT_ALLOWED_RADIUS_M,
    DEFAULT_FREE_LATE_MARKS,
    DEFAULT_LATE_CUTOFF,
    DEFAULT_WORKING_DAYS_PER_MONTH,
    DEFAULT_WORKING_HOURS_PER_DAY,
)
from app.db.base import Base


class AppSettings(Base):
    """App-level settings singleton (doc §16.1 hrms/settings). Always id=1."""

    __tablename__ = "app_settings"

    id: Mapped[int] = mapped_column(primary_key=True, default=1)
    office_lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    office_lng: Mapped[float | None] = mapped_column(Float, nullable=True)
    allowed_radius_m: Mapped[float] = mapped_column(Float, default=DEFAULT_ALLOWED_RADIUS_M)
    late_cutoff: Mapped[str] = mapped_column(String(5), default=DEFAULT_LATE_CUTOFF)  # "HH:MM"
    free_late_marks: Mapped[int] = mapped_column(Integer, default=DEFAULT_FREE_LATE_MARKS)
    working_hours_per_day: Mapped[float] = mapped_column(
        Float, default=DEFAULT_WORKING_HOURS_PER_DAY
    )
    working_days_per_month: Mapped[int] = mapped_column(
        Integer, default=DEFAULT_WORKING_DAYS_PER_MONTH
    )
    # List of holiday dates as ISO strings "YYYY-MM-DD".
    holidays: Mapped[list] = mapped_column(JSON, default=list)
