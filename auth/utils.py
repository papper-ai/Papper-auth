import hashlib
import random
import secrets
from datetime import datetime, timedelta
import jwt
from fastapi import Depends, HTTPException, status

from config import settings
from repositories import models
from repositories.postgres_repository import UserRepository


async def authenticate_user(email: str, password: str, user_repository: UserRepository) -> models.User or bool:
    user = await user_repository.get(email)
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
    uuid = (
        jwt.decode(token, settings.auth_jwt.public_key_path.read_text(), algorithms=settings.auth_jwt.algorithm)).get(
        "uuid")
    return uuid


async def decode_access_token(token: str):
    uuid = (jwt.decode(token, settings.auth_jwt.public_key_path.read_text(),
                       algorithms=settings.auth_jwt.algorithm)).get("uuid")
    return uuid


def generate_password():
    # 5 digits password
    password = str(secrets.randbelow(100000)).zfill(5)

    # hash password
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    return password, hashed_password
