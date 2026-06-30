from datetime import date as date_type
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import AttendanceStatus, LeaveType, SessionType
from app.db.base import Base


class AttendanceDay(Base):
    """One row per employee per calendar day (doc §8.2)."""

    __tablename__ = "attendance_days"
    __table_args__ = (UniqueConstraint("employee_id", "date", name="uq_attendance_emp_date"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    employee_id: Mapped[str] = mapped_column(ForeignKey("employees.id"), nullable=False, index=True)
    date: Mapped[date_type] = mapped_column(Date, nullable=False, index=True)

    status: Mapped[AttendanceStatus] = mapped_column(String(16), default=AttendanceStatus.ABSENT)
    leave_type: Mapped[LeaveType | None] = mapped_column(String(8), nullable=True)

    total_hours: Mapped[float] = mapped_column(Numeric(6, 2), default=0)
    paid_hours: Mapped[float] = mapped_column(Numeric(6, 2), default=0)

    is_wfh: Mapped[bool] = mapped_column(Boolean, default=False)
    is_field_duty: Mapped[bool] = mapped_column(Boolean, default=False)
    is_late: Mapped[bool] = mapped_column(Boolean, default=False)

    # True when an admin manually set the status (skip auto-recompute on punch).
    manual_override: Mapped[bool] = mapped_column(Boolean, default=False)

    employee = relationship("Employee", back_populates="attendance_days")
    sessions = relationship(
        "AttendanceSession",
        back_populates="day",
        cascade="all, delete-orphan",
        order_by="AttendanceSession.punch_in",
    )


class AttendanceSession(Base):
    """A single punch-in/punch-out pair (doc §8.1, §8.6)."""

    __tablename__ = "attendance_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    day_id: Mapped[int] = mapped_column(
        ForeignKey("attendance_days.id"), nullable=False, index=True
    )
    punch_in: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    punch_out: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    lng: Mapped[float | None] = mapped_column(Float, nullable=True)
    type: Mapped[SessionType] = mapped_column(String(8), default=SessionType.OFFICE)

    day = relationship("AttendanceDay", back_populates="sessions")
