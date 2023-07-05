from typing import Optional

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    username: Optional[str]
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False


class UserInDB(UserBase):
    id: int = None

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str


class User(UserInDB):
    pass


class UserInDB(UserInDB):
    hashed_password: str
