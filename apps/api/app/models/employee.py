from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import Category, Role
from app.db.base import Base


class Employee(Base):
    __tablename__ = "employees"

    # Employee ID is the primary key throughout the system (e.g. EMP001).
    id: Mapped[str] = mapped_column(String(16), primary_key=True)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str | None] = mapped_column(String(180), unique=True, nullable=True)
    department: Mapped[str] = mapped_column(String(60), nullable=False)
    category: Mapped[Category] = mapped_column(String(16), nullable=False)
    designation: Mapped[str] = mapped_column(String(120), default="")
    role: Mapped[Role] = mapped_column(String(16), default=Role.EMPLOYEE, nullable=False)

    # Pay configuration
    monthly_salary: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    hourly_rate: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    # Lists of {"name": str, "amount": number}
    fixed_components: Mapped[list] = mapped_column(JSON, default=list)
    deductions: Mapped[list] = mapped_column(JSON, default=list)

    # Attendance configuration
    wfh_limit: Mapped[int] = mapped_column(Integer, default=0)  # per month, Hybrid only
    free_punch: Mapped[bool] = mapped_column(Boolean, default=False)  # bypass GPS
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    pin_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    attendance_days = relationship(
        "AttendanceDay", back_populates="employee", cascade="all, delete-orphan"
    )
    leave_balances = relationship(
        "LeaveBalance", back_populates="employee", cascade="all, delete-orphan"
    )
