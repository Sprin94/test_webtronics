from sqlalchemy import delete, func, select, update
from sqlalchemy.orm import joinedload

from app.services.database.models import posts
from app.services.database.repositories.base import BaseCrud
from app.services.database.schemas.posts import (LikeInDB, PostBase, PostInDB,
                                                 PostUpdate)


class PostCrud(BaseCrud):
    model = posts.Post

    async def create(self, data: PostBase) -> PostInDB | None:
        post = self.model(**data.dict())
        self.session.add(post)
        await self.session.commit()
        await self.session.refresh(post)
        return post

    async def update(self, post_id: int, new_data: PostUpdate) -> PostInDB:
        stmt = (update(self.model)
                .where(self.model.id == post_id)
                .values(**new_data.dict(exclude_none=True))
                .returning(self.model))
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar()

    async def get_with_likes(self, post_id: int):
        stmt = (select(self.model)
                .where(self.model.id == post_id)
                .options(joinedload(self.model.likes))
                )
        result = await self.session.scalar(stmt)
        return result


class LikeCrud(BaseCrud):
    model = posts.Like

    async def get_posts_likes(self, post_id: int):
        stmt = select(self.model).where(post_id == post_id)
        result = await self.session.scalars(stmt)
        return result.all()

    async def create(self, user_id: int, post_id: int, value: int) -> PostInDB:
        like = self.model(user_id=user_id, post_id=post_id, value=value)
        self.session.add(like)
        await self.session.commit()
        await self.session.refresh(like)
        return like

    async def update(self, user_id: int, post_id: int, value: int) -> PostInDB:
        stmt = (update(self.model)
                .where(self.model.user_id == user_id, self.model.post_id == post_id)
                .values(value=value)
                .returning(self.model))
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar()

    async def delete(self, user_id: int, post_id: int) -> bool | None:
        stmt = delete(self.model).where(
            self.model.user_id == user_id,
            self.model.post_id == post_id,
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        if result.rowcount:
            return True
        return False
