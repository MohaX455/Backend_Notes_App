from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal

class Settings(BaseSettings):
    DB_HOST: str = ""
    DB_PORT: int = 3306
    DB_USER: str = ""
    DB_PASSWORD: str = ""
    DB_NAME: str = ""

    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_COOKIE_NAME: str = "refresh_token"
    REFRESH_COOKIE_MAX_AGE_SECONDS: int = 60 * 60 * 24 * 7
    COOKIE_SECURE: bool = False
    COOKIE_SAMESITE: Literal["lax", "strict", "none"] = "lax"

    model_config = SettingsConfigDict(
        env_file='.env',
        extra="ignore"
    )

settings = Settings()