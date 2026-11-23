"""Números escritos en palabras, para el filtro de no revelación (modelo_pedagogico.md §6;
tarea 66). Funciones puras.

Lee lo que un tutor escribiría en un mensaje: enteros ("mil doscientos treinta y cuatro"),
fracciones ("tres cuartos", "un medio", "5 octavos", "siete doceavos"), decimales ("dos coma
cinco", "cinco décimas", "dos enteros y veinticinco centésimas") y números mixtos ("dos enteros
y tres cuartos", "dos y medio").

El lector prefiere equivocarse hacia el lado seguro: si algo puede leerse como la respuesta, el
filtro lo bloquea y el estudiante recibe la pista local. Lo único que se ignora a propósito es
"un"/"una" sueltos ("un número", "una pizza"), que no son una cantidad sino un artículo.
"""

import re
import unicodedata
from dataclasses import dataclass
from fractions import Fraction

UNIDADES = {
    "cero": 0, "uno": 1, "un": 1, "una": 1, "dos": 2, "tres": 3, "cuatro": 4, "cinco": 5,
    "seis": 6, "siete": 7, "ocho": 8, "nueve": 9, "diez": 10, "once": 11, "doce": 12,
    "trece": 13, "catorce": 14, "quince": 15, "dieciseis": 16, "diecisiete": 17,
    "dieciocho": 18, "diecinueve": 19, "veinte": 20, "veintiuno": 21, "veintiun": 21,
    "veintiuna": 21, "veintidos": 22, "veintitres": 23, "veinticuatro": 24, "veinticinco": 25,
    "veintiseis": 26, "veintisiete": 27, "veintiocho": 28, "veintinueve": 29,
}  # fmt: skip
DECENAS = {
    "treinta": 30, "cuarenta": 40, "cincuenta": 50, "sesenta": 60, "setenta": 70,
    "ochenta": 80, "noventa": 90,
}  # fmt: skip
CENTENAS = {
    "cien": 100, "ciento": 100, "doscientos": 200, "doscientas": 200, "trescientos": 300,
    "trescientas": 300, "cuatrocientos": 400, "cuatrocientas": 400, "quinientos": 500,
    "quinientas": 500, "seiscientos": 600, "seiscientas": 600, "setecientos": 700,
    "setecientas": 700, "ochocientos": 800, "ochocientas": 800, "novecientos": 900,
    "novecientas": 900,
}  # fmt: skip
# Denominadores: "un cuarto", "tres décimos", "cinco décimas" (las dos formas se usan en clases).
DENOMINADORES = {
    "medio": 2, "media": 2, "tercio": 3, "cuarto": 4, "quinto": 5, "sexto": 6, "septimo": 7,
    "setimo": 7, "octavo": 8, "noveno": 9, "decimo": 10, "decima": 10, "centesimo": 100,
    "centesima": 100, "milesimo": 1000, "milesima": 1000,
}  # fmt: skip
ARTICULOS = {"un", "una"}


@dataclass(frozen=True)
class Cantidad:
    valor: Fraction
    entero_suelto: bool  # un entero sin denominador ("tres"), que en fracciones suele ser operando


def sin_tildes(texto: str) -> str:
    descompuesto = unicodedata.normalize("NFD", texto.lower())
    return "".join(c for c in descompuesto if unicodedata.category(c) != "Mn")


def _fichas(texto: str) -> list[str]:
    """Palabras y números en cifras, en orden; la puntuación corta las secuencias."""
    return re.findall(r"\d+|[a-zñ]+|[^\sa-zñ\d]", sin_tildes(texto))


def _denominador(palabra: str) -> int | None:
    singular = palabra[:-1] if palabra.endswith("s") else palabra
    if singular in DENOMINADORES:
        return DENOMINADORES[singular]
    # Los demás se forman con -avo: onceavos, doceavos, treceavos, dieciseisavos, veinteavos.
    if singular.endswith("avo") and singular[:-3] in UNIDADES and UNIDADES[singular[:-3]] > 10:
        return UNIDADES[singular[:-3]]
    return None


