"""Pipeline de verificación de ejercicios verbales generados por el LLM: capas 1 y 2
(modelo_dominio.md §8; AD-9). Funciones puras: reciben el ejercicio y devuelven el motivo del
descarte, o None si pasa.

Capa 1 (aritmética exacta): cada operación escrita en la solución se recalcula con fracciones
exactas; los números que usa tienen que salir del enunciado o de un paso anterior, y el
resultado tiene que ser la respuesta final. Nada de floats: 0,1 + 0,2 da exactamente 0,3.
Capa 2 (curricular y de forma): largo del enunciado, pregunta explícita, montos en pesos dentro
del rango del OA, pistas y retroalimentaciones que no revelan la respuesta, errores comunes
legibles y distintos de la respuesta.
"""

import re
from fractions import Fraction
from typing import Any, Protocol

from tutor.dominio.corrector import FormatoInvalido, fraccion, numero
from tutor.dominio.plantillas.base import decimal_cl, miles
from tutor.mensajes import revela

# Número escrito como en Chile: 1.500 · 2,75 · 3/4 · 1 1/2 (el punto solo como separador de miles).
NUMERO = r"(?:\d{1,3}(?:\.\d{3})+(?:,\d+)?|\d+(?:,\d+)?(?:\s\d+/\d+|/\d+)?)"
_OPERANDO = rf"\(*\s*{NUMERO}\s*\)*"
_EXPRESION = rf"{_OPERANDO}(?:\s*[-+×:]\s*{_OPERANDO})+"
_IGUALDAD = re.compile(rf"(?<![\d,./])({_EXPRESION})\s*=\s*({NUMERO})(?![\d/])")
_FICHA = re.compile(rf"{NUMERO}|[-+×:()]")
_NUMERO = re.compile(rf"(?<![\d,./]){NUMERO}(?![\d/])")
# Números chicos que una solución puede usar sin que estén escritos ("la mitad" es : 2).
CONSTANTES = {Fraction(n) for n in range(13)} | {Fraction(10**k) for k in range(1, 4)}
MONEDA_EXTRANJERA = re.compile(r"d[óo]lar|euro|€|US\$|USD", re.IGNORECASE)


class EjercicioVerbal(Protocol):
    enunciado: str
    formato_respuesta: str
    respuesta_final: str
    solucion_referencia: list[str]
    errores_comunes: list[Any]  # objetos con .respuesta, .causa y .retroalimentacion
    pistas: list[str]


def normalizar(texto: str) -> str:
    """Sin signo peso y con los signos de operación de siempre: × para multiplicar, : para
    dividir y - para restar."""
    t = texto.replace("$", "").replace("−", "-").replace("–", "-").replace("÷", ":")
    return re.sub(r"(?<=\d)\s*[x·*×]\s*(?=\d)", " × ", t)


def valor(texto: str) -> Fraction:
    texto = texto.strip()
    return fraccion(texto) if "/" in texto else numero(texto)


def valores(texto: str) -> set[Fraction]:
    """Todos los números que aparecen en un texto."""
    encontrados = set()
    for n in _NUMERO.findall(normalizar(texto)):
        try:
            encontrados.add(valor(n))
        except (FormatoInvalido, ValueError):
            continue
    return encontrados


def _evaluar(fichas: list[str]) -> Fraction:
    """Expresión con + - × : y paréntesis, con la prioridad de siempre (recursivo descendente)."""
    posicion = 0

    def mirar() -> str | None:
        return fichas[posicion] if posicion < len(fichas) else None

    def tomar() -> str:
        nonlocal posicion
        posicion += 1
        return fichas[posicion - 1]

    def factor() -> Fraction:
        if mirar() == "(":
            tomar()
            v = expresion()
            if tomar() != ")":
                raise ValueError("paréntesis sin cerrar")
            return v
        return valor(tomar())

    def termino() -> Fraction:
        v = factor()
        while mirar() in ("×", ":"):
            if tomar() == "×":
                v *= factor()
            else:
                v /= factor()  # ZeroDivisionError si divide por 0
        return v

    def expresion() -> Fraction:
        v = termino()
        while mirar() in ("+", "-"):
            v = v + termino() if tomar() == "+" else v - termino()
        return v

    resultado = expresion()
    if posicion != len(fichas):
        raise ValueError("sobran fichas")
    return resultado


def operaciones(texto: str) -> list[tuple[str, Fraction, Fraction, list[Fraction]]]:
    """Las igualdades "expresión = resultado" de un texto: (expresión, valor calculado, valor
    escrito, operandos). Las que no se pueden leer se omiten."""
    encontradas = []
    for expresion, escrito in _IGUALDAD.findall(normalizar(texto)):
        fichas = _FICHA.findall(expresion)
        try:
            calculado = _evaluar(fichas)
            operandos = [valor(f) for f in fichas if f not in "+-×:()"]
            encontradas.append((expresion.strip(), calculado, valor(escrito), operandos))
        except (FormatoInvalido, ValueError, ZeroDivisionError, IndexError):
            continue
    return encontradas


