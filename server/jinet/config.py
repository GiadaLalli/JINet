"""Application runtime configuration."""

from pydantic import BaseSettings, PostgresDsn


class Settings(BaseSettings):
    """Application settings."""

    client_id: str
    client_secret: str = "????"

    auth0_domain: str

    database_uri: PostgresDsn = "postgres+asyncpg://postgres:postgres@db/jinet"


settings = Settings()
