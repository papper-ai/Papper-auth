from pydantic import BaseModel


class RegistrationRequest(BaseModel):
    secret: str
    name: str
    surname: str
    login: str
    password: str
