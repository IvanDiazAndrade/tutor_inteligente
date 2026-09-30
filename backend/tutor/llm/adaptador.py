"""Adaptador LLM: única puerta hacia el proveedor (AD-4; estrategia_llm.md §3-5).

Concentra lo que el resto del sistema no debe saber del LLM:
- plantillas versionadas (RNF-M1) y parámetros por operación;
- política de datos (RNF-S3): las operaciones solo aceptan contenido matemático, así que un
  alias o un identificador no pueden llegar al proveedor ni por descuido;
- resiliencia (RNF-R3): timeout, reintentos con espera, circuit breaker y degradación;
- costo (RNF-C1): registro por llamada, alerta al 80 % y corte al 100 % del tope mensual.

Cuando el LLM no está disponible (sin clave, circuito abierto, tope alcanzado o error), cada
operación devuelve None y el orquestador usa su mensaje local (F6). La práctica nunca se corta.
"""

import logging
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from functools import lru_cache
from typing import Any

from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from tutor.config import Settings, get_settings
from tutor.llm.prompts import RepositorioPrompts
from tutor.llm.proveedores import (
    ErrorPermanente,
    ErrorTransitorio,
    ProveedorLLM,
    ProveedorOpenAI,
    RespuestaLLM,
    Solicitud,
)
from tutor.modelos import LlamadaLLM

log = logging.getLogger("tutor.llm")

ESPERAS_REINTENTO = (0.5, 2.0)  # segundos (estrategia_llm.md §5)

Filtro = Callable[[str], bool]  # True si el texto puede mostrarse al estudiante


# Contextos: lo único que puede viajar al proveedor (estrategia_llm.md §4) ------------------


@dataclass(frozen=True)
class ContextoEjercicio:
    """Contenido matemático del ejercicio. Sin alias, sin ids, sin datos de la cuenta."""

    curso: int
    enunciado: str
    solucion: list[str]
    banda: str  # "Empezando" | "Practicando" | "Dominado": variable pedagógica, no personal
    racha: int = 0


@dataclass(frozen=True)
class ContextoError(ContextoEjercicio):
    respuesta_estudiante: str = ""
    causa: str | None = None  # patrón de error común detectado, si hubo
    pistas_vistas: int = 0
    fallos: int = 0


@dataclass(frozen=True)
class ContextoPista(ContextoEjercicio):
    pista: str = ""  # pista ya verificada del banco
    numero: int = 1
    pistas_anteriores: list[str] = field(default_factory=list)
    simplificar: bool = False  # "No entiendo": misma idea, más simple, sin avanzar pasos


# Salidas estructuradas -------------------------------------------------------------------


class PasosNarrados(BaseModel):
    pasos: list[str]


class VeredictoTriaje(BaseModel):
    veredicto: str = Field(pattern="^(ok|dudoso)$")
    razones: list[str]


class ErrorComunLLM(BaseModel):
    respuesta: str
    causa: str
    retroalimentacion: str


class EjercicioLLM(BaseModel):
    """Esquema de modelo_dominio.md §2 que el LLM debe cumplir al generar (structured output)."""

    enunciado: str
    formato_respuesta: str = Field(pattern="^(numerico|fraccion)$")
    respuesta_final: str
    solucion_referencia: list[str]
    errores_comunes: list[ErrorComunLLM]
    pistas: list[str] = Field(min_length=3, max_length=3)


# Circuit breaker -------------------------------------------------------------------------


class CircuitBreaker:
    """Tras N fallos seguidos se declara degradado por un tiempo; al vencer, reintenta."""

    def __init__(self, fallos_para_corte: int, segundos: int, reloj: Callable[[], float]):
        self.fallos_para_corte = fallos_para_corte
        self.segundos = segundos
        self._reloj = reloj
        self._fallos = 0
        self._abierto_hasta = 0.0

    def permite(self) -> bool:
        return self._reloj() >= self._abierto_hasta

    def exito(self) -> None:
        self._fallos = 0

    def fallo(self) -> None:
        self._fallos += 1
        if self._fallos >= self.fallos_para_corte:
            self._abierto_hasta = self._reloj() + self.segundos
            self._fallos = 0
            log.warning("LLM degradado por %s s tras fallos consecutivos.", self.segundos)


