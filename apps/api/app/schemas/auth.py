from pydantic import BaseModel, Field

from app.core.constants import Role


class LoginRequest(BaseModel):
    employee_id: str
    pin: str = Field(min_length=4, max_length=8)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    employee_id: str
    full_name: str
    role: Role


class ChangePinRequest(BaseModel):
    current_pin: str = Field(min_length=4, max_length=8)
    new_pin: str = Field(min_length=4, max_length=8)


class ResetPinRequest(BaseModel):
    new_pin: str = Field(min_length=4, max_length=8)


class CurrentUser(BaseModel):
    employee_id: str
    role: Role
