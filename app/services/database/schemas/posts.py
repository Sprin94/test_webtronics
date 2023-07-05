from typing import Any, Optional

from pydantic import BaseModel, validator


class PostBase(BaseModel):
    title: str
    text: str
    owner_id: int


class PostCreate(BaseModel):
    title: str
    text: str


class PostUpdate(BaseModel):
    title: Optional[str]
    text: Optional[str]


class PostInDB(PostBase):
    id: int

    class Config:
        orm_mode = True


class LikeBase(BaseModel):
    user_id: int
    post_id: int
    value: int


class LikeInDB(LikeBase):
    id: int

    class Config:
        orm_mode = True


class LikeCreate(BaseModel):
    value: int

    @validator('value')
    def check_allowed_values(cls, value):
        if value not in (-1, 1):
            raise ValueError('Only -1 or 1 are allowed')
        return value


class PostInDBLikes(PostInDB):
    likes: list[LikeInDB]

    class Config:
        orm_mode = True
