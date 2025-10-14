from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from ..db.models import UserRole, ItemType, InteractionType, DifficultyLevel

class UserBase(BaseModel):
    email: EmailStr
    username: str
    role: Optional[UserRole] = UserRole.USER

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

class UserInDB(User):
    hashed_password: str