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
