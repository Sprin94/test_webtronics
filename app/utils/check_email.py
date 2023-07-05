import asyncio

import httpx
from fastapi import status

from app.core.config import settings
from app.services.database.repositories.users import UserCrud

API_ENDPOINT = 'https://api.hunter.io/v2/email-verifier'


async def check_email(
        email: str,
        user_crud: UserCrud,
        second_check: bool = False,
):
    async with httpx.AsyncClient() as client:
        params = {
            'email': email,
            'api_key': settings.EMAIL_HUNTER_API_KEY,
        }
        response = await client.get(API_ENDPOINT, params=params, timeout=20)
    if response.status_code == status.HTTP_200_OK:
        response_json = response.json()
        email_status = response_json['data'].get('status')
        if email_status == 'valid':
            await user_crud.activate_user(email)
            return
    if not second_check:
        asyncio.create_task(check_email(email, user_crud, second_check=True))
