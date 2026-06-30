from pydantic import BaseModel, ConfigDict, Field

from app.core.constants import Category, Role


class PayComponent(BaseModel):
    name: str
    amount: float


class EmployeeBase(BaseModel):
    full_name: str
    email: str | None = None
    department: str
    category: Category
    designation: str = ""
    role: Role = Role.EMPLOYEE
    monthly_salary: float = 0
    hourly_rate: float | None = None
    fixed_components: list[PayComponent] = Field(default_factory=list)
    deductions: list[PayComponent] = Field(default_factory=list)
    wfh_limit: int = 0
    free_punch: bool = False
    active: bool = True


class EmployeeCreate(EmployeeBase):
    id: str
    pin: str = Field(min_length=4, max_length=8)


class EmployeeUpdate(BaseModel):
    full_name: str | None = None
    email: str | None = None
    department: str | None = None
    category: Category | None = None
    designation: str | None = None
    role: Role | None = None
    monthly_salary: float | None = None
    hourly_rate: float | None = None
    fixed_components: list[PayComponent] | None = None
    deductions: list[PayComponent] | None = None
    wfh_limit: int | None = None
    free_punch: bool | None = None
    active: bool | None = None


class EmployeeOut(EmployeeBase):
    """PIN/hash never exposed (doc §17 data privacy)."""

    model_config = ConfigDict(from_attributes=True)
    id: str


class EmployeePublic(BaseModel):
    """Minimal info for the login dropdown — no pay/PIN data."""

    model_config = ConfigDict(from_attributes=True)
    id: str
    full_name: str
