from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str]
    birthday: Optional[datetime]
    avatar_url: Optional[str]
    timezone: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool = True

    class Config:
        from_attributes = True

class UserInDB(User):
    hashed_password: str