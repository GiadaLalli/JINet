"""Application runtime configuration."""

import secrets

from pydantic import PostgresDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    client_id: str = ""
    client_secret: str = "????"
    secret_key: str = secrets.token_urlsafe(32)

    auth0_domain: str = ""

    database_uri: PostgresDsn


settings = Settings()
