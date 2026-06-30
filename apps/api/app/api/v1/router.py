from fastapi import APIRouter

from app.api.v1.routers import (
    attendance,
    auth,
    dashboard,
    employees,
    leaves,
    payroll,
    settings,
)

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(employees.router)
api_router.include_router(attendance.router)
api_router.include_router(leaves.router)
api_router.include_router(payroll.router)
api_router.include_router(dashboard.router)
api_router.include_router(settings.router)
