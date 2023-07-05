from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from app.services.database.models.base import Base


class User(Base):

    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False, unique=True)
    hashed_password: str = Column(String(length=1024), nullable=False)
    email = Column(String, nullable=False, unique=True)
    is_active: bool = Column(Boolean, default=False, nullable=False)
    is_superuser: bool = Column(Boolean, default=False, nullable=False)
    posts = relationship('Post', back_populates='owner')
    likes = relationship('Like', back_populates='user')
