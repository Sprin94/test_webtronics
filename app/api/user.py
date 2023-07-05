import asyncio

from datetime import timedelta
from fastapi import APIRouter, Form, HTTPException, status, Depends, Query

from app.core.config import settings
from app.services.security.jwt import create_access_token
from app.services.database.schemas.tokens import Token
from app.services.database.schemas.users import UserCreate, User, UserInDB
from app.services.database.repositories.users import UserCrud
from app.services.security.permissions import get_current_active_user
from app.utils.check_email import check_email

router = APIRouter()


@router.post('/token', response_model=Token)
async def login_for_access_token(
    username: str = Form(),
    password: str = Form(),
    crud: UserCrud = Depends()
):
    user = await crud.authenticate_user(username=username, password=password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    access_token = create_access_token(
        data={'user_id': user.id}, expires_delta=access_token_expires
    )
    return {'access_token': access_token, 'token_type': 'bearer'}


@router.post('/sign-up', response_model=User, status_code=status.HTTP_201_CREATED)
async def user_registration(
    user: UserCreate,
    crud: UserCrud = Depends()
):
    user = await crud.create_user(user)
    asyncio.create_task(check_email(user.email, crud))
    return user


@router.get('/users', response_model=list[User])
async def users_list(
    crud: UserCrud = Depends(),
    current_user: UserInDB = Depends(get_current_active_user)
):
    users = await crud.get_list()
    return users
