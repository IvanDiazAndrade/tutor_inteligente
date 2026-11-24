"""Mensajes locales del tutor, sin LLM (modelo_pedagogico.md §3 y §7).

El refuerzo de una respuesta correcta siempre es local (la ruta correcta no llama al LLM).
La retroalimentación de error, las pistas y la re-explicación tienen aquí su versión local,
la que se usa cuando el LLM no está disponible o su texto no pasa los filtros (F6).
Todo texto dirigido al estudiante pasa por el filtro de no revelación antes de salir (§6).
"""

import random
import re
from typing import Any

from tutor.dominio import palabras
from tutor.dominio.columnas import con_bloque, separar_bloque
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


def error_local(
    error_comun: dict[str, Any] | None, solucion: list[str], respuesta: str, enunciado: str = ""
) -> str:
    """Retroalimentación de error sin LLM (§7): la del patrón detectado si lo hubo; si no,
    el primer paso de la solución de referencia."""
    if error_comun:
        texto = f"Todavía no es. {error_comun['retroalimentacion']}"
    else:
        texto = f"Todavía no es. Revisa este paso: {solucion[0]}"
    return sin_revelar(texto, respuesta, enunciado)


def reexplicacion_local(pistas: list[str], respuesta: str, enunciado: str = "") -> str:
    """Respuesta a "No entiendo" sin LLM: vuelve a la estrategia (pista 1), sin revelar más."""
    return sin_revelar(f"Vamos más despacio. {pistas[0]}", respuesta, enunciado)


RESPALDO = "Revisa tu procedimiento paso a paso. ¡Tú puedes!"

# Números, fracciones y números mixtos que aparecen en un texto ("1 1/2", "6/8", "0,75", "12.500").
_CANTIDADES = re.compile(r"\d+\s+\d+\s*/\s*\d+|\d+\s*/\s*\d+|\d+(?:[.,]\d+)*")
# "2,5 es mayor que 2,2" ("1/3 < 5/9" ya lo atrapa menciona).
_COMPARACION = re.compile(
    r"\d[\d.,/ ]*\s*(?:es|son|va|queda)?\s*"
    r"(?:menor|mayor|mas grande|mas chic[oa]|igual)\s+(?:que|a)\s*\d"
)


def revela(texto: str, respuesta: str, enunciado: str = "") -> bool:
    """¿El texto contiene la respuesta final, literal o en una forma equivalente aceptada?
    Filtro completo de no revelación (modelo_pedagogico.md §6; tarea 66).

    - Número: cualquier número de igual valor, en cifras ("1.200", "2,50") o en palabras
      ("mil doscientos", "dos coma cinco", "dos enteros y cinco décimas").
    - Fracción: las fracciones, decimales y mixtos de igual valor (6/8, 0,75, "tres cuartos",
      "75 centésimos" revelan 3/4), pero no los enteros sueltos, que suelen ser operandos.
    - Comparar (<, =, >): el símbolo o la comparación dicha entre dos números ("2,5 es mayor
      que 2,2"), en cualquiera de los dos sentidos.
    - Ordenar: la secuencia completa en el orden pedido, aunque la separen comas o signos.

    Excepción: si el enunciado ya da el valor de la respuesta en otra forma ("Escribe 59/100
    como decimal", "Escribe con cifras: tres mil"), el ejercicio es de escritura y solo revela
    la forma pedida; nombrar el dato del enunciado ("son 59 centésimos") no adelanta nada.
    """
    if menciona(texto, respuesta):
        return True
    if respuesta in ("<", "=", ">"):
        return _COMPARACION.search(palabras.sin_tildes(texto)) is not None
    if ";" in respuesta:
        return _ordena(texto, respuesta)
    es_fraccion = "/" in respuesta
    try:
        esperado = fraccion(respuesta) if es_fraccion else numero(respuesta)
    except FormatoInvalido:
        return False
    if enunciado and _dado_en_otra_forma(enunciado, esperado, respuesta):
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
    return any(
        c.valor == esperado and not (es_fraccion and c.entero_suelto)
        for c in palabras.cantidades(texto)
    )


def _forma(escrito: str) -> str:
    return "fraccion" if "/" in escrito else "decimal" if "," in escrito else "entero"


def _dado_en_otra_forma(enunciado: str, esperado, respuesta: str) -> bool:
    """¿El enunciado trae el valor de la respuesta escrito de otra forma? Si lo trae en la misma
    ("tenía 12 y regaló 6", respuesta 6), es una coincidencia y el filtro sigue completo."""
    for cantidad in _CANTIDADES.findall(enunciado):
        try:
            valor = fraccion(cantidad) if "/" in cantidad else numero(cantidad)
        except FormatoInvalido:
            continue
        if valor == esperado and _forma(cantidad) != _forma(respuesta):
            return True
    return any(c.valor == esperado for c in palabras.cantidades(enunciado))


def _ordena(texto: str, respuesta: str) -> bool:
    """¿Aparecen todos los valores de la respuesta seguidos y en el orden pedido?"""
    try:
        pedidos = [fraccion(v) if "/" in v else numero(v) for v in respuesta.split(";")]
    except FormatoInvalido:
        return False
    vistos = []
    for cantidad in _CANTIDADES.findall(texto):
        try:
            vistos.append(fraccion(cantidad) if "/" in cantidad else numero(cantidad))
        except FormatoInvalido:
            continue
    n = len(pedidos)
    return any(vistos[i : i + n] == pedidos for i in range(len(vistos) - n + 1))


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


def sin_revelar(texto: str, respuesta: str, enunciado: str = "") -> str:
    """Filtro de no revelación (§6, capa determinista): si el texto revela la respuesta final,
    se reemplaza por un mensaje seguro. En una pista con operación en columnas se revisa la
    frase y el bloque se conserva (se arma sin el resultado; ver dominio/columnas.py)."""
    frase, bloque = separar_bloque(texto)
    if bloque is None:
        return RESPALDO if revela(texto, respuesta, enunciado) else texto
    return con_bloque(RESPALDO if revela(frase, respuesta, enunciado) else frase, bloque)


def personalizar(texto: str, alias: str) -> str:
    """El LLM escribe {nombre}; el alias se inserta aquí, en el servidor y después del filtro,
    así nunca viaja al proveedor (estrategia_llm.md §4)."""
    return texto.replace("{nombre}", alias)
