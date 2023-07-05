from enum import IntEnum

from sqlalchemy import (Column, Enum, ForeignKey, Integer, String,
                        UniqueConstraint)
from sqlalchemy.orm import relationship

from app.services.database.models.base import Base


class Post(Base):
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    text = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    owner = relationship('User', back_populates='posts')
    likes = relationship('Like', back_populates='post')


class Like(Base):
    class LikeValue(IntEnum):
        DISLIKE = -1
        LIKE = 1

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    post_id = Column(Integer, ForeignKey('posts.id', ondelete='CASCADE'), nullable=False)
    value = Column(Enum(LikeValue))
    user = relationship('User', back_populates='likes')
    post = relationship('Post', back_populates='likes')

    __table_args__ = (
        UniqueConstraint('user_id', 'post_id', name='unique_likes'),
    )
