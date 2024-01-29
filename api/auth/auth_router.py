from fastapi import Depends, HTTPException, status, APIRouter, Cookie, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta

from pydantic import EmailStr

from auth.dependencies import authentication_with_token
from config import settings
from repositories import models
from repositories.postgres_repository import UserRepository
from auth import utils, email_sender

ACCESS_TOKEN_EXPIRE_MINUTES = settings.auth_jwt.access_token_expire_minutes
REFRESH_TOKEN_EXPIRE_HOURS = settings.auth_jwt.refresh_token_expire_hours
DOMAIN = settings.domain
auth_router = APIRouter(prefix="/personal")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="personal/token")


@auth_router.post("/registration")
async def registration(email: EmailStr, user_repository: UserRepository = Depends(UserRepository)):
    user = await user_repository.get(email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists",
        )
    else:
        password, hashed_password = utils.generate_password()
        await email_sender.send_email(password, email)
        await user_repository.add(models.User(email=email, password=hashed_password))


@auth_router.post("/token",
                  description="Get access-token while user logs in")
async def login_for_access_token(response: Response,
                                 form_data: OAuth2PasswordRequestForm = Depends(),
                                 user_repository: UserRepository = Depends(UserRepository)):
    user = await utils.authenticate_user(form_data.username, form_data.password, user_repository)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = await utils.create_token(
        data={"uuid": user.uuid}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh_token = await utils.create_token(
        data={"uuid": user.uuid}, expires_delta=timedelta(hours=REFRESH_TOKEN_EXPIRE_HOURS)
    )

    response.status_code = 200
    response.init_headers(headers={'Authorization': 'bearer' + access_token})
    response.set_cookie(key="access-token", value=access_token,
                        expires=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES).total_seconds(), 
                        domain=DOMAIN, samesite="lax", httponly=True)
    response.set_cookie(key="refresh-token", value=refresh_token,
                        expires=timedelta(hours=REFRESH_TOKEN_EXPIRE_HOURS).total_seconds(), 
                        domain=DOMAIN, samesite="lax", httponly=True)
    return response


@auth_router.post("/refresh", description="Refresh access-token and refresh-token key pair. Use when a user "
                                                   "authentication error occurs to get a new key pair")
async def refresh_token_regenerate(response: Response,
                                   refresh_token: str = Cookie(alias="refresh-token")):
    uuid = await utils.decode_token(refresh_token)
    access_token = await utils.create_token(
        data={"uuid": uuid}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh_token = await utils.create_token(
        data={"uuid": uuid}, expires_delta=timedelta(hours=REFRESH_TOKEN_EXPIRE_HOURS)
    )
    response.status_code = 200
    response.init_headers(headers={'Authorization': 'bearer' + access_token})

    response.set_cookie(key="access-token", 
                        value=access_token,
                        expires=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES).total_seconds(),
                        domain=DOMAIN, samesite="lax", httponly=True)
    response.set_cookie(key="refresh-token", value=refresh_token,
                        expires=timedelta(hours=REFRESH_TOKEN_EXPIRE_HOURS).total_seconds(), 
                        domain=DOMAIN, samesite="lax", httponly=True)
    return response


@auth_router.get("/user")
async def get_user(uuid: str = Depends(authentication_with_token), user_repository: UserRepository = Depends(UserRepository)):
    user = await user_repository.get_user_by_uuid(uuid)
    return {"user_email": user.email}