from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class UserBase(BaseModel):
    email: str
    full_name: str
    is_active: Optional[bool] = True

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    role_name: Optional[str] = "EMPLOYEE"

class UserLogin(BaseModel):
    email: str
    password: str

class RoleResponse(BaseModel):
    id: int
    name: str
    can_manage_users: bool
    can_manage_projects: bool
    can_invoke_agents: bool

    model_config = ConfigDict(from_attributes=True)

class UserResponse(UserBase):
    id: int
    created_at: Optional[datetime] = None
    role: Optional[RoleResponse] = None

    model_config = ConfigDict(from_attributes=True)

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: Optional[UserResponse] = None

class RefreshTokenRequest(BaseModel):
    refresh_token: str
