from typing import ClassVar, Type, TypeVar

from fastapi import Depends
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.database.session import get_session

Model = TypeVar('Model')


class BaseCrud:
    model: ClassVar[Type[Model]]

    def __init__(self, db: AsyncSession = Depends(get_session)):
        self.session = db

    async def get_list(self) -> list[Model]:
        stmt = select(self.model)
        result = await self.session.scalars(stmt)
        return result.all()

    async def get_by_id(self, id: int) -> Model:
        stmt = select(self.model).where(self.model.id == id)
        result = await self.session.scalar(stmt)
        return result

    async def delete(self, id: int):
        stmt = delete(self.model).where(self.model.id == id)
        result = await self._session.execute(stmt)
        await self.session.commit()
        if result.rowcount:
            return True
        return None
