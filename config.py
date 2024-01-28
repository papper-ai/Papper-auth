from pydantic_settings import BaseSettings
from pydantic import BaseModel
from pathlib import Path

BASE_DIR = Path(__file__).parent


class AuthJWT(BaseModel):
    private_key_path: Path = BASE_DIR / "auth" / "certs" / "private.pem"
    public_key_path: Path = BASE_DIR / "auth" / "certs" / "public.pem"
    algorithm: str = "RS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_hours: int = 24


class Settings(BaseSettings):
    db_dialect: str
    db_async_driver: str

    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str

    auth_jwt: AuthJWT = AuthJWT()
    mailgun_api_key: str

    @property
    def database_url(self) -> str:
        return f"{self.db_dialect}+{self.db_async_driver}://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
