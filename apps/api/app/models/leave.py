from datetime import date as date_type
from datetime import datetime

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import LeaveType
from app.db.base import Base


class LeaveRequest(Base):
    """Leave request lifecycle (doc §10.2)."""

    __tablename__ = "leave_requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    employee_id: Mapped[str] = mapped_column(ForeignKey("employees.id"), nullable=False, index=True)
    date_from: Mapped[date_type] = mapped_column(Date, nullable=False)
    date_to: Mapped[date_type] = mapped_column(Date, nullable=False)
    leave_type: Mapped[LeaveType] = mapped_column(String(8), nullable=False)
    reason: Mapped[str] = mapped_column(Text, default="")

    status: Mapped[str] = mapped_column(String(12), default="pending", index=True)
    reviewed_by: Mapped[str | None] = mapped_column(ForeignKey("employees.id"), nullable=True)
    review_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    comment: Mapped[str] = mapped_column(Text, default="")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    employee = relationship("Employee", foreign_keys=[employee_id])


class LeaveBalance(Base):
    """Per-employee remaining balance for each paid leave type (doc §10.3)."""

    __tablename__ = "leave_balances"
    __table_args__ = (UniqueConstraint("employee_id", "leave_type", name="uq_balance_emp_type"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    employee_id: Mapped[str] = mapped_column(ForeignKey("employees.id"), nullable=False, index=True)
    leave_type: Mapped[LeaveType] = mapped_column(String(8), nullable=False)
    balance: Mapped[int] = mapped_column(Integer, default=0)

    employee = relationship("Employee", back_populates="leave_balances")