def _escrito(v: Fraction) -> str:
    if v.denominator == 1:
        return miles(int(v))
    return decimal_cl(v) if (v * 1000).denominator == 1 else f"{v.numerator}/{v.denominator}"


def verificar_aritmetica(ej: EjercicioVerbal) -> str | None:
    """Capa 1. Devuelve el motivo del descarte, o None."""
    try:
        esperado = _respuesta(ej.respuesta_final, ej.formato_respuesta)
    except FormatoInvalido:
        return f"la respuesta final «{ej.respuesta_final}» no es un {ej.formato_respuesta}"
    pasos = [op for paso in ej.solucion_referencia for op in operaciones(paso)]
    if not pasos:
        return "la solución no tiene operaciones que se puedan verificar"
    disponibles = valores(ej.enunciado) | CONSTANTES
    for expresion, calculado, escrito, operandos in pasos:
        if calculado != escrito:
            return f"paso aritmético incorrecto: {expresion} da {_escrito(calculado)}"
        for operando in operandos:
            if operando not in disponibles:
                return (
                    f"la solución usa el número {_escrito(operando)}, que no está en el enunciado"
                )
        disponibles.add(escrito)
    if esperado != pasos[-1][2] and esperado not in valores(ej.solucion_referencia[-1]):
        return "la respuesta final no es el resultado de la solución"
    return None


def _respuesta(texto: str, formato: str) -> Fraction:
    if formato == "fraccion":
        return fraccion(texto)
    if formato == "numerico":
        return numero(texto)
    raise FormatoInvalido(f"formato no admitido para un ejercicio verbal: {formato}")


def verificar_forma(ej: EjercicioVerbal, curso: int, rango: dict[str, Any]) -> str | None:
    """Capa 2. Devuelve el motivo del descarte, o None."""
    palabras = len(ej.enunciado.split())
    tope = 60 if curso == 4 else 80
    if palabras > tope:
        return f"el enunciado tiene {palabras} palabras (máximo {tope} en {curso}° básico)"
    if "?" not in ej.enunciado:
        return "el enunciado no hace una pregunta"
    if MONEDA_EXTRANJERA.search(ej.enunciado):
        return "el contexto usa una moneda que no es el peso chileno"
    montos = [valor(m) for m in re.findall(rf"\$\s?({NUMERO})", ej.enunciado)]
    minimo, maximo = rango.get("monto_min"), rango.get("monto_max")
    for monto in montos:
        if (minimo and monto < minimo) or (maximo and monto > maximo):
            return f"el monto ${_escrito(monto)} está fuera del rango del OA"
        if rango.get("multiplo_de") and monto % rango["multiplo_de"]:
            return f"el monto ${_escrito(monto)} no es múltiplo de {rango['multiplo_de']}"
    if len(ej.pistas) != 3:
        return "no trae exactamente 3 pistas"
    for i, pista in enumerate(ej.pistas, 1):
        if revela(pista, ej.respuesta_final, ej.enunciado):
            return f"la pista {i} revela la respuesta"
    esperado = _respuesta(ej.respuesta_final, ej.formato_respuesta)
    if not ej.errores_comunes:
        return "no trae errores comunes"
    for error in ej.errores_comunes:
        try:
            if _respuesta(error.respuesta, ej.formato_respuesta) == esperado:
                return f"el error común «{error.respuesta}» vale lo mismo que la respuesta"
        except FormatoInvalido:
            return f"el error común «{error.respuesta}» no se puede leer"
        if revela(error.retroalimentacion, ej.respuesta_final, ej.enunciado):
            return "una retroalimentación de error revela la respuesta"
    return None


def verificar(ej: EjercicioVerbal, curso: int, rango: dict[str, Any]) -> str | None:
    """Capas 1 y 2, en orden. El primer motivo de descarte, o None si el ejercicio pasa."""
    return verificar_aritmetica(ej) or verificar_forma(ej, curso, rango)


def respuesta_canonica(texto: str, formato: str) -> str:
    """Cómo se guarda la respuesta: sin $ ni puntos de miles (3800, 2,5) o la fracción tal
    cual (3/4, 1 1/2). Así el corrector no confunde "$3.800" con 3,8."""
    if formato == "numerico":
        return decimal_cl(numero(texto))
    return re.sub(r"\s*/\s*", "/", " ".join(texto.split()))
