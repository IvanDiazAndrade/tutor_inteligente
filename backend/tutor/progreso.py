"""Reglas del modelo del estudiante que se muestran al usuario (modelo_estudiante.md §5 y §6).

Funciones puras, sin base de datos: banda del índice, estrellas, marca "para repasar" y
unidad sugerida. La app las recibe ya calculadas (el prototipo las replica en
app/src/modelo/progreso.ts solo para funcionar sin servidor).
"""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Literal, Protocol

UMBRAL_BAJO = Decimal("0.4")
UMBRAL_ALTO = Decimal("0.8")
UMBRAL_SUGERENCIA = Decimal("0.6")
DIAS_PARA_REPASAR = 21

Banda = Literal["Empezando", "Practicando", "Dominado"]


class UnidadCatalogo(Protocol):
    id: str
    curso: int
    orden: int


@dataclass(frozen=True)
class EstadoDominio:
    indice: Decimal
    fecha_ultimo_intento: datetime | None


def banda(indice: Decimal) -> Banda:
    if indice < UMBRAL_BAJO:
        return "Empezando"
    if indice < UMBRAL_ALTO:
        return "Practicando"
    return "Dominado"


def estrellas(dominio: EstadoDominio | None) -> int:
    """0 si la unidad no se ha iniciado; luego una estrella por banda (§6)."""
    if dominio is None:
        return 0
    return {"Empezando": 1, "Practicando": 2, "Dominado": 3}[banda(dominio.indice)]


def para_repasar(dominio: EstadoDominio | None, ahora: datetime) -> bool:
    """21 días sin intentos en una unidad con avance real (índice ≥ 0,4), §5."""
    if dominio is None or dominio.fecha_ultimo_intento is None or dominio.indice < UMBRAL_BAJO:
        return False
    return ahora - dominio.fecha_ultimo_intento > timedelta(days=DIAS_PARA_REPASAR)


def unidad_sugerida[U: UnidadCatalogo](
    unidades: Sequence[U], dominios: Mapping[str, EstadoDominio], ahora: datetime, curso: int
) -> U | None:
    """Prioridad de §5: 1) la "para repasar" más antigua; 2) la iniciada con menor índice
    (< 0,6); 3) la siguiente no iniciada según el orden del catálogo de su curso."""
    a_repasar = [u for u in unidades if para_repasar(dominios.get(u.id), ahora)]
    if a_repasar:
        return min(a_repasar, key=lambda u: dominios[u.id].fecha_ultimo_intento)

    debiles = [
        u for u in unidades if u.id in dominios and dominios[u.id].indice < UMBRAL_SUGERENCIA
    ]
    if debiles:
        return min(debiles, key=lambda u: dominios[u.id].indice)

    no_iniciadas = [u for u in unidades if u.curso == curso and u.id not in dominios]
    return min(no_iniciadas, key=lambda u: u.orden, default=None)
