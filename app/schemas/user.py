import uuid
from pydantic import BaseModel, EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    name: str
    email: EmailStr
    phone: PhoneNumber
    birthday: Optional[datetime]
    timezone: str


class UserResponse(UserBase):
    id: uuid.UUID
    is_active: bool = True
    avatar_url: Optional[str]

    class Config:
        from_attributes = True

class UserAuth(BaseModel):
    email: EmailStr
    password: str

class UserCreate(UserBase):
    password: str
