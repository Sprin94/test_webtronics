import uvicorn
from fastapi import FastAPI
from fastapi_cache import caches
from fastapi_cache.backends.redis import CACHE_KEY, RedisCacheBackend

from app.api.posts import router as posts_router
from app.api.user import router as user_router
from app.core.config import settings

app = FastAPI()
app.include_router(user_router)
app.include_router(posts_router)


@app.on_event('startup')
async def on_startup() -> None:
    rc = RedisCacheBackend(settings.REDIS_URI)
    caches.set(CACHE_KEY, rc)


def main():
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)


if __name__ == '__main__':
    main()
