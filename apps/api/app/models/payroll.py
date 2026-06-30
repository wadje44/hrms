from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PayrollRecord(Base):
    """Stored payslip per employee-month (doc §11.3). month = 'YYYY-MM'."""

    __tablename__ = "payroll_records"
    __table_args__ = (UniqueConstraint("month", "employee_id", name="uq_payroll_month_emp"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    month: Mapped[str] = mapped_column(String(7), nullable=False, index=True)
    employee_id: Mapped[str] = mapped_column(ForeignKey("employees.id"), nullable=False, index=True)

    gross: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    deductions_total: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    net: Mapped[float] = mapped_column(Numeric(12, 2), default=0)

    # Full itemized payslip snapshot (doc §11.5).
    breakdown: Mapped[dict] = mapped_column(JSON, default=dict)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class HourlyRateOverride(Base):
    """Per-employee, per-month hourly rate override (doc §11.4)."""

    __tablename__ = "hourly_rate_overrides"
    __table_args__ = (UniqueConstraint("month", "employee_id", name="uq_override_month_emp"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    month: Mapped[str] = mapped_column(String(7), nullable=False, index=True)
    employee_id: Mapped[str] = mapped_column(ForeignKey("employees.id"), nullable=False, index=True)
    hourly_rate: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
