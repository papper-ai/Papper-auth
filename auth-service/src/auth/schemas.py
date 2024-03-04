import uuid

from pydantic import BaseModel


class RegistrationRequest(BaseModel):
    secret: uuid.UUID
    name: str
    surname: str
    login: str
    password: str
