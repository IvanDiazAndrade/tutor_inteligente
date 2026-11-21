"""Plantillas paramétricas de 6° básico (modelo_dominio.md §4)."""

import random
from fractions import Fraction

from tutor.dominio.plantillas.base import (
    PALABRAS_DECIMALES,
    PALABRAS_LUGARES,
    EjercicioGenerado,
    _errores,
    _sin_revelar,
    decimal_cl,
    decimales,
    fijo,
    miles,
)

COMA = "Revisa dónde va la coma: cuenta los decimales del número decimal."


def _decimal(azar: random.Random, k: int, minimo: int, maximo: int) -> Fraction:
    """Un decimal con exactamente k decimales (la última cifra no es 0) entre minimo y maximo."""
    while True:
        n = azar.randint(minimo * 10**k, maximo * 10**k)
        if k == 0 or n % 10:
            v = Fraction(n, 10**k)
            if v > 0:
                return v


# 6B-OA7: multiplicación y división de decimales por naturales y por 10, 100 y 1.000 -----


class DecimalesPorNatural:
    id = "6B-OA7-mult-div-decimales"
    unidad_id = "6B-OA7"
    version = 1

    def instanciar(self, nivel: int, azar: random.Random) -> EjercicioGenerado:
        # N1: multiplicar o dividir por 10, 100 o 1.000 (mover la coma) · N2: un decimal por
        # un natural de una cifra · N3: un decimal dividido por un natural de una cifra, exacto.
        # Resultados hasta la milésima.
        if nivel == 1:
            return self._potencia(azar)
        if nivel == 2:
            return self._por_natural(azar)
        return self._entre_natural(azar)

    def _ejercicio(self, nivel, enunciado, respuesta, solucion, errores, pistas):
        return EjercicioGenerado(
            unidad_id=self.unidad_id,
            plantilla_id=self.id,
            nivel=nivel,
            enunciado=enunciado,
            formato_respuesta="numerico",
            respuesta_final=respuesta,
            solucion_referencia=solucion,
            errores_comunes=_errores(respuesta, errores),
            pistas=[
                _sin_revelar(p, respuesta, "Ya casi: falta poner la coma en su lugar.")
                for p in pistas
            ],
        )

    def _potencia(self, azar: random.Random) -> EjercicioGenerado:
        multiplica = azar.random() < 0.5
        while True:
            j = azar.randint(1, 2) if multiplica else azar.randint(1, 3)
            if multiplica:
                x = _decimal(azar, azar.randint(1, 3), 0, 99 // 10 ** (j - 1))
            else:
                x = _decimal(azar, azar.randint(0, 3 - j), 1, 999)
            r = x * 10**j if multiplica else x / 10**j
            if decimales(r) <= 3 and r < 1000 and r != x:
                break
        potencia = 10**j
        respuesta = decimal_cl(r)
        signo, lado = ("×", "derecha") if multiplica else (":", "izquierda")
        lugares = PALABRAS_LUGARES[j]
        contrario = x / potencia if multiplica else x * potencia
        errores = [
            (
                decimal_cl(contrario),
                "movió la coma hacia el lado contrario",
                "Al multiplicar el número crece y la coma va a la derecha; al dividir, "
                "achica y va a la izquierda.",
            ),
            (
                decimal_cl(r * 10 if multiplica else r / 10),
                "movió la coma un lugar de más",
                "Cuenta los ceros: la coma se mueve tantos lugares como ceros tiene "
                f"el {'factor' if multiplica else 'divisor'}.",
            ),
        ]
        if j > 1:
            errores.append(
                (
                    decimal_cl(r / 10 if multiplica else r * 10),
                    "movió la coma un lugar de menos",
                    "Cuenta los ceros: la coma se mueve tantos lugares como ceros tiene "
                    f"el {'factor' if multiplica else 'divisor'}.",
                )
            )
        return self._ejercicio(
            1,
            f"Calcula {decimal_cl(x)} {signo} {miles(potencia)}.",
            respuesta,
            [
                f"{'Multiplicar' if multiplica else 'Dividir'} por {miles(potencia)} es mover "
                f"la coma {lugares} a la {lado}; si faltan cifras, se completan con ceros.",
                f"{decimal_cl(x)} {signo} {miles(potencia)} = {respuesta}.",
            ],
            errores,
            [
                "Al multiplicar por 10, 100 o 1.000 la coma se mueve a la derecha; al dividir, "
                "a la izquierda.",
                f"Cuenta los ceros: la coma se mueve {lugares}.",
                f"Mueve la coma de {decimal_cl(x)} {lugares} a la {lado}.",
            ],
        )

    def _por_natural(self, azar: random.Random) -> EjercicioGenerado:
        while True:
            k = azar.randint(1, 2)
            x, n = _decimal(azar, k, 0, 49), azar.randint(2, 9)
            r = x * n
            if decimales(r) > 0:
                break
        X, P = int(x * 10**k), int(r * 10**k)
        respuesta = decimal_cl(r)
        final = fijo(r, k)
        palabras = PALABRAS_DECIMALES[k]
        ultimo = f"Como {decimal_cl(x)} tiene {palabras}, el producto también: {final}"
        ultimo += f", es decir, {respuesta}." if final != respuesta else "."
        return self._ejercicio(
            2,
            f"Calcula {decimal_cl(x)} × {n}.",
            respuesta,
            [f"Se multiplica como si no hubiera coma: {X} × {n} = {P}.", ultimo],
            [
                (str(P), "olvidó poner la coma", COMA),
                (decimal_cl(r * 10), "dejó un decimal de menos", COMA),
                (decimal_cl(r / 10), "dejó un decimal de más", COMA),
            ],
            [
                "Multiplica como si no hubiera coma y al final pon la coma.",
                f"Calcula {X} × {n}.",
                f"{X} × {n} = {P}. Ahora pon la coma: el número decimal tiene {palabras}.",
            ],
        )

    def _entre_natural(self, azar: random.Random) -> EjercicioGenerado:
        while True:
            k = azar.randint(1, 2)
            q, n = _decimal(azar, k, 0, 19), azar.randint(2, 9)
            d = q * n
            # El dividendo tiene los mismos decimales que el cociente: la división es directa.
            if decimales(d) == k:
                break
        D, Q = int(d * 10**k), int(q * 10**k)
        respuesta = decimal_cl(q)
        palabras = PALABRAS_DECIMALES[k]
        return self._ejercicio(
            3,
            f"Calcula {decimal_cl(d)} : {n}.",
            respuesta,
            [
                f"Se divide como si no hubiera coma: {D} : {n} = {Q}.",
                f"El cociente tiene tantos decimales como el dividendo ({palabras}): "
                f"el resultado es {respuesta}.",
            ],
            [
                (str(Q), "olvidó poner la coma", COMA),
                (decimal_cl(q * 10), "dejó un decimal de menos", COMA),
                (decimal_cl(q / 10), "dejó un decimal de más", COMA),
            ],
            [
                "Divide como si no hubiera coma; al final, el cociente lleva tantos decimales "
                "como el dividendo.",
                f"Calcula {D} : {n}.",
                f"{D} : {n} = {Q}. Ahora pon la coma: el dividendo tiene {palabras}.",
            ],
        )
