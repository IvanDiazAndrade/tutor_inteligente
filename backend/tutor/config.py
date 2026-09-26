"""Configuración leída de variables de entorno o del archivo .env (RNF-M1, RNF-S5)."""

from decimal import Decimal
from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql+psycopg://tutor:tutor@localhost:5432/tutor"
    jwt_secret: SecretStr = SecretStr("solo-para-desarrollo")
    openai_api_key: SecretStr = SecretStr("")
    llm_modelo: str = "gpt-5.4-nano"
    llm_tope_usd: Decimal = Decimal("5")


@lru_cache
def get_settings() -> Settings:
    return Settings()
