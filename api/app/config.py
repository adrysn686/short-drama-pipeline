"""Centralized environment configuration for the API service."""
from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://factory:factory@localhost:5432/short_drama_pipeline"

    anthropic_api_key: str = ""

    fal_api_key: str = ""

    elevenlabs_api_key: str = ""
    sync_api_key: str = ""

    mubert_api_key: str = ""
    openai_api_key: str = ""

    tiktok_client_key: str = ""
    tiktok_client_secret: str = ""

    meta_app_id: str = ""
    meta_app_secret: str = ""
    meta_long_lived_access_token: str = ""
    ig_business_account_id: str = ""

    youtube_client_id: str = ""
    youtube_client_secret: str = ""
    youtube_refresh_token: str = ""

    storage_backend: str = "local"

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()