def _entero(fichas: list[str], i: int) -> tuple[int, int, bool] | None:
    """Lee un entero en palabras (o en cifras) desde la posición i: (valor, posición siguiente,
    ¿es solo un artículo?). Cada palabra tiene que ser menor que la anterior ("doscientos
    treinta y cuatro"), salvo mil y millón, que multiplican: así "dos tres" no se lee como 5."""
    if i < len(fichas) and fichas[i].isdigit():
        return int(fichas[i]), i + 1, False
    total, actual, tope, j, leidas = 0, 0, None, i, []
    while j < len(fichas):
        palabra = fichas[j]
        if palabra in CENTENAS and (tope is None or tope >= 1000) and actual == 0:
            actual, tope = CENTENAS[palabra], 100 if palabra != "cien" else 1
        elif palabra in DECENAS and (tope is None or tope >= 100) and actual % 100 == 0:
            actual, tope = actual + DECENAS[palabra], 10
            # "treinta y cuatro": la "y" solo une una decena con una unidad.
            if (
                j + 2 < len(fichas)
                and fichas[j + 1] == "y"
                and UNIDADES.get(fichas[j + 2], 0) in range(1, 10)
            ):
                actual, tope, j = actual + UNIDADES[fichas[j + 2]], 1, j + 2
        elif palabra in UNIDADES and (tope is None or tope >= 100):
            if palabra == "cero" and leidas:
                break
            actual, tope = actual + UNIDADES[palabra], 1
        elif palabra == "mil" and (total == 0 or total >= 10**6) and actual < 1000:
            total, actual, tope = total + max(actual, 1) * 1000, 0, 1000
        elif palabra in ("millon", "millones") and total == 0:
            total, actual, tope = max(actual, 1) * 10**6, 0, 10**6 + 1
        else:
            break
        leidas.append(palabra)
        j += 1
    if not leidas:
        return None
    return total + actual, j, leidas in (["un"], ["una"])


def _decimales(fichas: list[str], i: int) -> tuple[Fraction, int] | None:
    """Lo que va después de "coma": "cinco" (0,5), "veinticinco" (0,25), "cero cinco" (0,05)."""
    ceros = 0
    while i < len(fichas) and fichas[i] == "cero":
        ceros, i = ceros + 1, i + 1
    leido = _entero(fichas, i)
    if leido is None or leido[2]:
        return None
    valor, siguiente, _ = leido
    return Fraction(valor, 10 ** (ceros + len(str(valor)))), siguiente


def _parte_fraccionaria(fichas: list[str], i: int) -> tuple[Fraction, int] | None:
    """Una fracción en palabras desde i: "tres cuartos", "un medio", "5 octavos"."""
    leido = _entero(fichas, i)
    if leido is None:
        return None
    numerador, j, _ = leido
    if j < len(fichas) and (denominador := _denominador(fichas[j])):
        return Fraction(numerador, denominador), j + 1
    return None


def cantidades(texto: str) -> list[Cantidad]:
    """Las cantidades escritas en palabras (con o sin cifras) que aparecen en un texto."""
    fichas = _fichas(texto)
    encontradas: list[Cantidad] = []
    i = 0
    while i < len(fichas):
        leido = _entero(fichas, i)
        if leido is None:
            i += 1
            continue
        entero, j, articulo = leido
        posicion = fichas[i] in ("mil", "millon", "millones") and fichas[i - 1 : i] == ["de"]
        if j == i + 1 and posicion:
            articulo = True  # "unidades de mil" nombra una posición, no una cantidad
        siguiente = fichas[j] if j < len(fichas) else None
        if siguiente is not None and (denominador := _denominador(siguiente)):
            encontradas.append(Cantidad(Fraction(entero, denominador), False))
            i = j + 1
            continue
        if siguiente == "coma" and (decimal := _decimales(fichas, j + 1)):
            encontradas.append(Cantidad(entero + decimal[0], False))
            i = decimal[1]
            continue
        # "dos enteros y tres cuartos", "dos y tres cuartos", "dos y medio", "dos enteros".
        k = j + 1 if siguiente in ("entero", "enteros") else j
        if k < len(fichas) and fichas[k] == "y" and not articulo:
            if k + 1 < len(fichas) and fichas[k + 1] in ("medio", "media"):
                encontradas.append(Cantidad(entero + Fraction(1, 2), False))
                i = k + 2
                continue
            if parte := _parte_fraccionaria(fichas, k + 1):
                encontradas.append(Cantidad(entero + parte[0], False))
                i = parte[1]
                continue
        # "los dos números", "las tres pistas": cuentan cosas del ejercicio, no son un resultado.
        contadas = i > 0 and fichas[i - 1] in ("los", "las", "ambos", "ambas")
        if not articulo and not contadas and not fichas[i].isdigit():
            encontradas.append(Cantidad(Fraction(entero), True))
        i = max(k, i + 1)
    return encontradas
