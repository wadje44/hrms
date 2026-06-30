from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.constants import BALANCE_LEAVE_TYPES
from app.core.deps import (
    CurrentUser,
    get_current_user,
    get_employee_or_404,
    require_admin,
    require_manager,
)
from app.db.session import get_db
from app.models.leave import LeaveBalance, LeaveRequest
from app.schemas.leave import (
    LeaveBalanceAdjust,
    LeaveBalanceOut,
    LeaveCreate,
    LeaveOut,
    LeaveReview,
)
from app.services import leave_service

router = APIRouter(prefix="/leaves", tags=["leaves"])


@router.post("", response_model=LeaveOut, status_code=201)
def apply_leave(
    payload: LeaveCreate,
    user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return leave_service.create_request(db, user.employee_id, payload)


@router.get("/me", response_model=list[LeaveOut])
def my_leaves(user: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)):
    return (
        db.query(LeaveRequest)
        .filter(LeaveRequest.employee_id == user.employee_id)
        .order_by(LeaveRequest.created_at.desc())
        .all()
    )


@router.get("/pending", response_model=list[LeaveOut])
def pending_leaves(_: CurrentUser = Depends(require_manager), db: Session = Depends(get_db)):
    return (
        db.query(LeaveRequest)
        .filter(LeaveRequest.status == "pending")
        .order_by(LeaveRequest.created_at)
        .all()
    )


@router.post("/{leave_id}/review", response_model=LeaveOut)
def review_leave(
    leave_id: int,
    payload: LeaveReview,
    user: CurrentUser = Depends(require_manager),
    db: Session = Depends(get_db),
):
    req = db.get(LeaveRequest, leave_id)
    if req is None:
        raise HTTPException(status_code=404, detail="Leave request not found")
    return leave_service.review_request(db, req, user.employee_id, payload.approve, payload.comment)


@router.get("/balances/me", response_model=list[LeaveBalanceOut])
def my_balances(user: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(LeaveBalance).filter(LeaveBalance.employee_id == user.employee_id).all()


@router.get("/balances/{employee_id}", response_model=list[LeaveBalanceOut])
def employee_balances(
    employee_id: str, _: CurrentUser = Depends(require_admin), db: Session = Depends(get_db)
):
    return db.query(LeaveBalance).filter(LeaveBalance.employee_id == employee_id).all()


@router.put("/balances/{employee_id}", response_model=LeaveBalanceOut)
def adjust_balance(
    employee_id: str,
    payload: LeaveBalanceAdjust,
    _: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    get_employee_or_404(db, employee_id)
    if payload.leave_type not in BALANCE_LEAVE_TYPES:
        raise HTTPException(status_code=400, detail="UL has no balance")
    bal = leave_service.get_balance(db, employee_id, payload.leave_type)
    if bal is None:
        bal = LeaveBalance(employee_id=employee_id, leave_type=payload.leave_type)
        db.add(bal)
    bal.balance = payload.balance
    db.commit()
    db.refresh(bal)
    return bal
