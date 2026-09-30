"""Configuración leída de variables de entorno o del archivo .env (RNF-M1, RNF-S5)."""

from decimal import Decimal
from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql+psycopg://tutor:tutor@127.0.0.1:5432/tutor"
    # En Render se define JWT_SECRET con un valor aleatorio largo; este es solo para desarrollo.
    jwt_secret: SecretStr = SecretStr("solo-para-desarrollo-no-usar-en-produccion-0123456789")
    # Vigencia de los tokens (RNF-S1: sesiones con expiración).
    jwt_minutos_apoderado: int = 24 * 60
    jwt_minutos_estudiante: int = 8 * 60
    # PIN del estudiante: bloqueo temporal tras varios fallos (diagramas_secuencia.md §2).
    pin_max_fallos: int = 5
    pin_minutos_bloqueo: int = 5
    openai_api_key: SecretStr = SecretStr("")
    llm_modelo: str = "gpt-5.4-nano"
    llm_tope_usd: Decimal = Decimal("5")


@lru_cache
def get_settings() -> Settings:
    return Settings()
