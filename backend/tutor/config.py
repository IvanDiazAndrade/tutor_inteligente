"""Configuración leída de variables de entorno o del archivo .env (RNF-M1, RNF-S5)."""

from decimal import Decimal
from functools import lru_cache
from pathlib import Path

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
    # Motor adaptativo (modelo_estudiante.md §1-4). En configuración y no en código: se
    # calibran en TT2 con datos sintéticos (§9).
    motor_alfa: Decimal = Decimal("0.3")
    motor_alfa_sondeo: Decimal = Decimal("0.5")
    motor_intentos_sondeo: int = 3
    motor_umbral_subir: Decimal = Decimal("0.8")
    motor_umbral_bajar: Decimal = Decimal("0.4")
    motor_racha_subir: int = 3
    motor_descuento_pista: Decimal = Decimal("0.15")
    motor_piso_con_pistas: Decimal = Decimal("0.4")
    # Política de intentos (modelo_pedagogico.md §5; RF-P7).
    max_pistas: int = 3
    fallos_para_resolver_juntos: int = 3
    # LLM (estrategia_llm.md). Sin OPENAI_API_KEY el tutor funciona con sus mensajes locales
    # (modo degradado F6), así que la app se puede usar y probar sin clave.
    openai_api_key: SecretStr = SecretStr("")
    # Fijar aquí el snapshot exacto al configurar la cuenta (estrategia_llm.md §2).
    llm_modelo: str = "gpt-5.4-nano"
    llm_timeout_segundos: float = 8.0  # deja margen dentro del ≤ 10 s p90 de RNF-R1
    llm_reintentos: int = 2  # solo ante errores transitorios (timeout, 429, 5xx)
    llm_fallos_para_corte: int = 5  # circuit breaker: fallos seguidos antes de cortar
    llm_segundos_de_corte: int = 60
    # Algunos modelos de razonamiento no aceptan temperatura: en ese caso, False.
    llm_usar_temperatura: bool = True
    # Tope mensual de gasto (stack_tecnologico.md §4): alerta al 80 %, corte al 100 %.
    llm_tope_usd: Decimal = Decimal("5")
    llm_alerta_fraccion: Decimal = Decimal("0.8")
    # Precios de referencia por millón de tokens: verificar en la página oficial de OpenAI.
    llm_precio_entrada_usd_mtok: Decimal = Decimal("0.20")
    llm_precio_salida_usd_mtok: Decimal = Decimal("1.25")
    # Carpeta de las plantillas de prompts (RNF-M1: editables sin recompilar).
    prompts_dir: str = str(Path(__file__).resolve().parents[2] / "prompts")


@lru_cache
def get_settings() -> Settings:
    return Settings()
