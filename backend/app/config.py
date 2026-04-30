from functools import lru_cache

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_prefix="SIMUBOSS_",
        extra="ignore",
    )

    app_name: str = "simuBoss Backend"
    app_env: str = "development"
    frontend_origin: str = "http://127.0.0.1:5173"

    admin_username: str = "admin"
    admin_password: str = "123456"
    session_ttl_hours: int = 24 * 7

    deepseek_api_key: str = Field(
        default="",
        validation_alias=AliasChoices("SIMUBOSS_DEEPSEEK_API_KEY", "VITE_DEEPSEEK_API_KEY"),
    )
    deepseek_model: str = Field(
        default="deepseek-chat",
        validation_alias=AliasChoices("SIMUBOSS_DEEPSEEK_MODEL", "VITE_DEEPSEEK_MODEL"),
    )
    deepseek_base_url: str = Field(
        default="https://api.deepseek.com",
        validation_alias=AliasChoices("SIMUBOSS_DEEPSEEK_BASE_URL", "VITE_DEEPSEEK_BASE_URL"),
    )
    database_url: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
