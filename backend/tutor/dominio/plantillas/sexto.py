"""Plantillas paramétricas de 6° básico (modelo_dominio.md §4)."""

import random
from fractions import Fraction
from math import gcd, lcm

from tutor.dominio.plantillas.base import (
    PALABRAS_DECIMALES,
    PALABRAS_LUGARES,
    SIMBOLO_EN_PALABRAS,
    EjercicioGenerado,
    _errores,
    _errores_texto,
    _sin_revelar,
    decimal_cl,
    decimales,
    fijo,
    miles,
    simbolo,
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


# Números mixtos (6B-OA5 y 6B-OA6) ---------------------------------------------------------


def mixto(v: Fraction) -> str:
    """Escritura de un número positivo como en la escuela: 2 3/4, 3 (entero) o 3/4 (propia)."""
    entero = v.numerator // v.denominator
    resto = v - entero
    if resto == 0:
        return str(entero)
    fraccion = f"{resto.numerator}/{resto.denominator}"
    return f"{entero} {fraccion}" if entero else fraccion


def _mixto_al_azar(azar: random.Random, d: int, entero_max: int) -> tuple[int, int, int]:
    """Entero, numerador y denominador de un número mixto con fracción propia irreducible."""
    while True:
        e, n = azar.randint(1, entero_max), azar.randint(1, d - 1)
        if gcd(n, d) == 1:
            return e, n, d


def _sin_simplificar(numerador: int, m: int, respuesta: str) -> str:
    """El resultado como número mixto con denominador m y, si se simplifica, su forma final:
    "2 2/4, es decir, 2 1/2"."""
    entero, resto = divmod(numerador, m)
    escrito = f"{entero} {resto}/{m}" if entero else f"{resto}/{m}"
    return escrito if escrito == respuesta else f"{escrito}, que simplificado es {respuesta}"


# 6B-OA5: fracciones impropias y números mixtos ------------------------------------------


class ImpropiasYMixtos:
    id = "6B-OA5-impropias-mixtos"
    unidad_id = "6B-OA5"
    version = 1
    DENOMINADORES = (2, 3, 4, 5, 6, 8)

    def instanciar(self, nivel: int, azar: random.Random) -> EjercicioGenerado:
        # N1: fracción impropia a número mixto · N2: número mixto a fracción impropia ·
        # N3: comparar un número mixto con una fracción impropia (a veces valen lo mismo).
        # En N1 y N2 la forma ES el objetivo: aceptaEquivalentes = false.
        e, n, d = _mixto_al_azar(azar, azar.choice(self.DENOMINADORES), 5)
        impropia = e * d + n
        texto_mixto, texto_impropia = f"{e} {n}/{d}", f"{impropia}/{d}"
        if nivel == 1:
            return self._a_mixto(e, n, d, impropia, texto_mixto, texto_impropia)
        if nivel == 2:
            return self._a_impropia(e, n, d, impropia, texto_mixto, texto_impropia)
        return self._comparar(e, n, d, azar)

    def _ejercicio(
        self, nivel, enunciado, formato, respuesta, solucion, errores, pistas, regla
    ) -> EjercicioGenerado:
        return EjercicioGenerado(
            unidad_id=self.unidad_id,
            plantilla_id=self.id,
            nivel=nivel,
            enunciado=enunciado,
            formato_respuesta=formato,
            respuesta_final=respuesta,
            solucion_referencia=solucion,
            errores_comunes=errores,
            pistas=pistas,
            regla_validacion=regla,
        )

    def _a_mixto(self, e, n, d, impropia, texto_mixto, texto_impropia) -> EjercicioGenerado:
        sobra = "sobra 1" if n == 1 else f"sobran {n}"
        return self._ejercicio(
            1,
            f"Escribe {texto_impropia} como número mixto.",
            "fraccion",
            texto_mixto,
            [
                f"Se divide el numerador por el denominador: {impropia} : {d} = {e} y {sobra}.",
                f"El cociente es la parte entera ({e}) y lo que sobra es el numerador de la "
                f"fracción ({n}/{d}).",
                f"{texto_impropia} = {texto_mixto}.",
            ],
            _errores_texto(
                texto_mixto,
                [
                    (
                        f"{n} {e}/{d}" if e < d and n != e else None,
                        "intercambió la parte entera y lo que sobra",
                        "El cociente de la división es la parte entera; "
                        "lo que sobra va arriba en la "
                        "fracción.",
                    ),
                    (
                        f"{e + 1} {n}/{d}",
                        "contó un entero de más",
                        f"Revisa cuántas veces cabe {d} en {impropia}.",
                    ),
                    (
                        texto_impropia,
                        "no la convirtió",
                        "Vale lo mismo, pero se pedía escribirla como número mixto.",
                    ),
                ],
            ),
            [
                "Un número mixto tiene una parte entera y una fracción propia.",
                f"Divide el numerador por el denominador: {impropia} : {d}.",
                f"{impropia} : {d} da {e} y {sobra}. El cociente es la parte entera y lo "
                "que sobra va en el numerador.",
            ],
            {"aceptaEquivalentes": False, "numeroMixto": True},
        )

    def _a_impropia(self, e, n, d, impropia, texto_mixto, texto_impropia) -> EjercicioGenerado:
        return self._ejercicio(
            2,
            f"Escribe {texto_mixto} como fracción impropia.",
            "fraccion",
            texto_impropia,
            [
                f"Se multiplica el entero por el denominador: {e} × {d} = {e * d}.",
                f"Se le suma el numerador: {e * d} + {n} = {impropia}.",
                f"El denominador se mantiene: {texto_mixto} = {texto_impropia}.",
            ],
            _errores_texto(
                texto_impropia,
                [
                    (
                        f"{e + n}/{d}",
                        "sumó el entero al numerador",
                        "Cada entero son varios cuartos, tercios...: "
                        "primero multiplica el entero por "
                        "el denominador.",
                    ),
                    (
                        f"{e * d}/{d}",
                        "olvidó sumar el numerador",
                        "Después de multiplicar el entero por el denominador, súmale el numerador.",
                    ),
                    (
                        f"{e * n + d}/{d}" if e * n + d != impropia else None,
                        "multiplicó el entero por el numerador",
                        "El entero se multiplica por el denominador, no por el numerador.",
                    ),
                    (
                        texto_mixto,
                        "no la convirtió",
                        "Vale lo mismo, pero se pedía escribirla como fracción impropia.",
                    ),
                ],
            ),
            [
                "Para pasar a fracción impropia, cuenta cuántas partes hay en total.",
                f"Multiplica el entero por el denominador: {e} × {d}.",
                f"{e} × {d} = {e * d}. Súmale el numerador y mantén el denominador.",
            ],
            {"aceptaEquivalentes": False},
        )

    def _comparar(self, e, n, d, azar: random.Random) -> EjercicioGenerado:
        x = Fraction(e * d + n, d)
        while True:
            d2 = azar.choice(self.DENOMINADORES)
            if azar.random() < 0.25 and (x * d2).denominator == 1:
                num_y = int(x * d2)  # la misma cantidad, como impropia: 2 1/4 y 9/4 o 18/8
            else:
                num_y = azar.randint(d2 + 1, 6 * d2)
            if num_y % d2:  # una fracción impropia, no un entero
                break
        y = Fraction(num_y, d2)
        tx, ty = f"{e} {n}/{d}", f"{num_y}/{d2}"
        sim = simbolo(x, y)
        m = d * d2 // gcd(d, d2)
        X, Y = int(x * m), int(y * m)
        retro = (
            "Escribe los dos de la misma forma, por ejemplo como fracciones impropias con el "
            "mismo denominador, y compara."
        )
        return self._ejercicio(
            3,
            f"¿Qué signo va entre {tx} y {ty}?",
            "comparar",
            sim,
            [
                f"Se escribe {tx} como fracción impropia: {e * d + n}/{d}.",
                f"Con denominador común {m}: {X}/{m} y {Y}/{m}.",
                f"Como {X} {SIMBOLO_EN_PALABRAS[sim]} {Y}, {tx} {sim} {ty}.",
            ],
            _errores_texto(
                sim,
                [
                    (
                        simbolo(Fraction(e), Fraction(num_y)),
                        "comparó la parte entera con el numerador",
                        retro,
                    ),
                    ({"<": ">", ">": "<", "=": None}[sim], "comparó al revés", retro),
                    (None if sim == "=" else "=", "pensó que valían lo mismo", retro),
                ],
            ),
            [
                "Para comparar, escribe los dos números de la misma forma.",
                f"Escribe {tx} como fracción impropia.",
                f"{tx} son {e * d + n} partes de {d}. Ahora escribe las dos fracciones con "
                f"denominador {m} y compara los numeradores.",
            ],
            {"aceptaEquivalentes": True, "valores": [tx, ty]},
        )


# 6B-OA6: suma y resta de números mixtos -------------------------------------------------


class SumaRestaMixtos:
    id = "6B-OA6-mixtos"
    unidad_id = "6B-OA6"
    version = 1
    DENOMINADORES = (2, 3, 4, 5, 6, 8, 10, 12)

    def instanciar(self, nivel: int, azar: random.Random) -> EjercicioGenerado:
        # N1: suma con igual denominador, sin canje (1 1/5 + 2 3/5) · N2: igual denominador,
        # suma con canje o resta con préstamo · N3: distinto denominador, suma o resta.
        while True:
            d1 = azar.choice(self.DENOMINADORES)
            d2 = d1 if nivel < 3 else azar.choice(self.DENOMINADORES)
            if nivel == 3 and (d1 == d2 or lcm(d1, d2) > 24):
                continue
            e1, n1, _ = _mixto_al_azar(azar, d1, 6)
            e2, n2, _ = _mixto_al_azar(azar, d2, 4)
            x, y = e1 + Fraction(n1, d1), e2 + Fraction(n2, d2)
            resta = nivel > 1 and azar.random() < 0.5
            if resta and x < y:
                e1, n1, d1, e2, n2, d2, x, y = e2, n2, d2, e1, n1, d1, y, x
            r = x - y if resta else x + y
            canje = Fraction(n1, d1) + Fraction(n2, d2) >= 1
            prestamo = Fraction(n1, d1) < Fraction(n2, d2)
            if r <= 0 or r == y or r.denominator == 1:
                continue
            if nivel == 1 and canje:
                continue
            if nivel == 2 and not (prestamo if resta else canje):
                continue
            break
        m = lcm(d1, d2)
        respuesta = mixto(r)
        tx, ty = f"{e1} {n1}/{d1}", f"{e2} {n2}/{d2}"
        signo = "−" if resta else "+"
        A, B = n1 * (m // d1), n2 * (m // d2)
        if resta:
            I1, I2 = int(x * m), int(y * m)
            solucion = [
                f"Se escriben como fracciones impropias con denominador {m}: {I1}/{m} y {I2}/{m}.",
                f"Se restan los numeradores: {I1} − {I2} = {I1 - I2}, y queda {I1 - I2}/{m}.",
                f"Como número mixto: {_sin_simplificar(I1 - I2, m, respuesta)}.",
            ]
            pistas = [
                "Escribe los dos números mixtos como fracciones impropias con el mismo "
                "denominador.",
                f"{tx} son {I1} partes de {m}, y {ty} son {I2} partes de {m}.",
                f"Resta {I1} − {I2} y escribe el resultado como número mixto.",
            ]
            candidatos = [
                (
                    f"{e1 - e2} {abs(A - B)}/{m}" if A != B and e1 > e2 else None,
                    "restó la fracción menor de la mayor",
                    "Si la fracción de arriba es menor, pide prestado un entero antes de restar.",
                ),
                (mixto(x + y), "sumó en vez de restar", "Fíjate en el signo: aquí hay que restar."),
            ]
        else:
            enteros, partes = e1 + e2, A + B
            solucion = [
                f"Se suman las partes enteras: {e1} + {e2} = {enteros}.",
                f"Se suman las fracciones con denominador {m}: {A}/{m} + {B}/{m} = {partes}/{m}.",
                (
                    f"Como {partes}/{m} es más que un entero, se canjea: {partes}/{m} = "
                    f"1 {partes - m}/{m}, y la parte entera queda en {enteros + 1}."
                )
                if canje
                else "La fracción es menor que un entero: no hay canje.",
                f"El resultado es {_sin_simplificar(int(r * m), m, respuesta)}.",
            ]
            pistas = [
                "Suma por separado las partes enteras y las fracciones.",
                f"Partes enteras: {e1} + {e2}. Fracciones: escríbelas con denominador {m}.",
                f"Las fracciones suman {partes} partes de {m}"
                + (": eso es más que un entero, así que canjea." if canje else ".")
                + " Ahora junta todo.",
            ]
            candidatos = [
                (
                    f"{enteros} {partes - m}/{m}" if canje and partes > m else None,
                    "olvidó sumar el entero del canje",
                    "Cuando las fracciones suman más que un entero, "
                    "ese entero se agrega a la parte "
                    "entera.",
                ),
                (
                    f"{enteros} {n1 + n2}/{d1 + d2}",
                    "sumó también los denominadores",
                    "Los denominadores no se suman: se busca un denominador común.",
                ),
                (
                    mixto(x - y) if x > y else None,
                    "restó en vez de sumar",
                    "Fíjate en el signo: aquí hay que sumar.",
                ),
            ]
        return EjercicioGenerado(
            unidad_id=self.unidad_id,
            plantilla_id=self.id,
            nivel=nivel,
            enunciado=f"Calcula {tx} {signo} {ty}.",
            formato_respuesta="fraccion",
            respuesta_final=respuesta,
            solucion_referencia=solucion,
            errores_comunes=_errores(respuesta, [c for c in candidatos if c[0]]),
            pistas=pistas,
            regla_validacion={"aceptaEquivalentes": True, "numeroMixto": True},
        )
