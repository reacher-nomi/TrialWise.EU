"""App settings, read from environment variables (or a .env file).

Why: the same code runs in Dev, Stage and Live. Only the environment
variables change, never the code ("12-factor app" principle).
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "dev"  # dev | stage | live
    database_url: str = "postgresql+psycopg://app:app@localhost:5432/trialwise"
    ctgov_base_url: str = "https://clinicaltrials.gov/api/v2"


@lru_cache  # read settings once, then reuse
def get_settings() -> Settings:
    return Settings()
