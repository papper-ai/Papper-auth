import hashlib
import typing
from datetime import datetime, timedelta

import jwt
import uuid
from fastapi import HTTPException, status

from auth.schemas import Tokens
from config import settings
from repositories import models
from repositories.postgres_repository import UserRepository, SecretRepository
from pydantic import UUID4

ACCESS_TOKEN_EXPIRE_MINUTES = settings.auth_jwt.access_token_expire_minutes
REFRESH_TOKEN_EXPIRE_HOURS = settings.auth_jwt.refresh_token_expire_hours

DecodedToken = typing.NamedTuple("decoded_token", [("user_id", str), ("login", str)])


async def authenticate_user(login: str, password: str,
                            user_repository: UserRepository) -> typing.Union[models.User, bool]:
    user = await user_repository.get_user_by_login(login)
    if not hashlib.sha256(password.encode()).hexdigest() == user.password:
        return False
    return user


async def create_token(data: dict, expires_delta: timedelta = None):
    if expires_delta:
        data.update({"exp": datetime.utcnow() + expires_delta})
    encoded_jwt = jwt.encode(data, settings.auth_jwt.private_key_path.read_text(),
                             algorithm=settings.auth_jwt.algorithm)
    return encoded_jwt


async def get_access_and_refresh_tokens(user: models.User) -> Tokens:
    access_token = await create_token(
        data={"user_id": user.user_id, "login": user.login, "has_face_id": user.has_face_id},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    refresh_token = await create_token(
        data={"user_id": user.user_id, "has_face_id": user.has_face_id},
        expires_delta=timedelta(hours=REFRESH_TOKEN_EXPIRE_HOURS),
    )

    return Tokens(access_token=access_token, refresh_token=refresh_token)


async def decode_token(token: str) -> DecodedToken:
    user_id = (
        jwt.decode(token, settings.auth_jwt.public_key_path.read_text(), algorithms=settings.auth_jwt.algorithm)).get(
        "user_id")
    login = (
        jwt.decode(token, settings.auth_jwt.public_key_path.read_text(), algorithms=settings.auth_jwt.algorithm)).get(
        "login"
    )
    return DecodedToken(user_id=user_id, login=login)


async def decode_access_token(token: str):
    uuid = (jwt.decode(token, settings.auth_jwt.public_key_path.read_text(),
                       algorithms=settings.auth_jwt.algorithm))["user_id"]
    return uuid


def hash_password(password: str):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    return hashed_password


async def check_secret(secret: uuid.UUID, secret_repository: SecretRepository):
    secret_entity = await secret_repository.get(secret)
    if not secret_entity:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid secret",
            headers={"WWW-Authenticate": "Bearer"},
        )
    else:
        return secret_entity
