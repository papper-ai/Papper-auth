import hashlib
import secrets
import typing
from datetime import datetime, timedelta
import jwt
import uuid
from fastapi import Depends, HTTPException, status
from config import settings
from src.repositories import models
from src.repositories.postgres_repository import UserRepository, SecretRepository


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


async def decode_token(token: str):
    user_id = (
        jwt.decode(token, settings.auth_jwt.public_key_path.read_text(), algorithms=settings.auth_jwt.algorithm)).get(
        "user_id")
    return user_id


async def decode_access_token(token: str):
    uuid = (jwt.decode(token, settings.auth_jwt.public_key_path.read_text(),
                       algorithms=settings.auth_jwt.algorithm)).get("uuid")
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
