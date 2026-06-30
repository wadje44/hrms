"""FastAPI dependencies: current user + role-based access guards."""

from collections.abc import Callable

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.constants import Role
from app.core.security import decode_access_token
from app.models.employee import Employee
from app.schemas.auth import CurrentUser

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme)) -> CurrentUser:
    cred_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
    except jwt.PyJWTError as exc:
        raise cred_exc from exc
    emp_id = payload.get("sub")
    role = payload.get("role")
    if not emp_id or not role:
        raise cred_exc
    return CurrentUser(employee_id=emp_id, role=Role(role))


def require_roles(*roles: Role) -> Callable[[CurrentUser], CurrentUser]:
    def guard(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return user

    return guard


# Convenience guards
require_admin = require_roles(Role.ADMIN)
require_manager = require_roles(Role.ADMIN, Role.MANAGER)


def get_employee_or_404(db: Session, employee_id: str) -> Employee:
    emp = db.get(Employee, employee_id)
    if emp is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return emp
