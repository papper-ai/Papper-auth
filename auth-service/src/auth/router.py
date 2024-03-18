from datetime import timedelta

import uuid
from fastapi import Depends, HTTPException, status, APIRouter, Cookie, Response, Body
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from auth import schemas as auth_models
from auth import utils
from auth.dependencies import authentication_with_token, add_secret_depends
from config import settings
from repositories import models as repo_models
from repositories.postgres_repository import UserRepository, SecretRepository

ACCESS_TOKEN_EXPIRE_MINUTES = settings.auth_jwt.access_token_expire_minutes
REFRESH_TOKEN_EXPIRE_HOURS = settings.auth_jwt.refresh_token_expire_hours
DOMAIN = settings.domain

auth_router = APIRouter(prefix="/personal")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="personal/token")


@auth_router.post("/registration")
async def registration(
    registration_request: auth_models.RegistrationRequest,
    user_repository: UserRepository = Depends(UserRepository),
    secret_repository: SecretRepository = Depends(SecretRepository),
):
    user = await user_repository.get_user_by_login(registration_request.login)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists",
        )
    else:
        secret_entity = await utils.check_secret(
            registration_request.secret, secret_repository
        )

        secret_entity.used_by = user_id = uuid.uuid4()  # creating user_id
        secret_entity.is_used = True
        await secret_repository.add(secret_entity)

        registration_request.password = utils.hash_password(
            registration_request.password
        )
        await user_repository.add(
            repo_models.User(
                **registration_request.model_dump(exclude={"secret"}),
                user_id=user_id,
                used_secret=secret_entity.secret
            )
        )


@auth_router.post(
    "/token",
    description="Get access-token while user logs in",
    response_model=auth_models.Tokens,
    status_code=status.HTTP_200_OK,
)
async def login_for_access_token(
    login_credentials: auth_models.LoginCredentials,
    user_repository: UserRepository = Depends(UserRepository),
):
    logging_data = auth_models.LoggingData(username=login_credentials.login, password=login_credentials.password)
    user = await utils.authenticate_user(
        logging_data.username, logging_data.password, user_repository
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = await utils.create_token(
        data={"user_id": user.user_id},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    refresh_token = await utils.create_token(
        data={"user_id": user.user_id},
        expires_delta=timedelta(hours=REFRESH_TOKEN_EXPIRE_HOURS),
    )

    return auth_models.Tokens(access_token=access_token, refresh_token=refresh_token)


@auth_router.post(
    "/refresh",
    response_model=auth_models.Tokens,
    status_code=status.HTTP_200_OK,
    description="Refresh access-token and refresh-token key pair. Use when a user "
    "authentication error occurs to get a new key pair",
)
async def refresh_token_regenerate(refresh_token: str = Body(..., embed=True)):
    user_id = await utils.decode_token(refresh_token)

    access_token = await utils.create_token(
        data={"user_id": user_id},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    refresh_token = await utils.create_token(
        data={"user_id": user_id},
        expires_delta=timedelta(hours=REFRESH_TOKEN_EXPIRE_HOURS),
    )

    return auth_models.Tokens(access_token=access_token, refresh_token=refresh_token)


@auth_router.post("/user", description="Get user by access-token (used for debugging)")
async def get_user(
    user_id: str = Depends(authentication_with_token),
    user_repository: UserRepository = Depends(UserRepository),
):
    user = await user_repository.get(user_id)
    return user.__dict__


@auth_router.post("/secrets", description="Get all secrets")
async def get_secrets(
    user_id: str = Depends(authentication_with_token),
    secret_repository: SecretRepository = Depends(SecretRepository),
):
    secrets = await secret_repository.get_secrets()
    return secrets


@auth_router.post("/add_secret", description="Add new secret")
async def add_secret(
    secret: auth_models.Secret = Depends(add_secret_depends),
    secret_repository: SecretRepository = Depends(SecretRepository),
):
    await secret_repository.add(repo_models.Secret(**secret.model_dump()))
