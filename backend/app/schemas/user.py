from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.user import RoleEnum


class UserBase(BaseModel):
    username: str
    email: str
    role: RoleEnum = RoleEnum.OPERATOR


class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: Optional[RoleEnum] = RoleEnum.OPERATOR


class UserUpdate(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None
    role: Optional[RoleEnum] = None
    is_active: Optional[bool] = None


class UserOut(BaseModel):
    id: str
    username: str
    email: str
    role: RoleEnum
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
