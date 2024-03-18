import uuid

from pydantic import BaseModel, Field


class RegistrationRequest(BaseModel):
    secret: uuid.UUID
    name: str
    surname: str
    login: str
    password: str


class Secret(BaseModel):
    secret: uuid.UUID
    created_by: str


class Tokens(BaseModel):
    access_token: str
    refresh_token: str


class LoginCredentials(BaseModel):
    login: str
    password: str
