from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import (
    CurrentUser,
    get_current_user,
    get_employee_or_404,
    require_admin,
)
from app.core.security import hash_pin
from app.db.session import get_db
from app.models.employee import Employee
from app.schemas.employee import EmployeeCreate, EmployeeOut, EmployeeUpdate

router = APIRouter(prefix="/employees", tags=["employees"])


@router.get("", response_model=list[EmployeeOut])
def list_employees(
    department: str | None = None,
    category: str | None = None,
    active: bool | None = None,
    _: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    q = db.query(Employee)
    if department:
        q = q.filter(Employee.department == department)
    if category:
        q = q.filter(Employee.category == category)
    if active is not None:
        q = q.filter(Employee.active.is_(active))
    return q.order_by(Employee.id).all()


@router.get("/me", response_model=EmployeeOut)
def get_me(user: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)):
    return get_employee_or_404(db, user.employee_id)


@router.post("", response_model=EmployeeOut, status_code=201)
def create_employee(
    payload: EmployeeCreate,
    _: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    if db.get(Employee, payload.id) is not None:
        raise HTTPException(status_code=409, detail="Employee ID already exists")
    data = payload.model_dump(exclude={"pin"})
    data["fixed_components"] = [c for c in data.get("fixed_components", [])]
    data["deductions"] = [d for d in data.get("deductions", [])]
    emp = Employee(**data, pin_hash=hash_pin(payload.pin))
    db.add(emp)
    db.commit()
    db.refresh(emp)
    return emp


@router.patch("/{employee_id}", response_model=EmployeeOut)
def update_employee(
    employee_id: str,
    payload: EmployeeUpdate,
    _: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    emp = get_employee_or_404(db, employee_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(emp, field, value)
    db.commit()
    db.refresh(emp)
    return emp


@router.delete("/{employee_id}", status_code=204)
def deactivate_employee(
    employee_id: str,
    _: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Soft-delete: deactivate (doc §6.2). Inactive employees drop out of attendance/payroll."""
    emp = get_employee_or_404(db, employee_id)
    emp.active = False
    db.commit()
