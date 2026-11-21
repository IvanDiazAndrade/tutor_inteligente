"""Piezas comunes del generador paramétrico (AD-9; modelo_dominio.md §4).

Cada plantilla sortea sus parámetros dentro del rango del OA y construye el ejercicio completo
con el esquema de §2: enunciado, respuesta final, solución paso a paso, errores comunes (como
fórmulas de los parámetros), tres pistas y representación pictórica opcional. El resultado es
correcto por construcción: la respuesta sale de los parámetros, nunca al revés. Los niveles
cambian los parámetros, no la plantilla.
"""

import random
import re
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Any, Protocol

from tutor.dominio.corrector import fraccion, numero


@dataclass(frozen=True)
class EjercicioGenerado:
    unidad_id: str
    plantilla_id: str
    nivel: int
    enunciado: str
    formato_respuesta: str
    respuesta_final: str
    solucion_referencia: list[str]
    errores_comunes: list[dict[str, str]]
    pistas: list[str]
    regla_validacion: dict[str, Any] = field(default_factory=lambda: {"aceptaEquivalentes": True})
    representacion: dict[str, Any] | None = None


class Plantilla(Protocol):
    id: str
    unidad_id: str
    version: int

    def instanciar(self, nivel: int, azar: random.Random) -> EjercicioGenerado: ...


def valor(texto: str) -> Fraction:
    """Valor exacto de una respuesta escrita como fracción, número mixto, entero o decimal."""
    return fraccion(texto) if "/" in texto else numero(texto)


def _errores(respuesta: str, candidatos: list[tuple[str, str, str]]) -> list[dict[str, str]]:
    """Descarta errores que valen lo mismo que la respuesta o que otro error (p. ej. 2/4 y 1/2):
    un patrón ambiguo no sirve para diagnosticar la causa."""
    vistos = {valor(respuesta)}
    errores = []
    for respuesta_error, causa, retro in candidatos:
        if valor(respuesta_error) not in vistos:
            vistos.add(valor(respuesta_error))
            errores.append(
                {"respuesta": respuesta_error, "causa": causa, "retroalimentacion": retro}
            )
    return errores


def menciona(texto: str, respuesta: str) -> bool:
    """¿El texto contiene la respuesta como número o fracción suelto (no dentro de otro)?"""
    return re.search(rf"(?<![\d/]){re.escape(respuesta)}(?![\d/])", texto) is not None


def _sin_revelar(pista: str, respuesta: str, alternativa: str) -> str:
    """Si por casualidad la pista nombra la respuesta (p. ej. 99 : 9 -> "divide 11 : 9"),
    se usa una versión sin números. El filtro del tutor lo revisa de nuevo al servirla."""
    formas = {respuesta, miles(int(respuesta))} if respuesta.isdigit() else {respuesta}
    return alternativa if any(menciona(pista, forma) for forma in formas) else pista


def miles(n: int) -> str:
    """Entero con punto de miles, como se escribe en Chile (1.800, 12.500). El corrector acepta
    la respuesta con o sin el punto (modelo_dominio.md §3.1)."""
    return f"{n:,}".replace(",", ".")


PALABRAS_DECIMALES = {1: "un decimal", 2: "dos decimales", 3: "tres decimales"}
PALABRAS_LUGARES = {1: "un lugar", 2: "dos lugares", 3: "tres lugares"}


def decimales(v: Fraction) -> int:
    """Cantidad de decimales de un número decimal exacto (2,35 -> 2; 7 -> 0)."""
    k = 0
    while (v * 10**k).denominator != 1:
        k += 1
        if k > 6:
            raise ValueError(f"{v} no es un decimal finito")
    return k


def fijo(v: Fraction, k: int) -> str:
    """Decimal con coma y exactamente k decimales (3,50), como se escribe al alinear comas."""
    escalado = v * 10**k
    if escalado.denominator != 1:
        raise ValueError(f"{v} tiene más de {k} decimales")
    n = abs(int(escalado))
    signo = "-" if v < 0 else ""
    if k == 0:
        return f"{signo}{n}"
    return f"{signo}{n // 10**k},{n % 10**k:0{k}d}"


def decimal_cl(v: Fraction) -> str:
    """Decimal con coma y sin ceros sobrantes, como se escribe en Chile (9,4; 0,125; 7)."""
    return fijo(v, decimales(v))
