import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str
    version: str
    app_env: str
    destination_domain: str
    log_level: str
    debug: bool
    host: str
    port: int
    
    model_config = SettingsConfigDict(
        env_file=f".env.{os.getenv('APP_ENV', 'dev')}",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()