"""Motor adaptativo: modelo del estudiante (modelo_estudiante.md §1-4; AD-5).

Funciones puras sobre el estado de DominioOA. El índice de dominio por OA es un promedio
móvil exponencial: un solo número, sin datos de entrenamiento y explicable en una frase
("sube cuando responde bien, baja cuando se equivoca; lo último pesa más").
"""

from dataclasses import dataclass, replace
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal
from typing import Literal

from tutor.config import Settings, get_settings

TRES_DECIMALES = Decimal("0.001")  # dominio_oa.indice es numeric(4,3)


@dataclass(frozen=True)
class EstadoMotor:
    indice: Decimal
    nivel: int
    racha: int
    intentos: int
    fecha_ultimo_intento: datetime | None = None


ESTADO_INICIAL = EstadoMotor(indice=Decimal("0.5"), nivel=2, racha=0, intentos=0)  # §4

CambioNivel = Literal["sube", "baja"] | None


def ponderar(es_correcta: bool, pistas: int, ajustes: Settings | None = None) -> Decimal:
    """Resultado ponderado de un intento (§1): 0 si es incorrecta; si es correcta, 1 menos
    0,15 por pista usada, con piso 0,4 (resolver con ayuda sigue siendo evidencia parcial)."""
    a = ajustes or get_settings()
    if not es_correcta:
        return Decimal(0)
    return max(a.motor_piso_con_pistas, 1 - a.motor_descuento_pista * pistas)


def registrar_intento(
    estado: EstadoMotor,
    es_correcta: bool,
    pistas: int,
    ahora: datetime,
    ajustes: Settings | None = None,
) -> tuple[EstadoMotor, CambioNivel]:
    """Actualiza el índice, la racha y el nivel tras un intento corregido (pseudocódigo §3)."""
    a = ajustes or get_settings()
    r = ponderar(es_correcta, pistas, a)
    intentos = estado.intentos + 1
    # Sondeo en frío (§4): los primeros intentos de la unidad pesan más para ubicar rápido.
    alfa = a.motor_alfa_sondeo if intentos <= a.motor_intentos_sondeo else a.motor_alfa
    indice = (estado.indice + alfa * (r - estado.indice)).quantize(TRES_DECIMALES, ROUND_HALF_UP)
    racha = estado.racha + 1 if es_correcta else 0

    nivel, cambio = estado.nivel, None
    if indice >= a.motor_umbral_subir and racha >= a.motor_racha_subir and nivel < 3:
        nivel, cambio = nivel + 1, "sube"
    elif indice < a.motor_umbral_bajar and nivel > 1:
        # Sin condición de racha: ante evidencia de frustración se actúa rápido (§3).
        nivel, cambio = nivel - 1, "baja"
    if cambio:
        racha = 0  # la racha se reinicia con cada cambio de nivel

    nuevo = replace(
        estado,
        indice=indice,
        nivel=nivel,
        racha=racha,
        intentos=intentos,
        fecha_ultimo_intento=ahora,
    )
    return nuevo, cambio
