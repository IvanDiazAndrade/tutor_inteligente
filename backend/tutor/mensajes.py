"""Mensajes locales del tutor, sin LLM (modelo_pedagogico.md §3 y §7).

El refuerzo de una respuesta correcta siempre es local (la ruta correcta no llama al LLM).
La retroalimentación de error, las pistas y la re-explicación tienen aquí su versión local,
la que se usa cuando el LLM no está disponible o su texto no pasa los filtros (F6).
Todo texto dirigido al estudiante pasa por el filtro de no revelación antes de salir (§6).
"""

import random
import re
from typing import Any

from tutor.dominio.corrector import FormatoInvalido, fraccion, numero
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

# Números, fracciones y números mixtos que aparecen en un texto ("1 1/2", "6/8", "0,75", "12.500").
_CANTIDADES = re.compile(r"\d+\s+\d+\s*/\s*\d+|\d+\s*/\s*\d+|\d+(?:[.,]\d+)*")


def revela(texto: str, respuesta: str) -> bool:
    """¿El texto contiene la respuesta final, literal o en una forma equivalente aceptada?

    Si la respuesta es una fracción se comparan las fracciones y los decimales del texto (6/8 y
    0,75 revelan 3/4), pero no los enteros sueltos, que suelen ser operandos ("Suma 1 + 3").
    Si es un número, cualquier número de igual valor.
    Las respuestas en palabras ("tres cuartos") se agregan con el filtro completo (tarea 66).
    """
    if menciona(texto, respuesta):
        return True
    es_fraccion = "/" in respuesta
    try:
        esperado = fraccion(respuesta) if es_fraccion else numero(respuesta)
    except FormatoInvalido:
        return False
    for cantidad in _CANTIDADES.findall(texto):
        if es_fraccion and re.fullmatch(r"\d+", cantidad):
            continue  # en respuestas fraccionarias, un entero suelto suele ser un operando
        try:
            valor = fraccion(cantidad) if "/" in cantidad else numero(cantidad, respuesta)
        except FormatoInvalido:
            continue
        if valor == esperado:
            return True
    return False


def _valores(texto: str) -> set:
    valores = set()
    for cantidad in _CANTIDADES.findall(texto):
        try:
            valores.add(fraccion(cantidad) if "/" in cantidad else numero(cantidad))
        except FormatoInvalido:
            continue
    return valores


def numeros_nuevos(texto: str, permitido: str) -> bool:
    """¿El texto trae números que no están en `permitido`? Una pista reformulada o una
    narración que inventa números puede adelantar pasos o cambiar la solución verificada."""
    return not _valores(texto) <= _valores(permitido)


def sin_revelar(texto: str, respuesta: str) -> str:
    """Filtro de no revelación (§6, capa determinista): si el texto revela la respuesta final,
    se reemplaza por un mensaje seguro."""
    return RESPALDO if revela(texto, respuesta) else texto


def personalizar(texto: str, alias: str) -> str:
    """El LLM escribe {nombre}; el alias se inserta aquí, en el servidor y después del filtro,
    así nunca viaja al proveedor (estrategia_llm.md §4)."""
    return texto.replace("{nombre}", alias)
