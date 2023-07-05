from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.services.database.repositories.users import UserCrud
from app.services.database.repositories.posts import PostCrud

from app.services.security.jwt import ALGORITHM
from app.core.config import settings
from app.services.database.schemas.tokens import TokenPayload
from app.services.database.schemas.users import UserInDB


reusable_oauth2 = OAuth2PasswordBearer(tokenUrl='token')


async def get_current_user(
        crud: UserCrud = Depends(),
        token: str = Depends(reusable_oauth2),
) -> UserInDB:
    try:
        payload = jwt.decode(token,
                             settings.SECRET_KEY,
                             algorithms=[ALGORITHM])
        token_data = TokenPayload(**payload)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Could not validate credentials'
        )
    user = await crud.get_by_id(token_data.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Bad token')
    return user


async def get_current_active_user(
        current_user: UserInDB = Depends(get_current_user),
        crud: UserCrud = Depends()
) -> UserInDB:
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Inactive user')
    return current_user


async def get_current_active_superuser(
        current_user: UserInDB = Depends(get_current_user),
        crud: UserCrud = Depends()
) -> UserInDB:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='The user doesnt have enough privileges'
        )
    return current_user


async def is_post_author(
        post_id: int,
        post_crud: PostCrud = Depends(),
        current_user=Depends(get_current_active_user)
) -> UserInDB:
    post = await post_crud.get_by_id(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Post not found'
        )
    if post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Not authorized'
        )
    return current_user
