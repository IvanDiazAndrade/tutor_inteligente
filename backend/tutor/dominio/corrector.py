"""Corrector programático (modelo_dominio.md §3; AD-2: el LLM nunca califica).

Función pura: corregir(respuesta_cruda, ejercicio) -> ResultadoCorreccion. Toda la aritmética
es exacta con fractions.Fraction: nunca se usan números de punto flotante (0,1 + 0,2 debe dar
exactamente 0,3). El mismo normalizador lo usa el filtro de no revelación del tutor.
"""

import re
from collections.abc import Sequence
from dataclasses import dataclass
from fractions import Fraction
from typing import Any, Literal, Protocol

Formato = Literal["numerico", "fraccion", "ordenar", "comparar"]
SIMBOLOS_COMPARAR = {"<", "=", ">"}


class EjercicioCorregible(Protocol):
    formato_respuesta: str
    respuesta_final: str
    regla_validacion: dict[str, Any]
    errores_comunes: Sequence[dict[str, Any]]


@dataclass(frozen=True)
class ResultadoCorreccion:
    estado: Literal["correcta", "incorrecta", "formato_invalido"]
    # Correcta pero escrita en otra forma aceptada (p. ej. 6/8 cuando la canónica es 3/4).
    forma_distinta: bool = False
    error_comun: dict[str, Any] | None = None
    mensaje: str | None = None  # solo para formato_invalido

    @property
    def cuenta_como_intento(self) -> bool:
        """Lo rechazado por formato no es evidencia de dominio (modelo_estudiante.md §1)."""
        return self.estado != "formato_invalido"


class FormatoInvalido(ValueError):
    """La entrada no se puede interpretar; el mensaje se muestra al estudiante."""


# Normalización (§3.1) ----------------------------------------------------------------------

_MILES = re.compile(r"^\d{1,3}(\.\d{3})+$")


def _limpiar(texto: str) -> str:
    texto = texto.strip().lower().replace("$", "").replace("pesos", "")
    return re.sub(r"\s+", " ", texto).strip()


def _decimales_de(canonico: str) -> int:
    """Cuántas posiciones decimales tiene la respuesta esperada (0 si es entera)."""
    partes = canonico.replace(",", ".").split(".")
    return len(partes[1]) if len(partes) == 2 else 0


def numero(texto: str, esperado: str | None = None) -> Fraction:
    """Convierte un número escrito por un niño a Fraction exacta.

    - Coma y punto decimal valen igual (0,5 = 0.5 = ,5).
    - El punto de miles (1.000, 12.500) se elimina; si "1.500" es ambiguo, decide el formato
      esperado: si la respuesta esperada es entera se lee mil quinientos.
    """
    t = _limpiar(texto).replace(" ", "")
    if not t:
        raise FormatoInvalido("Escribe un número.")
    negativo = t.startswith("-")
    t = t.lstrip("-")
    if _MILES.match(t) and (esperado is None or _decimales_de(esperado) == 0):
        t = t.replace(".", "")
    t = t.replace(",", ".")
    if not re.fullmatch(r"\d*\.?\d*", t) or t in {"", "."} or t.count(".") > 1:
        raise FormatoInvalido("Escribe un número.")
    entero, _, decimales = t.partition(".")
    valor = Fraction(int(entero or "0")) + (
        Fraction(int(decimales), 10 ** len(decimales)) if decimales else 0
    )
    return -valor if negativo else valor


def fraccion(texto: str) -> Fraction:
    """a/b o número mixto "c a/b". Denominador 0 es formato inválido."""
    t = _limpiar(texto)
    mixto = re.fullmatch(r"(\d+)\s+(\d+)\s*/\s*(\d+)", t)
    simple = re.fullmatch(r"(\d+)\s*/\s*(\d+)", t)
    if mixto:
        entero, num, den = (int(g) for g in mixto.groups())
    elif simple:
        entero, (num, den) = 0, (int(g) for g in simple.groups())
    elif re.fullmatch(r"\d+", t):
        return Fraction(int(t))  # un entero también es una fracción válida (4/4 = 1)
    else:
        raise FormatoInvalido("Escribe la fracción con el número de arriba y el de abajo.")
    if den == 0:
        raise FormatoInvalido("El número de abajo no puede ser 0.")
    return entero + Fraction(num, den)


def _misma_escritura(texto: str, canonico: str) -> bool:
    return re.sub(r"\s", "", _limpiar(texto)) == re.sub(r"\s", "", _limpiar(canonico))


def _secuencia(texto: str) -> list[Fraction]:
    """Valores ordenados separados por punto y coma, como los arma la app: "1/4; 0,5; 1 1/2"."""
    partes = [p for p in _limpiar(texto).split(";") if p.strip()]
    if len(partes) < 2:
        raise FormatoInvalido("Ordena todos los valores.")
    return [fraccion(p) if "/" in p else numero(p) for p in partes]


# Corrección por formato (§3.2) ---------------------------------------------------------


def _valor(texto: str, formato: str, esperado: str) -> Any:
    if formato == "numerico":
        return numero(texto, esperado)
    if formato == "fraccion":
        return fraccion(texto)
    if formato == "ordenar":
        return _secuencia(texto)
    if formato == "comparar":
        simbolo = _limpiar(texto)
        if simbolo not in SIMBOLOS_COMPARAR:
            raise FormatoInvalido("Elige <, = o >.")
        return simbolo
    raise ValueError(f"formato desconocido: {formato}")


def corregir(respuesta: str, ejercicio: EjercicioCorregible) -> ResultadoCorreccion:
    formato = ejercicio.formato_respuesta
    canonico = ejercicio.respuesta_final
    try:
        dada = _valor(respuesta, formato, canonico)
    except FormatoInvalido as error:
        return ResultadoCorreccion("formato_invalido", mensaje=str(error))
    esperada = _valor(canonico, formato, canonico)

    if dada == esperada:
        if formato == "fraccion":
            # Fraction compara por valor: 6/8 == 3/4. Si el OA exige la forma (simplificar,
            # impropia <-> mixto), solo vale la escritura canónica.
            exacta = _misma_escritura(respuesta, canonico)
            if not exacta and not ejercicio.regla_validacion.get("aceptaEquivalentes", True):
                return _incorrecta(respuesta, ejercicio)
            return ResultadoCorreccion("correcta", forma_distinta=not exacta)
        return ResultadoCorreccion("correcta")
    return _incorrecta(respuesta, ejercicio)


def _incorrecta(respuesta: str, ejercicio: EjercicioCorregible) -> ResultadoCorreccion:
    """Busca si la respuesta coincide con un error común anticipado (diagnóstico, RF-P2):
    primero escrito igual y, si no, por valor (6/16 también delata sumar denominadores)."""
    formato, canonico = ejercicio.formato_respuesta, ejercicio.respuesta_final
    for error in ejercicio.errores_comunes:
        if _misma_escritura(respuesta, error["respuesta"]):
            return ResultadoCorreccion("incorrecta", error_comun=error)
    try:
        dada = _valor(respuesta, formato, canonico)
    except FormatoInvalido:
        return ResultadoCorreccion("incorrecta")
    for error in ejercicio.errores_comunes:
        try:
            if _valor(error["respuesta"], formato, canonico) == dada:
                return ResultadoCorreccion("incorrecta", error_comun=error)
        except FormatoInvalido:
            continue
    return ResultadoCorreccion("incorrecta")
