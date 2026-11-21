"""Plantillas paramétricas de 5° básico (modelo_dominio.md §4)."""

import random
from fractions import Fraction
from math import gcd, lcm

from tutor.dominio.plantillas.base import (
    PALABRAS_DECIMALES,
    EjercicioGenerado,
    _errores,
    _sin_revelar,
    decimal_cl,
    fijo,
    miles,
)

# 5B-OA4: división de 3 dígitos por 1 dígito, con resto (§4.1) ---------------------------


class DivisionConResto:
    id = "5B-OA4-div-resto"
    unidad_id = "5B-OA4"
    version = 1

    def instanciar(self, nivel: int, azar: random.Random) -> EjercicioGenerado:
        # N1: resto 0 y divisor 2-5 · N2: resto > 0 · N3: resto > 0 y se pregunta cociente o resto.
        divisor = azar.randint(2, 5) if nivel == 1 else azar.randint(2, 9)
        resto = 0 if nivel == 1 else azar.randint(1, divisor - 1)
        # El dividendo se construye desde el cociente y el resto (correcto por construcción).
        cociente = azar.randint(-(-(100 - resto) // divisor), (999 - resto) // divisor)
        dividendo = cociente * divisor + resto
        pide_resto = nivel == 3 and azar.random() < 0.5

        pregunta = "¿Cuál es el resto?" if pide_resto else "¿Cuál es el cociente?"
        respuesta = str(resto if pide_resto else cociente)
        pasos, ultimo_parcial = _pasos_division(dividendo, divisor)
        solucion = [*pasos, f"El cociente es {cociente} y el resto es {resto}."]

        if pide_resto:
            errores = _errores(
                respuesta,
                [
                    (
                        str(cociente),
                        "confundió cociente con resto",
                        "Ese número es cuántas veces cabe el divisor. "
                        "La pregunta pide lo que sobra.",
                    ),
                    (
                        "0",
                        "pensó que la división era exacta",
                        "Revisa el último paso: después de repartir, ¿sobró algo?",
                    ),
                ],
            )
            pista_final = _sin_revelar(
                f"El cociente es {cociente}. Multiplica {cociente} × {divisor} "
                "y réstalo al dividendo.",
                respuesta,
                "Multiplica el cociente por el divisor y réstalo al dividendo.",
            )
        else:
            errores = _errores(
                respuesta,
                [
                    (
                        str(cociente + 1),
                        "siguió dividiendo de más",
                        "Revisa el último paso: el resto tiene que ser menor que el divisor.",
                    ),
                    (
                        str(resto),
                        "confundió cociente con resto",
                        "Ese número es lo que sobra. "
                        "La pregunta pide cuántas veces cabe el divisor.",
                    ),
                ],
            )
            # A un paso del final (§4.3 del modelo pedagógico): todas las cifras menos la última.
            pista_final = _sin_revelar(
                f"El cociente empieza con {str(cociente)[:-1]}. "
                f"Ahora divide {ultimo_parcial} : {divisor}.",
                respuesta,
                "Ya tienes casi todo el cociente: te falta dividir la última parte.",
            )

        return EjercicioGenerado(
            unidad_id=self.unidad_id,
            plantilla_id=self.id,
            nivel=nivel,
            enunciado=f"Calcula {dividendo} : {divisor}. {pregunta}",
            formato_respuesta="numerico",
            respuesta_final=respuesta,
            solucion_referencia=solucion,
            errores_comunes=errores,
            pistas=[
                "Dividir es repartir en partes iguales. "
                "Empieza por las primeras cifras del dividendo.",
                _sin_revelar(
                    pasos[0],
                    respuesta,
                    "Divide las primeras cifras del dividendo por el divisor y anota lo que sobra.",
                ),
                pista_final,
            ],
        )


def _pasos_division(dividendo: int, divisor: int) -> tuple[list[str], int]:
    """Pasos del algoritmo de la división, cifra por cifra, en lenguaje de 5° básico.
    Devuelve también el último número que se divide (para la pista 3)."""
    cifras = str(dividendo)
    pasos: list[str] = []
    parcial = 0
    ultimo = 0
    empezo = False
    for i, cifra in enumerate(cifras):
        parcial = parcial * 10 + int(cifra)
        if not empezo and parcial < divisor and i < len(cifras) - 1:
            continue
        cabe = parcial // divisor
        ultimo = parcial
        sobra = parcial - cabe * divisor
        prefijo = "Se baja el " + cifra + f" y queda {parcial}. " if empezo else ""
        pasos.append(
            f"{prefijo}{parcial} : {divisor} = {cabe}, porque {cabe} × {divisor} = "
            f"{cabe * divisor}. Sobra {sobra}."
        )
        parcial = sobra
        empezo = True
    return pasos, ultimo


# 5B-OA3: multiplicación de 2 cifras por 2 cifras -----------------------------------------


class Multiplicacion2x2:
    id = "5B-OA3-mult-2x2"
    unidad_id = "5B-OA3"
    version = 1

    def instanciar(self, nivel: int, azar: random.Random) -> EjercicioGenerado:
        # N1: el segundo factor es una decena exacta (34 × 20) · N2: factores de 11 a 49 ·
        # N3: factores mayores (51-99 por 21-99). Ningún factor termina en 0 salvo en N1.
        while True:
            if nivel == 1:
                a, b = azar.randint(11, 99), azar.randint(2, 9) * 10
            elif nivel == 2:
                a, b = azar.randint(11, 49), azar.randint(11, 49)
            else:
                a, b = azar.randint(51, 99), azar.randint(21, 99)
            if a % 10 and (nivel == 1 or b % 10):
                break
        producto = a * b
        respuesta = str(producto)
        sumo = (
            str(a + b),
            "sumó en vez de multiplicar",
            "Fíjate en el signo: es una multiplicación, no una suma.",
        )
        if nivel == 1:
            cifra = b // 10
            parcial = a * cifra
            solucion = [
                f"Multiplicar por {b} es multiplicar por {cifra} y agregar un cero.",
                f"{a} × {cifra} = {miles(parcial)}.",
                f"Se agrega el cero: {a} × {b} = {miles(producto)}.",
            ]
            pistas = [
                "Multiplicar por una decena exacta es multiplicar por su primera cifra "
                "y agregar un cero al final.",
                f"Primero calcula {a} × {cifra}.",
                f"{a} × {cifra} = {miles(parcial)}. Ahora agrégale un cero.",
            ]
            errores = [
                (
                    str(parcial),
                    "olvidó agregar el cero",
                    "Multiplicaste por la cifra de las decenas, pero falta el cero del final.",
                ),
                sumo,
            ]
        else:
            decenas, unidades = b // 10 * 10, b % 10
            p1, p2 = a * decenas, a * unidades
            solucion = [
                f"Se descompone {b} en {decenas} + {unidades}.",
                f"{a} × {decenas} = {miles(p1)}.",
                f"{a} × {unidades} = {miles(p2)}.",
                f"Se suman los productos: {miles(p1)} + {miles(p2)} = {miles(producto)}.",
            ]
            pistas = [
                "Descompón el segundo factor en decenas y unidades, y multiplica el primero "
                "por cada parte.",
                f"Descompón {b} en {decenas} + {unidades}.",
                f"{a} × {decenas} = {miles(p1)} y {a} × {unidades} = {miles(p2)}. Ahora súmalos.",
            ]
            errores = [
                (
                    str(p1 // 10 + p2),
                    "olvidó el cero del producto por las decenas",
                    "El producto por las decenas termina en cero: revisa cómo lo escribiste "
                    "antes de sumar.",
                ),
                (
                    str((a // 10) * (b // 10) * 100 + (a % 10) * (b % 10)),
                    "multiplicó solo las cifras de la misma posición",
                    "Cada cifra de un factor se multiplica por todo el otro factor, "
                    "no solo por la cifra de su misma posición.",
                ),
                sumo,
            ]
        return EjercicioGenerado(
            unidad_id=self.unidad_id,
            plantilla_id=self.id,
            nivel=nivel,
            enunciado=f"Calcula {a} × {b}.",
            formato_respuesta="numerico",
            respuesta_final=respuesta,
            solucion_referencia=solucion,
            errores_comunes=_errores(respuesta, errores),
            pistas=[_sin_revelar(p, respuesta, "Ya casi: haz el último cálculo.") for p in pistas],
        )


# 5B-OA5: operatoria combinada con paréntesis y prioridad -----------------------------------

PRIORIDAD = (
    "Recuerda el orden: primero las multiplicaciones y divisiones, después las sumas y restas."
)
PARENTESIS = "Lo que está entre paréntesis se calcula primero."


class OperatoriaCombinada:
    id = "5B-OA5-combinada"
    unidad_id = "5B-OA5"
    version = 1
    # N1: suma o resta con una multiplicación (prioridad) · N2: paréntesis, o tres
    # operaciones · N3: con división exacta (prioridad o paréntesis). Resultado entero > 0.
    FORMAS = {
        1: ("a+bxc", "axb-c", "a-bxc"),
        2: ("(a+b)xc", "ax(b-c)", "a+bxc-d"),
        3: ("a+b:c", "(a-b):c", "axb-c:d"),
    }

    def instanciar(self, nivel: int, azar: random.Random) -> EjercicioGenerado:
        while True:
            armado = _armar_combinada(azar.choice(self.FORMAS[nivel]), azar)
            if armado is not None:
                break
        expresion, pasos, ultima, resultado, candidatos = armado
        respuesta = str(resultado)
        return EjercicioGenerado(
            unidad_id=self.unidad_id,
            plantilla_id=self.id,
            nivel=nivel,
            enunciado=f"Calcula {expresion}.",
            formato_respuesta="numerico",
            respuesta_final=respuesta,
            solucion_referencia=pasos,
            errores_comunes=_errores(
                respuesta,
                [(str(v), causa, retro) for v, causa, retro in candidatos if v and v > 0],
            ),
            pistas=[
                "Primero se resuelve lo que está entre paréntesis; después, multiplicaciones "
                "y divisiones; al final, sumas y restas.",
                _sin_revelar(pasos[0], respuesta, "Empieza por la operación que va primero."),
                _sin_revelar(
                    f"Ya casi: te queda calcular {ultima}.",
                    respuesta,
                    "Ya casi: haz la última operación.",
                ),
            ],
        )


def _armar_combinada(forma: str, azar: random.Random):
    """Devuelve (expresión, pasos, última operación, resultado, errores) o None si los
    parámetros sorteados no sirven."""
    n = azar.randint
    if forma == "a+bxc":
        a, b, c = n(2, 60), n(2, 9), n(2, 9)
        p = b * c
        r = a + p
        return (
            f"{a} + {b} × {c}",
            [f"Primero se multiplica: {b} × {c} = {p}.", f"Luego se suma: {a} + {p} = {r}."],
            f"{a} + {p}",
            r,
            [((a + b) * c, "sumó antes de multiplicar", PRIORIDAD)],
        )
    if forma == "axb-c":
        a, b = n(2, 9), n(2, 9)
        p = a * b
        c = n(1, p - 1)
        r = p - c
        return (
            f"{a} × {b} − {c}",
            [f"Primero se multiplica: {a} × {b} = {p}.", f"Luego se resta: {p} − {c} = {r}."],
            f"{p} − {c}",
            r,
            [(a * (b - c), "restó antes de multiplicar", PRIORIDAD)],
        )
    if forma == "a-bxc":
        b, c = n(2, 9), n(2, 9)
        p = b * c
        a = n(p + 1, p + 60)
        r = a - p
        return (
            f"{a} − {b} × {c}",
            [f"Primero se multiplica: {b} × {c} = {p}.", f"Luego se resta: {a} − {p} = {r}."],
            f"{a} − {p}",
            r,
            [((a - b) * c, "restó antes de multiplicar", PRIORIDAD)],
        )
    if forma == "(a+b)xc":
        a, b, c = n(2, 30), n(2, 30), n(2, 9)
        s = a + b
        r = s * c
        return (
            f"({a} + {b}) × {c}",
            [f"Primero el paréntesis: {a} + {b} = {s}.", f"Luego se multiplica: {s} × {c} = {r}."],
            f"{s} × {c}",
            r,
            [(a + b * c, "no resolvió primero el paréntesis", PARENTESIS)],
        )
    if forma == "ax(b-c)":
        a, b = n(2, 9), n(5, 40)
        c = n(1, b - 1)
        s = b - c
        r = a * s
        return (
            f"{a} × ({b} − {c})",
            [f"Primero el paréntesis: {b} − {c} = {s}.", f"Luego se multiplica: {a} × {s} = {r}."],
            f"{a} × {s}",
            r,
            [(a * b - c, "no resolvió primero el paréntesis", PARENTESIS)],
        )
    if forma == "a+bxc-d":
        a, b, c = n(2, 40), n(2, 9), n(2, 9)
        p = b * c
        s = a + p
        d = n(1, s - 1)
        r = s - d
        return (
            f"{a} + {b} × {c} − {d}",
            [
                f"Primero se multiplica: {b} × {c} = {p}.",
                f"Luego, de izquierda a derecha: {a} + {p} = {s}.",
                f"Por último: {s} − {d} = {r}.",
            ],
            f"{s} − {d}",
            r,
            [((a + b) * c - d, "sumó antes de multiplicar", PRIORIDAD)],
        )
    if forma == "a+b:c":
        c, q, a = n(2, 9), n(2, 12), n(2, 60)
        b = c * q
        r = a + q
        suma = a + b
        return (
            f"{a} + {b} : {c}",
            [f"Primero se divide: {b} : {c} = {q}.", f"Luego se suma: {a} + {q} = {r}."],
            f"{a} + {q}",
            r,
            [(suma // c if suma % c == 0 else None, "sumó antes de dividir", PRIORIDAD)],
        )
    if forma == "(a-b):c":
        c, q, b = n(2, 9), n(2, 15), n(1, 40)
        s = c * q
        a = s + b
        sin_parentesis = a - b // c if b % c == 0 else None
        return (
            f"({a} − {b}) : {c}",
            [f"Primero el paréntesis: {a} − {b} = {s}.", f"Luego se divide: {s} : {c} = {q}."],
            f"{s} : {c}",
            q,
            [(sin_parentesis, "no resolvió primero el paréntesis", PARENTESIS)],
        )
    # "axb-c:d"
    a, b, d, q = n(2, 9), n(2, 9), n(2, 9), n(2, 9)
    p, c = a * b, d * q
    if p <= q:
        return None
    r = p - q
    resta = p - c
    return (
        f"{a} × {b} − {c} : {d}",
        [
            f"Primero la multiplicación y la división: {a} × {b} = {p} y {c} : {d} = {q}.",
            f"Luego se resta: {p} − {q} = {r}.",
        ],
        f"{p} − {q}",
        r,
        [
            (
                resta // d if resta > 0 and resta % d == 0 else None,
                "restó antes de dividir",
                PRIORIDAD,
            )
        ],
    )


# 5B-OA9: suma y resta de fracciones con distinto denominador (hasta 12) -----------------


def _texto(f: Fraction) -> str:
    return f"{f.numerator}/{f.denominator}"


class FraccionesDistintoDenominador:
    id = "5B-OA9-distinto-den"
    unidad_id = "5B-OA9"
    version = 1

    def instanciar(self, nivel: int, azar: random.Random) -> EjercicioGenerado:
        # N1: suma; un denominador es múltiplo del otro (1/2 + 1/4) · N2: suma con
        # denominadores que no son múltiplos (1/3 + 1/4) · N3: resta. Fracciones propias e
        # irreducibles, denominador común hasta 24; en la suma el resultado es menor que 1.
        resta = nivel == 3
        while True:
            d1, d2 = azar.randint(2, 12), azar.randint(2, 12)
            if d1 == d2:
                continue
            m = lcm(d1, d2)
            multiplo = m == max(d1, d2)
            if m > 24 or (nivel == 1 and not multiplo) or (nivel == 2 and multiplo):
                continue
            a, b = azar.randint(1, d1 - 1), azar.randint(1, d2 - 1)
            if gcd(a, d1) != 1 or gcd(b, d2) != 1:
                continue
            fa, fb = Fraction(a, d1), Fraction(b, d2)
            if resta and fa < fb:
                a, d1, b, d2, fa, fb = b, d2, a, d1, fb, fa
            r = fa - fb if resta else fa + fb
            # El resultado no puede valer lo mismo que una fracción que aparece en las pistas.
            if 0 < r < 1 and r not in (fa, fb):
                break
        A, B = a * (m // d1), b * (m // d2)
        S = A - B if resta else A + B
        respuesta = _texto(r)
        signo = "−" if resta else "+"
        amplificadas = [f"{x}/{dx} = {X}/{m}" for x, dx, X in ((a, d1, A), (b, d2, B)) if dx != m]
        solucion = [
            f"Los denominadores son distintos ({d1} y {d2}): se busca un denominador común. "
            f"El mínimo común múltiplo es {m}.",
            "Se amplifica: " + " y ".join(amplificadas) + ".",
            f"Se {'restan' if resta else 'suman'} los numeradores: {A} {signo} {B} = {S}, "
            f"y queda {S}/{m}.",
            (
                f"Se simplifica: {S}/{m} = {respuesta}."
                if r.denominator != m
                else f"El resultado es {respuesta}."
            ),
        ]
        if resta:
            candidatos = [
                (
                    f"{a - b}/{d1 - d2}" if a > b and d1 > d2 else None,
                    "restó numeradores y denominadores",
                    "Antes de restar, las fracciones tienen que tener el mismo denominador; "
                    "los denominadores no se restan.",
                ),
                (
                    f"{a - b}/{m}" if a > b else None,
                    "no amplificó los numeradores",
                    "Al cambiar el denominador también hay que amplificar el numerador.",
                ),
                (
                    _texto(fa + fb),
                    "sumó en vez de restar",
                    "Fíjate en el signo: aquí hay que restar.",
                ),
            ]
        else:
            candidatos = [
                (
                    f"{a + b}/{d1 + d2}",
                    "sumó numeradores y denominadores",
                    "Antes de sumar, las fracciones tienen que tener el mismo denominador; "
                    "los denominadores no se suman.",
                ),
                (
                    f"{a + b}/{m}",
                    "no amplificó los numeradores",
                    "Al cambiar el denominador también hay que amplificar el numerador.",
                ),
            ]
        return EjercicioGenerado(
            unidad_id=self.unidad_id,
            plantilla_id=self.id,
            nivel=nivel,
            enunciado=f"Calcula {a}/{d1} {signo} {b}/{d2}.",
            formato_respuesta="fraccion",
            respuesta_final=respuesta,
            solucion_referencia=solucion,
            errores_comunes=_errores(respuesta, [c for c in candidatos if c[0]]),
            pistas=[
                f"Para {'restar' if resta else 'sumar'} fracciones con distinto denominador, "
                "primero hay que escribirlas con el mismo denominador.",
                f"Busca un múltiplo común de {d1} y {d2}. El menor es {m}.",
                f"Con denominador {m} queda {A}/{m} {signo} {B}/{m}. "
                f"Ahora {'resta' if resta else 'suma'} los numeradores.",
            ],
        )


# 5B-OA12: suma y resta de decimales hasta la milésima -----------------------------------


def _decimal_al_azar(azar: random.Random, k: int, maximo: int) -> Fraction:
    """Un decimal con exactamente k decimales (la última cifra no es 0) y parte entera ≤ maximo."""
    while True:
        n = azar.randint(1, (maximo + 1) * 10**k - 1)
        if n % 10:
            return Fraction(n, 10**k)


class SumaRestaDecimales:
    id = "5B-OA12-decimales"
    unidad_id = "5B-OA12"
    version = 1

    def instanciar(self, nivel: int, azar: random.Random) -> EjercicioGenerado:
        # N1: décimos, los dos números con un decimal · N2: hasta centésimos, con distinta
        # cantidad de decimales · N3: hasta milésimos, con distinta cantidad de decimales.
        while True:
            if nivel == 1:
                k1 = k2 = 1
            else:
                tope = 2 if nivel == 2 else 3
                k1, k2 = azar.randint(1, tope), azar.randint(1, tope)
                if k1 == k2 or max(k1, k2) != tope:
                    continue
            x = _decimal_al_azar(azar, k1, 49 if nivel == 1 else 29)
            y = _decimal_al_azar(azar, k2, 49 if nivel == 1 else 29)
            resta = azar.random() < 0.5
            if resta and x < y:
                x, y, k1, k2 = y, x, k2, k1
            r = x - y if resta else x + y
            if r > 0 and r not in (x, y):
                break
        k = max(k1, k2)
        X, Y, R = int(x * 10**k), int(y * 10**k), int(r * 10**k)
        respuesta = decimal_cl(r)
        signo = "−" if resta else "+"
        palabras = PALABRAS_DECIMALES[k]
        if k1 == k2:
            igualar = f"Los dos números tienen {palabras}: las comas quedan alineadas."
            pista_2 = f"Calcula {X} {signo} {Y} como si no hubiera coma."
        else:
            igualar = (
                f"Se completan con ceros para que los dos tengan {palabras}: "
                f"{fijo(x, k)} {signo} {fijo(y, k)}."
            )
            pista_2 = (
                "Completa con ceros para que tengan la misma cantidad de decimales: "
                f"{fijo(x, k)} y {fijo(y, k)}."
            )
        final = fijo(r, k)
        ultimo = f"Se pone la coma dejando {palabras}: {final}"
        ultimo += f", es decir, {respuesta}." if final != respuesta else "."
        solucion = [
            igualar,
            f"Se {'resta' if resta else 'suma'} como con números naturales: {X} {signo} {Y} = {R}.",
            ultimo,
        ]

        otra = x + y if resta else x - y
        candidatos = [
            (
                decimal_cl(r / 10),
                "corrió la coma",
                "Revisa dónde va la coma: el resultado tiene tantos decimales como el número "
                "que tiene más.",
            )
        ]
        if otra > 0:
            candidatos.append(
                (
                    decimal_cl(otra),
                    "sumó en vez de restar" if resta else "restó en vez de sumar",
                    f"Fíjate en el signo: aquí hay que {'restar' if resta else 'sumar'}.",
                )
            )
        if k1 != k2:
            # Error clásico: alinear las cifras por la derecha en vez de alinear las comas.
            e1, e2 = int(x), int(y)
            f1, f2 = int((x - e1) * 10**k1), int((y - e2) * 10**k2)
            if resta:
                mal = e1 - e2 + Fraction(f1 - f2, 10**k)
            else:
                mal = e1 + e2 + Fraction(f1 + f2, 10**k)
            if mal > 0:
                candidatos.append(
                    (
                        decimal_cl(mal),
                        "alineó las cifras por la derecha y no por la coma",
                        "Las comas tienen que quedar una debajo de la otra: completa con ceros "
                        "para que los dos números tengan la misma cantidad de decimales.",
                    )
                )
        return EjercicioGenerado(
            unidad_id=self.unidad_id,
            plantilla_id=self.id,
            nivel=nivel,
            enunciado=f"Calcula {decimal_cl(x)} {signo} {decimal_cl(y)}.",
            formato_respuesta="numerico",
            respuesta_final=respuesta,
            solucion_referencia=solucion,
            errores_comunes=_errores(respuesta, candidatos),
            pistas=[
                "Escribe los números uno debajo del otro, con las comas alineadas.",
                _sin_revelar(pista_2, respuesta, "Iguala la cantidad de decimales con ceros."),
                _sin_revelar(
                    f"{X} {signo} {Y} = {R}. Ahora pon la coma dejando {palabras}.",
                    respuesta,
                    f"Calcula como si no hubiera coma y deja {palabras}.",
                ),
            ],
        )