# Adaptador -------------------------------------------------------------------------------


class AdaptadorLLM:
    def __init__(
        self,
        proveedor: ProveedorLLM | None,
        ajustes: Settings | None = None,
        prompts: RepositorioPrompts | None = None,
        reloj: Callable[[], float] = time.monotonic,
        esperar: Callable[[float], None] = time.sleep,
    ):
        self.proveedor = proveedor
        self.ajustes = ajustes or get_settings()
        self.prompts = prompts or RepositorioPrompts(self.ajustes.prompts_dir)
        self.circuito = CircuitBreaker(
            self.ajustes.llm_fallos_para_corte, self.ajustes.llm_segundos_de_corte, reloj
        )
        self._esperar = esperar

    @property
    def habilitado(self) -> bool:
        return self.proveedor is not None

    # Operaciones del tutor (estrategia_llm.md §3) ---------------------------------------
    # `aceptable` es el filtro del orquestador (no revelación, números nuevos): si rechaza el
    # texto, la llamada queda como "filtrado" y la operación devuelve None (mensaje local).

    def retroalimentacion(
        self, bd: Session, ctx: ContextoError, sesion_id=None, aceptable: Filtro | None = None
    ) -> str | None:
        r = self._llamar(
            bd,
            "generarRetroalimentacion",
            "retroalimentacion",
            vars(ctx),
            0.4,
            120,
            None,
            sesion_id,
            validar=_por_texto(aceptable),
        )
        return r.texto.strip() if r else None

    def pista(
        self, bd: Session, ctx: ContextoPista, sesion_id=None, aceptable: Filtro | None = None
    ) -> str | None:
        r = self._llamar(
            bd,
            "generarPista",
            "pista",
            vars(ctx),
            0.4,
            120,
            None,
            sesion_id,
            validar=_por_texto(aceptable),
        )
        return r.texto.strip() if r else None

    def explicacion_guiada(
        self,
        bd: Session,
        ctx: ContextoEjercicio,
        sesion_id=None,
        aceptable: Filtro | None = None,
    ) -> list[str] | None:
        def validar(r: RespuestaLLM) -> bool:
            pasos = r.datos.pasos
            # Si cambia la cantidad de pasos, se usan los originales (misma estructura verificada).
            return len(pasos) == len(ctx.solucion) and (
                aceptable is None or all(aceptable(paso) for paso in pasos)
            )

        r = self._llamar(
            bd,
            "narrarExplicacionGuiada",
            "explicacion-guiada",
            vars(ctx),
            0.3,
            400,
            PasosNarrados,
            sesion_id,
            validar=validar,
        )
        return [paso.strip() for paso in r.datos.pasos] if r else None

    # Operaciones de generación (F5): las usa el pipeline del banco (tarea 60) ----------

    def generar_ejercicio(self, bd: Session, variables: dict[str, Any]) -> EjercicioLLM | None:
        r = self._llamar(
            bd,
            "generarEjercicio",
            "gen-ejercicio",
            variables,
            0.9,
            700,
            EjercicioLLM,
            None,
            sistema="Responde solo con el ejercicio en el formato pedido.",
        )
        return r.datos if r else None

    def triaje(self, bd: Session, curso: int, ejercicio_json: str) -> VeredictoTriaje | None:
        r = self._llamar(
            bd,
            "triajeEjercicio",
            "triaje-ejercicio",
            {"curso": curso, "ejercicioJson": ejercicio_json},
            0.0,
            300,
            VeredictoTriaje,
            None,
            sistema="Eres un revisor. Responde solo con el JSON pedido.",
        )
        return r.datos if r else None

    # Núcleo --------------------------------------------------------------------------

    def gasto_del_mes(self, bd: Session) -> Decimal:
        inicio = datetime.now(UTC).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        total = bd.scalar(
            select(func.coalesce(func.sum(LlamadaLLM.costo_usd), 0)).where(
                LlamadaLLM.creado_en >= inicio
            )
        )
        return Decimal(total)

    def _costo(self, entrada: int, salida: int) -> Decimal:
        a = self.ajustes
        millon = Decimal(1_000_000)
        return (
            a.llm_precio_entrada_usd_mtok * entrada + a.llm_precio_salida_usd_mtok * salida
        ) / millon

    def _llamar(
        self,
        bd: Session,
        operacion: str,
        plantilla: str,
        variables: dict[str, Any],
        temperatura: float,
        max_tokens: int,
        esquema: type[BaseModel] | None,
        sesion_id,
        sistema: str | None = None,
        validar: Callable[[RespuestaLLM], bool] | None = None,
    ) -> RespuestaLLM | None:
        if not self.habilitado:
            return None  # sin clave: modo local, nada que registrar
        a = self.ajustes
        prompt = self.prompts.render(plantilla, **variables)
        registro = dict(
            operacion=operacion,
            modelo=a.llm_modelo,
            version_prompt=prompt.version,
            sesion_id=sesion_id,
        )

        if not self.circuito.permite():
            bd.add(LlamadaLLM(**registro, resultado="degradado"))
            return None
        gasto = self.gasto_del_mes(bd)
        if gasto >= a.llm_tope_usd:
            bd.add(LlamadaLLM(**registro, resultado="tope"))
            log.error("Tope mensual de LLM alcanzado (US$%s): modo local.", gasto)
            return None
        if gasto >= a.llm_tope_usd * a.llm_alerta_fraccion:
            log.warning(
                "Gasto de LLM al %s%% del tope mensual.", round(gasto / a.llm_tope_usd * 100)
            )

        solicitud = Solicitud(
            modelo=a.llm_modelo,
            instrucciones=sistema or self.prompts.render("tutor-sistema").texto,
            entrada=prompt.texto,
            temperatura=temperatura if a.llm_usar_temperatura else None,
            max_tokens=max_tokens,
            timeout=a.llm_timeout_segundos,
            esquema=esquema,
        )
        inicio = time.monotonic()
        resultado, respuesta = "error", None
        for intento in range(a.llm_reintentos + 1):
            try:
                respuesta = self.proveedor.completar(solicitud)
                resultado = "ok"
                break
            except ErrorTransitorio as e:
                resultado = "timeout" if "timeout" in str(e).lower() else "error"
                log.warning("LLM %s falló (intento %s): %s", operacion, intento + 1, e)
                if intento < a.llm_reintentos:
                    self._esperar(ESPERAS_REINTENTO[min(intento, len(ESPERAS_REINTENTO) - 1)])
            except ErrorPermanente as e:
                log.error("LLM %s falló sin reintento: %s", operacion, e)
                resultado = "error"
                break

        latencia = int((time.monotonic() - inicio) * 1000)
        if respuesta is None:
            self.circuito.fallo()
            bd.add(LlamadaLLM(**registro, resultado=resultado, latencia_ms=latencia))
            return None
        self.circuito.exito()  # el proveedor respondió; que el filtro rechace no es una falla
        filtrada = validar is not None and not validar(respuesta)
        bd.add(
            LlamadaLLM(
                **registro,
                resultado="filtrado" if filtrada else "ok",
                latencia_ms=latencia,
                tokens_entrada=respuesta.tokens_entrada,
                tokens_salida=respuesta.tokens_salida,
                costo_usd=self._costo(respuesta.tokens_entrada, respuesta.tokens_salida),
            )
        )
        return None if filtrada else respuesta


def _por_texto(aceptable: "Filtro | None") -> Callable[[RespuestaLLM], bool] | None:
    return None if aceptable is None else (lambda r: bool(r.texto.strip()) and aceptable(r.texto))


@lru_cache
def get_adaptador() -> AdaptadorLLM:
    """Un adaptador por proceso (el circuit breaker vive en memoria). Sin clave, sin proveedor."""
    ajustes = get_settings()
    clave = ajustes.openai_api_key.get_secret_value()
    return AdaptadorLLM(ProveedorOpenAI(clave) if clave else None, ajustes)
