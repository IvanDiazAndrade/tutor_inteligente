"""Piezas comunes de las plantillas paramétricas (AD-9; modelo_dominio.md §4).

Las usan `plantillas.py` y las fichas de cada curso. Toda la aritmética es exacta (enteros y
Fraction): nunca se usan números de punto flotante.
"""

import random
import re
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Any, Protocol

from tutor.dominio.corrector import FormatoInvalido, fraccion, numero


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


def _clave(texto: str) -> Any:
    """Valor de una respuesta para comparar errores; los símbolos y secuencias, por su texto."""
    for convertir in (fraccion, numero):
        try:
            return convertir(texto)
        except FormatoInvalido:
            continue
    return texto


def _errores(respuesta: str, candidatos: list[tuple[str, str, str]]) -> list[dict[str, str]]:
    """Descarta errores que valen lo mismo que la respuesta o que otro error (p. ej. 2/4 y 1/2):
    un patrón ambiguo no sirve para diagnosticar la causa."""
    vistos = {_clave(respuesta)}
    errores = []
    for valor, causa, retro in candidatos:
        if _clave(valor) not in vistos:
            vistos.add(_clave(valor))
            errores.append({"respuesta": valor, "causa": causa, "retroalimentacion": retro})
    return errores


def menciona(texto: str, respuesta: str) -> bool:
    """¿El texto contiene la respuesta como número o fracción suelto (no dentro de otro)?"""
    return re.search(rf"(?<![\d/]){re.escape(respuesta)}(?![\d/])", texto) is not None


# Números, fracciones y números mixtos que aparecen en un texto ("1 1/2", "6/8", "0,75", "12.500").
CANTIDADES = re.compile(r"\d+\s+\d+\s*/\s*\d+|\d+\s*/\s*\d+|\d+(?:[.,]\d+)*")


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
    for cantidad in CANTIDADES.findall(texto):
        if es_fraccion and re.fullmatch(r"\d+", cantidad):
            continue  # en respuestas fraccionarias, un entero suelto suele ser un operando
        try:
            valor = fraccion(cantidad) if "/" in cantidad else numero(cantidad, respuesta)
        except FormatoInvalido:
            continue
        if valor == esperado:
            return True
    return False


def _sin_revelar(pista: str, respuesta: str, alternativa: str) -> str:
    """Si por casualidad la pista nombra la respuesta (p. ej. 99 : 9 -> "divide 11 : 9"),
    se usa una versión sin números. El filtro del tutor lo revisa de nuevo al servirla."""
    return alternativa if revela(pista, respuesta) else pista


# Escritura de números (convención chilena, RF-P6) ------------------------------------------


def miles(n: int) -> str:
    """12500 -> "12.500"."""
    return f"{n:,}".replace(",", ".")


def decimal(valor: Fraction | int) -> str:
    """Escribe un valor decimal exacto con coma y sin ceros de más: Fraction(5, 4) -> "1,25"."""
    valor = Fraction(valor)
    posiciones = 0
    while (valor * 10**posiciones).denominator != 1:
        posiciones += 1
    escalado = int(valor * 10**posiciones)
    if posiciones == 0:
        return str(escalado)
    entero, resto = divmod(escalado, 10**posiciones)
    return f"{entero},{resto:0{posiciones}d}"


def mixto(valor: Fraction) -> str:
    """Fraction(7, 3) -> "2 1/3"; un entero se escribe solo y una fracción propia, como a/b."""
    entero, resto = divmod(valor.numerator, valor.denominator)
    if resto == 0:
        return str(entero)
    return f"{entero} {resto}/{valor.denominator}" if entero else f"{resto}/{valor.denominator}"


def circulo(denominador: int, *partes: int) -> dict[str, Any]:
    return {
        "tipo": "fraccion-circulo",
        "parametros": {"denominador": denominador, "partesDestacadas": list(partes)},
    }


