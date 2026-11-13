from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: SecretStr

    jwt_secret_key: SecretStr
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 14

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
