from datetime import datetime, timedelta
from typing import Dict, Union

from jose import jwt

from app.core.config import settings

ALGORITHM = 'HS256'
access_token_jwt_subject = 'access'


def create_access_token(
        data: dict,
        expires_delta: timedelta | None = None
) -> Dict[str, Union[str, datetime]]:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({'exp': expire,
                      'sub': access_token_jwt_subject})
    encoded_jwt = jwt.encode(to_encode,
                             settings.SECRET_KEY,
                             algorithm=ALGORITHM)
    return encoded_jwt