def recta(maximo: int, divisiones: int, punto: int) -> dict[str, Any]:
    """Recta de 0 a `maximo`, con `divisiones` tramos iguales y un punto en la marca `punto`."""
    return {
        "tipo": "recta-numerica",
        "parametros": {"minimo": 0, "maximo": maximo, "divisiones": divisiones, "punto": punto},
    }


def cuadricula(pintadas: int) -> dict[str, Any]:
    return {"tipo": "cuadricula-decimal", "parametros": {"pintadas": pintadas}}


Pista = str | tuple[str, str]  # texto, o (texto, alternativa si el texto revelara la respuesta)
_PISTA_GENERAL = "Vuelve a leer el enunciado y revisa cada paso con calma."


class Ficha:
    """Base de las plantillas: arma el ejercicio con el esquema de §2 y cuida las pistas."""

    id: str
    unidad_id: str
    version = 1

    def _crear(
        self,
        nivel: int,
        enunciado: str,
        formato: str,
        respuesta: str,
        solucion: list[str],
        errores: list[tuple[str, str, str]],
        pistas: list[Pista],
        equivalentes: bool = True,
        representacion: dict[str, Any] | None = None,
        entrada_mixta: bool = False,
    ) -> EjercicioGenerado:
        finales = []
        for pista in pistas:
            texto, alternativa = pista if isinstance(pista, tuple) else (pista, _PISTA_GENERAL)
            finales.append(_sin_revelar(texto, respuesta, alternativa))
        return EjercicioGenerado(
            unidad_id=self.unidad_id,
            plantilla_id=self.id,
            nivel=nivel,
            enunciado=enunciado,
            formato_respuesta=formato,
            respuesta_final=respuesta,
            solucion_referencia=solucion,
            errores_comunes=_errores(respuesta, errores),
            pistas=finales,
            # entradaMixta: la app muestra una casilla para el entero. Lo decide la plantilla y no
            # la respuesta, para no delatar cuándo un resultado da justo un número entero.
            regla_validacion={"aceptaEquivalentes": equivalentes, "entradaMixta": entrada_mixta},
            representacion=representacion,
        )

    def _comparar(
        self,
        nivel: int,
        izquierda: str,
        derecha: str,
        valores: tuple[Fraction, Fraction],
        pasos: list[str],
        causa: str,
        retro: str,
        pistas: list[Pista],
    ) -> EjercicioGenerado:
        a, b = valores
        signo = "<" if a < b else ">" if a > b else "="
        return self._crear(
            nivel,
            f"Compara {izquierda} y {derecha}. Elige el signo que corresponde: "
            f"{izquierda} __ {derecha}.",
            "comparar",
            signo,
            [*pasos, f"Por eso, {izquierda} {signo} {derecha}."],
            [(">" if signo != ">" else "<", causa, retro)],
            pistas,
        )

    def _ordenar(
        self,
        nivel: int,
        valores: list[tuple[Fraction, str]],
        azar: random.Random,
        pasos: list[str],
        retro: str,
        pistas: list[Pista],
        confusion: tuple[str, str, str] | None = None,
    ) -> EjercicioGenerado:
        """Ordenar de menor a mayor. Los valores viajan en `representacion`, ya desordenados:
        la app los muestra para tocarlos en orden (el corrector compara por valor)."""
        ordenados = [texto for _, texto in sorted(valores)]
        presentados = list(ordenados)
        while presentados == ordenados:
            azar.shuffle(presentados)
        errores = [("; ".join(reversed(ordenados)), "ordenó de mayor a menor", retro)]
        if confusion:
            errores.append(confusion)
        respuesta = "; ".join(ordenados)
        return self._crear(
            nivel,
            f"Ordena de menor a mayor: {'; '.join(presentados)}.",
            "ordenar",
            respuesta,
            [*pasos, f"De menor a mayor queda: {respuesta}."],
            errores,
            pistas,
            representacion={"tipo": "valores-ordenar", "parametros": {"valores": presentados}},
        )
