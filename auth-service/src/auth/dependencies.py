import jwt.exceptions
from fastapi import Cookie, HTTPException, status

from src.auth import utils


async def authentication_with_token(access_token: str = Cookie(alias="access-token")):
    try:
        return await utils.decode_access_token(access_token)

    except jwt.exceptions.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.exceptions.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
