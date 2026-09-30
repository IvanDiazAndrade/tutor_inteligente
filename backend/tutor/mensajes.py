"""Mensajes locales del tutor, sin LLM (modelo_pedagogico.md §3 y §7).

El refuerzo de una respuesta correcta siempre es local (la ruta correcta no llama al LLM).
La retroalimentación de error y la re-explicación usan aquí su versión de respaldo, la misma
que se usa cuando el LLM no está disponible (F6); el LLM se conecta en las tareas 55 y 59.
Todo texto dirigido al estudiante pasa por `sin_revelar` antes de salir (§6).
"""

import random
from typing import Any

from tutor.dominio.plantillas import menciona

REFUERZOS = [
    "¡Muy bien! Lo lograste.",
    "¡Excelente! Vas muy bien.",
    "¡Eso es! Sigue así.",
    "¡Genial! Lo resolviste tú.",
    "¡Muy bien pensado!",
    "¡Correcto! Buen trabajo.",
]


def refuerzo(racha: int, subio_de_nivel: bool, azar: random.Random | None = None) -> str:
    """Refuerzo positivo con variante de logro (§3): el caso más frecuente, sin costo de API."""
    if subio_de_nivel:
        return "¡Subiste de nivel! Ahora vienen ejercicios un poco más desafiantes."
    if racha >= 3:
        return f"¡{racha} seguidas! {(azar or random).choice(REFUERZOS)}"
    return (azar or random).choice(REFUERZOS)


def forma_canonica(respuesta_final: str) -> str:
    """Cuando la respuesta es correcta pero escrita de otra forma (6/8 por 3/4). Se agrega
    después de corregir: ahí ya no revela nada."""
    return f"También puedes escribirla como {respuesta_final}."


def error_local(error_comun: dict[str, Any] | None, solucion: list[str], respuesta: str) -> str:
    """Retroalimentación de error sin LLM (§7): la del patrón detectado si lo hubo; si no,
    el primer paso de la solución de referencia."""
    if error_comun:
        return sin_revelar(f"Todavía no es. {error_comun['retroalimentacion']}", respuesta)
    return sin_revelar(f"Todavía no es. Revisa este paso: {solucion[0]}", respuesta)


def reexplicacion_local(pistas: list[str], respuesta: str) -> str:
    """Respuesta a "No entiendo" sin LLM: vuelve a la estrategia (pista 1), sin revelar más."""
    return sin_revelar(f"Vamos más despacio. {pistas[0]}", respuesta)


RESPALDO = "Revisa tu procedimiento paso a paso. ¡Tú puedes!"


def sin_revelar(texto: str, respuesta: str) -> str:
    """Filtro de no revelación (§6, capa determinista): si el texto nombra la respuesta final,
    se reemplaza por un mensaje seguro. La versión completa (equivalentes y palabras) llega
    con el orquestador y el LLM (tareas 59 y 66)."""
    return RESPALDO if menciona(texto, respuesta) else texto
