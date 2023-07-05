import json

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.exc import IntegrityError
from fastapi_cache.backends.redis import RedisCacheBackend

from app.services.database.schemas.posts import (
    PostInDB, PostBase, PostCreate, PostUpdate, PostInDBLikes, LikeCreate, LikeInDB
)
from app.services.database.schemas.users import UserInDB
from app.services.database.repositories.posts import PostCrud, LikeCrud
from app.services.security.permissions import get_current_active_user, is_post_author
from app.utils.cache import redis_cache

router = APIRouter()


LIKE_CACHE_KEY = 'likes:{post_id}'


@router.get('/posts', response_model=list[PostInDB])
async def get_posts_list(posts_crud: PostCrud = Depends()):
    posts = await posts_crud.get_list()
    return posts


@router.post('/posts', response_model=PostInDB)
async def create_post(
    data: PostCreate,
    posts_crud: PostCrud = Depends(),
    user: UserInDB = Depends(get_current_active_user),
):
    post = await posts_crud.create(
        PostBase(**data.dict(),
                 owner_id=user.id,)
    )
    return post


@router.patch('/posts/{post_id}', response_model=PostInDB)
async def update_post(
    data: PostUpdate,
    post_id: int,
    posts_crud: PostCrud = Depends(),
    user: UserInDB = Depends(is_post_author),
):
    post = await posts_crud.update(
        post_id=post_id,
        new_data=data
    )
    return post


@router.delete('/posts/{post_id}', response_model=PostInDB)
async def delete_post(
    post_id: int,
    posts_crud: PostCrud = Depends(),
    user: UserInDB = Depends(is_post_author),
):
    post = await posts_crud.delete(post_id=post_id)
    return post


@router.get('/posts/{post_id}', response_model=PostInDBLikes)
async def get_post(
    post_id: int,
    posts_crud: PostCrud = Depends()
) -> PostInDBLikes:
    post = await posts_crud.get_with_likes(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Post not found',
        )
    return post


@router.post('/posts/{post_id}/likes')
async def add_like(
    post_id: int,
    data: LikeCreate,
    posts_crud: PostCrud = Depends(),
    like_crud: LikeCrud = Depends(),
    user: UserInDB = Depends(get_current_active_user),
    cache: RedisCacheBackend = Depends(redis_cache)
):
    post = await posts_crud.get_by_id(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Post not found',
        )
    if post.owner_id == user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='you cant like your posts',
        )

    like = await like_crud.update(user.id, post_id, data.value)
    if not like:
        await like_crud.create(user.id, post_id, data.value)
    await cache.delete(LIKE_CACHE_KEY.format(post_id=post_id))
    return {'message': 'Successfully like'}


@router.delete('/posts/{post_id}/likes')
async def delete_like(
    post_id: int,
    posts_crud: PostCrud = Depends(),
    like_crud: LikeCrud = Depends(),
    user: UserInDB = Depends(get_current_active_user),
    cache: RedisCacheBackend = Depends(redis_cache),
):
    post = await posts_crud.get_by_id(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Post not found',
        )
    is_deleted = await like_crud.delete(user.id, post_id)
    if is_deleted:
        await cache.delete(LIKE_CACHE_KEY.format(post_id=post_id))
        return {'message': 'Like deleted'}
    return {'message': 'you havent liked yet'}


@router.get('/posts/{post_id}/likes')
async def get_likes(
    post_id: int,
    posts_crud: PostCrud = Depends(),
    like_crud: LikeCrud = Depends(),
    cache: RedisCacheBackend = Depends(redis_cache)
):
    key = LIKE_CACHE_KEY.format(post_id=post_id)
    in_cache = await cache.get(key)
    if not in_cache:
        post = await posts_crud.get_by_id(post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Post not found',
            )
        likes = await like_crud.get_posts_likes(post_id)
        likes = [LikeInDB.from_orm(like).dict() for like in likes]
        await cache.set(key, json.dumps(likes))
    else:
        in_cache = json.loads(in_cache)
    return in_cache or likes
