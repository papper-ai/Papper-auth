from typing import NoReturn

import jwt.exceptions
import uuid
from fastapi import Cookie, HTTPException, status, Form
from pydantic import UUID4
from auth import utils
from auth.schemas import RegistrationRequest, Secret


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


def registration_depends(secret: uuid.UUID = Form(...), name: str = Form(...), surname: str = Form(...), login: str = Form(...),
                         password: str = Form(...)):
    return RegistrationRequest(secret=secret, name=name, surname=surname, login=login, password=password)


def add_secret_depends(secret: uuid.UUID = Form(..., description='17374954-9f59-4bdd-873f-9d30b95549bf'),
                       created_by: str = Form(..., description='vasya')):
    return Secret(secret=secret, created_by=created_by)
