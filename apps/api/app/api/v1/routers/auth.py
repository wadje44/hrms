from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.constants import Role
from app.core.deps import get_current_user, get_employee_or_404, require_admin
from app.core.security import create_access_token, hash_pin, verify_pin
from app.db.session import get_db
from app.models.employee import Employee
from app.schemas.auth import (
    ChangePinRequest,
    CurrentUser,
    LoginRequest,
    ResetPinRequest,
    TokenResponse,
)
from app.schemas.employee import EmployeePublic

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/employees", response_model=list[EmployeePublic])
def login_directory(db: Session = Depends(get_db)):
    """Names + IDs for the login dropdown (doc §5.1). No sensitive data."""
    return db.query(Employee).filter(Employee.active.is_(True)).order_by(Employee.full_name).all()


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    emp = db.get(Employee, payload.employee_id)
    if emp is None or not emp.active or not verify_pin(payload.pin, emp.pin_hash):
        raise HTTPException(status_code=401, detail="Invalid employee ID or PIN")
    token = create_access_token(subject=emp.id, role=emp.role)
    return TokenResponse(
        access_token=token, employee_id=emp.id, full_name=emp.full_name, role=Role(emp.role)
    )


@router.post("/change-pin", status_code=204)
def change_pin(
    payload: ChangePinRequest,
    user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    emp = get_employee_or_404(db, user.employee_id)
    if not verify_pin(payload.current_pin, emp.pin_hash):
        raise HTTPException(status_code=400, detail="Current PIN is incorrect")
    emp.pin_hash = hash_pin(payload.new_pin)
    db.commit()


@router.post("/employees/{employee_id}/reset-pin", status_code=204)
def reset_pin(
    employee_id: str,
    payload: ResetPinRequest,
    _: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    emp = get_employee_or_404(db, employee_id)
    emp.pin_hash = hash_pin(payload.new_pin)
    db.commit()
