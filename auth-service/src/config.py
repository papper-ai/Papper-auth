from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import BaseSettings

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

    db_container_port: int

    auth_jwt: AuthJWT = AuthJWT()

    domain: str
    host_port: str

    is_testing: bool

    @property
    def database_url(self) -> str:
        if self.is_testing:
            return f"{self.db_dialect}+{self.db_async_driver}://{self.db_user}:{self.db_password}@localhost:{self.db_container_port}/{self.db_name}"
        else:
            return f"{self.db_dialect}+{self.db_async_driver}://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    class Config:
        extra = "ignore"
        if Path(r"C:\Users\desktop\PycharmProjects\Papper\.env").exists():
            env_file = r"C:\Users\desktop\PycharmProjects\Papper\.env"


settings = Settings()
