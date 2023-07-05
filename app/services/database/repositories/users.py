from fastapi import HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError

from app.services.database.models import user
from app.services.database.repositories.base import BaseCrud
from app.services.database.schemas.users import User, UserCreate
from app.services.security.password_security import (get_password_hash,
                                                     verify_password)


class UserCrud(BaseCrud):
    model = user.User

    async def get_by_id(self, id: int):
        stmt = (select(self.model).where(self.model.id == id))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str):
        stmt = (select(self.model).where(self.model.username == username))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_user(self, user: UserCreate):
        new_user_data = user.dict()
        password = new_user_data.pop('password')
        new_user_data['hashed_password'] = get_password_hash(password)
        user = self.model(**new_user_data)
        self.session.add(user)
        try:
            await self.session.commit()
            await self.session.refresh(user)
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='User already exist'
            )
        return user

    async def authenticate_user(
        self,
        username: str,
        password: str,
    ) -> User:
        user = await self.get_by_username(username)
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Incorrect username or password.'
            )
        return user

    async def activate_user(self, email: str):
        stmt = (
            update(self.model)
            .where(self.model.email == email)
            .values(is_active=True)
        )
        await self.session.execute(stmt)
        await self.session.commit()
