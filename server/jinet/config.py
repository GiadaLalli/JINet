"""Application runtime configuration."""

from pydantic import PostgresDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    client_id: str = ""
    client_secret: str = "????"

    auth0_domain: str = ""

    database_uri: PostgresDsn


settings = Settings()
