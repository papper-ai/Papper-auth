from datetime import timedelta

import uuid
from fastapi import Depends, HTTPException, status, APIRouter, Cookie, Response, Body
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from auth import schemas as auth_models
from auth import utils
from auth.dependencies import authentication_with_token, add_secret_depends
from auth.utils import get_access_and_refresh_tokens
from config import settings
from repositories import models as repo_models
from repositories.postgres_repository import UserRepository, SecretRepository

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
    user = await utils.authenticate_user(
        login_credentials.login, login_credentials.password, user_repository
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return await get_access_and_refresh_tokens(user)


@auth_router.post(
    "/refresh",
    response_model=auth_models.Tokens,
    status_code=status.HTTP_200_OK,
    description="Refresh access-token and refresh-token key pair. Use when a user "
    "authentication error occurs to get a new key pair",
)
async def refresh_token_regenerate(refresh_token: str = Body(..., embed=True),
                                    user_repository: UserRepository = Depends(UserRepository)):
    decoded_token = await utils.decode_token(refresh_token)
    user_id = decoded_token.user_id
    user = await user_repository.get(user_id)

    return await get_access_and_refresh_tokens(user)


@auth_router.post("/user", description="Get user by access-token (used for debugging)")
async def get_user(
    user_id: str = Depends(authentication_with_token),
    user_repository: UserRepository = Depends(UserRepository),
):
    user = await user_repository.get(user_id)
    return user.__dict__


@auth_router.get("/user/{uuid}/token", description="Get access-token by user UUID",
                 response_model=auth_models.Tokens)
async def get_token_by_uuid(uuid: uuid.UUID, user_repository: UserRepository = Depends(UserRepository)):
    user = await user_repository.get(uuid)
    return await get_access_and_refresh_tokens(user)


@auth_router.post("/user/update", description="Update User")
async def update_user(
    user_id: uuid.UUID = Body(..., embed=True),
    has_face_id: bool = Body(..., embed=True),
    user_repository: UserRepository = Depends(UserRepository),
):
    user = await user_repository.get(user_id)
    user.is_active = has_face_id
    await user_repository.merge(user)


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