from pydantic import BaseModel, EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    name: str
    email: EmailStr
    phone: PhoneNumber
    birthday: Optional[datetime]
    avatar_url: Optional[str]
    timezone: str


class UserResponse(UserBase):
    id: int
    is_active: bool = True

    class Config:
        from_attributes = True

class UserAuth:
    email: EmailStr
    password: str

class UserCreate(UserBase):
    password: str