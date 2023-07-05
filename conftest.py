import asyncio
import random
import string
from datetime import timedelta
from typing import AsyncGenerator

import pytest
from fastapi.testclient import TestClient
from fastapi_cache import caches
from fastapi_cache.backends.memory import CACHE_KEY, InMemoryCacheBackend
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.main import app
from app.services.database.models.base import Base
from app.services.database.models.posts import Post
from app.services.database.models.user import User
from app.services.database.repositories.users import UserCrud
from app.services.database.session import get_session
from app.services.security.jwt import create_access_token
from app.services.security.password_security import get_password_hash
from app.utils.cache import redis_cache

metadata = Base.metadata

# DB
DATABASE_URL_TEST = (
    f'postgresql+asyncpg://{settings.TEST_POSTGRES_USER}:'
    f'{settings.TEST_POSTGRES_PASSWORD}@{settings.TEST_POSTGRES_SERVER}'
    f':{settings.TEST_POSTGRES_PORT}/{settings.TEST_POSTGRES_DB}')

engine_test = create_async_engine(DATABASE_URL_TEST, poolclass=NullPool)
async_session_maker = sessionmaker(
    engine_test,
    class_=AsyncSession,
    expire_on_commit=False
)
metadata.bind = engine_test


async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


# CACHE
@pytest.fixture(autouse=True, scope='session')
def mock_cache():
    mc = InMemoryCacheBackend()
    caches.set(CACHE_KEY, mc)


def memory_cache():
    return caches.get(CACHE_KEY)


# DI
app.dependency_overrides[get_session] = override_get_session
app.dependency_overrides[redis_cache] = memory_cache


@pytest.fixture(autouse=True, scope='session')
async def prepare_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(metadata.drop_all)


@pytest.fixture(scope='session')
async def user():
    async with async_session_maker() as session:
        hashed_password = get_password_hash('user')
        user = User(
            email='test@email.com',
            username='user',
            hashed_password=hashed_password,
            is_active=True,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


@pytest.fixture(scope='function')
async def not_active_user():
    random_str = ''.join(random.choice(string.ascii_letters) for _ in range(10))
    async with async_session_maker() as session:
        hashed_password = get_password_hash('user')
        user = User(
            email=f'{random_str}@email.com',
            username=random_str,
            hashed_password=hashed_password,
            is_active=False,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


@pytest.fixture(scope='session')
async def user_2():
    async with async_session_maker() as session:
        hashed_password = get_password_hash('user')
        user = User(
            email='test_2@email.com',
            username='user_2',
            hashed_password=hashed_password,
            is_active=True,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


@pytest.fixture(scope='session')
async def user_2_post(user_2):
    async with async_session_maker() as session:
        post = Post(
            title='test',
            text='test_text',
            owner_id=user_2.id,
        )
        session.add(post)
        await session.commit()
        await session.refresh(post)
        return post


@pytest.fixture(scope='session')
def event_loop(request):
    '''Create an instance of the default event loop for each test case.'''
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='function')
def client() -> TestClient:
    yield TestClient(app)


@pytest.fixture(scope='session')
def auth_client(user) -> TestClient:
    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    token = create_access_token(
        data={'user_id': user.id}, expires_delta=access_token_expires
    )
    headers = {
        'Authorization': f'Bearer {token}'
    }
    yield TestClient(app, headers=headers)


@pytest.fixture(scope='function')
async def user_crud() -> UserCrud:
    async with async_session_maker() as session:
        yield UserCrud(session)
