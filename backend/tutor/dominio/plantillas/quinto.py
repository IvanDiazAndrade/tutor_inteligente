"""Plantillas paramétricas de 5° básico (modelo_dominio.md §4)."""

import random
from fractions import Fraction
from math import gcd, lcm

from tutor.dominio.columnas import (
    con_bloque,
    pistas_division,
    pistas_producto_dos_cifras,
    separar_bloque,
)
from tutor.dominio.plantillas.base import (
    PALABRAS_DECIMALES,
    SIMBOLO_EN_PALABRAS,
    EjercicioGenerado,
    _errores,
    _errores_texto,
    _sin_revelar,
    decimal_cl,
    decimales,
    fijo,
    mezclados,
    miles,
    secuencia,
    simbolo,
)
from tutor.dominio.plantillas.cuarto import (
    AL_REVES,
    POSICIONES,
    _ejercicio,
    comparar_naturales,
    ordenar_naturales,
    valor_posicional,
)

# 5B-OA4: división de 3 dígitos por 1 dígito, con resto (§4.1) ---------------------------


class DivisionConResto:
    id = "5B-OA4-div-resto"
    unidad_id = "5B-OA4"
    version = 2  # v2: pistas con la división escrita

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
        pasos, _ = _pasos_division(dividendo, divisor)
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

        # La división escrita (columnas.py): la pista 3 queda a un paso del final (§4.3 del modelo
        # pedagógico), sin la última cifra del cociente ni el resto.
        estrategia, primer_paso, casi = pistas_division(dividendo, divisor)
        if pide_resto:
            frase, bloque = separar_bloque(casi)
            casi = con_bloque(f"{frase} Lo que sobra al final es el resto.", bloque)

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
                estrategia,
                _sin_revelar(
                    primer_paso,
                    respuesta,
                    "Divide las primeras cifras del dividendo por el divisor y anota lo que sobra.",
                ),
                _sin_revelar(
                    casi, respuesta, "Divide la parte que falta y fíjate en lo que sobra."
                ),
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
    version = 2  # v2: pistas con la multiplicación escrita (niveles 2 y 3)

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
            pistas = pistas_producto_dos_cifras(a, b)
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


# 5B-OA1: números naturales hasta 1.000 millones ------------------------------------------


class NumerosGrandes:
    id = "5B-OA1-numeros-grandes"
    unidad_id = "5B-OA1"
    version = 1

    def instanciar(self, nivel: int, azar: random.Random) -> EjercicioGenerado:
        # N1: valor posicional de una cifra en números de 7 a 9 cifras · N2: redondear a la
        # unidad, decena o centena de mil · N3: comparar dos números u ordenar cuatro.
        if nivel == 1:
            return valor_posicional(self, 1, azar, 1_000_000, 999_999_999, (3, 8))
        if nivel == 2:
            return self._redondear(azar)
        if azar.random() < 0.5:
            return comparar_naturales(self, 3, azar, 100_000, 999_999_999)
        return ordenar_naturales(self, 3, azar, 100_000, 999_999_999)

    def _redondear(self, azar: random.Random) -> EjercicioGenerado:
        while True:
            n = azar.randint(100_000, 999_999_999)
            p = azar.randint(3, 5)
            potencia = 10**p
            if n % potencia:  # que haya algo que redondear
                break
        singular, plural = POSICIONES[p]
        x, y = n // potencia % 10, n // (potencia // 10) % 10
        sube = y >= 5
        r = (n // potencia + (1 if sube else 0)) * potencia
        respuesta = str(r)
        truncado = n // potencia * potencia
        criterio = "5 o más" if sube else "menor que 5"
        efecto = "sube en 1" if sube else "se mantiene"
        candidatos = [
            (
                str(truncado) if sube else str(truncado + potencia),
                "redondeó hacia el lado equivocado",
                "Mira la cifra de la derecha: si es 5 o más, se sube; si es menor que 5, se "
                "mantiene.",
            ),
            (
                str(round(n / (potencia * 10)) * potencia * 10),
                "redondeó a otra posición",
                f"Fíjate en la posición pedida: las {plural}.",
            ),
            (
                str(round(n / (potencia // 10)) * (potencia // 10)),
                "redondeó a otra posición",
                f"Fíjate en la posición pedida: las {plural}.",
            ),
        ]
        return _ejercicio(
            self,
            2,
            f"Redondea {miles(n)} a la {singular} más cercana.",
            "numerico",
            respuesta,
            [
                f"La cifra de las {plural} es {x}; se mira la cifra de su derecha, que es {y}.",
                f"Como {y} es {criterio}, la cifra de las {plural} {efecto} y las cifras de "
                "la derecha pasan a ser 0.",
                f"{miles(n)} redondeado a la {singular} es {miles(r)}.",
            ],
            _errores(respuesta, candidatos),
            [
                "Para redondear, mira la cifra que está justo a la derecha de la posición pedida.",
                f"La cifra de las {plural} es {x} y la de su derecha es {y}.",
                f"Como {y} es {criterio}, la cifra de las {plural} {efecto}. Después, todo lo "
                "de la derecha se vuelve 0.",
            ],
        )


# 5B-OA7: fracciones equivalentes: amplificar, simplificar y comparar ---------------------


class FraccionesEquivalentes:
    id = "5B-OA7-equivalentes"
    unidad_id = "5B-OA7"
    version = 1

    def instanciar(self, nivel: int, azar: random.Random) -> EjercicioGenerado:
        # N1: amplificar por un número dado · N2: simplificar hasta la fracción irreducible ·
        # N3: comparar fracciones de distinto denominador (a veces son equivalentes).
        # En amplificar y simplificar la forma ES el objetivo: aceptaEquivalentes = false.
        if nivel == 1:
            return self._amplificar(azar)
        if nivel == 2:
            return self._simplificar(azar)
        return self._comparar(azar)

    @staticmethod
    def _irreducible(azar: random.Random, maximo: int) -> tuple[int, int]:
        while True:
            d = azar.randint(2, maximo)
            a = azar.randint(1, d - 1)
            if gcd(a, d) == 1:
                return a, d

    def _amplificar(self, azar: random.Random) -> EjercicioGenerado:
        a, d = self._irreducible(azar, 10)
        k = azar.randint(2, 5)
        A, D = a * k, d * k
        respuesta = f"{A}/{D}"
        mismo = "Para amplificar se multiplican el numerador y el denominador por el mismo número."
        return _ejercicio(
            self,
            1,
            f"Amplifica {a}/{d} por {k}.",
            "fraccion",
            respuesta,
            [
                f"Para amplificar por {k} se multiplican el numerador y el denominador por {k}.",
                f"{a} × {k} = {A} y {d} × {k} = {D}.",
                f"La fracción amplificada es {respuesta}.",
            ],
            _errores_texto(
                respuesta,
                [
                    (f"{A}/{d}", "amplificó solo el numerador", mismo),
                    (f"{a}/{D}", "amplificó solo el denominador", mismo),
                    (
                        f"{a + k}/{d + k}",
                        "sumó en vez de multiplicar",
                        "Amplificar es multiplicar, no sumar.",
                    ),
                    (
                        f"{a}/{d}",
                        "no amplificó la fracción",
                        "Vale lo mismo, pero se pedía escribirla amplificada.",
                    ),
                ],
            ),
            [
                "Amplificar una fracción es multiplicar su numerador y su denominador por el "
                "mismo número.",
                f"Multiplica el numerador: {a} × {k}.",
                f"El numerador queda en {A}. Ahora multiplica el denominador: {d} × {k}.",
            ],
            {"aceptaEquivalentes": False},
        )

    def _simplificar(self, azar: random.Random) -> EjercicioGenerado:
        while True:
            a, d = self._irreducible(azar, 12)
            k = azar.randint(2, 6)
            if d * k <= 60:
                break
        A, D = a * k, d * k
        respuesta = f"{a}/{d}"
        divisores = [j for j in range(2, k) if k % j == 0]
        parcial = f"{A // divisores[0]}/{D // divisores[0]}" if divisores else None
        return _ejercicio(
            self,
            2,
            f"Simplifica {A}/{D} hasta que ya no se pueda simplificar más.",
            "fraccion",
            respuesta,
            [
                f"Se busca el mayor número que divide a {A} y a {D}: es {k}.",
                f"{A} : {k} = {a} y {D} : {k} = {d}.",
                f"La fracción simplificada es {respuesta}.",
            ],
            _errores_texto(
                respuesta,
                [
                    (
                        parcial,
                        "simplificó solo una vez",
                        "Vas bien, pero todavía se puede simplificar: "
                        "busca otro número que divida a "
                        "los dos.",
                    ),
                    (
                        f"{a}/{D}",
                        "simplificó solo el numerador",
                        "Para simplificar se dividen el numerador y el denominador "
                        "por el mismo número.",
                    ),
                    (
                        f"{A}/{D}",
                        "no simplificó",
                        "Vale lo mismo, pero se pedía escribirla con números más pequeños.",
                    ),
                ],
            ),
            [
                "Simplificar es dividir el numerador y el denominador por el mismo número.",
                f"Busca un número que divida a {A} y a {D} a la vez.",
                f"El mayor número que divide a los dos es {k}.",
            ],
            {"aceptaEquivalentes": False},
        )

    def _comparar(self, azar: random.Random) -> EjercicioGenerado:
        while True:
            a, d1 = self._irreducible(azar, 12)
            if azar.random() < 0.25:
                j = azar.randint(2, 4)
                b, d2 = a * j, d1 * j  # equivalentes: 3/4 y 6/8
            else:
                b, d2 = self._irreducible(azar, 12)
            if d1 != d2 and lcm(d1, d2) <= 24 and d2 <= 24:
                break
        if azar.random() < 0.5:
            a, d1, b, d2 = b, d2, a, d1
        x, y = Fraction(a, d1), Fraction(b, d2)
        m = lcm(d1, d2)
        A, B = a * (m // d1), b * (m // d2)
        sim = simbolo(x, y)
        tx, ty = f"{a}/{d1}", f"{b}/{d2}"
        ingenuo = simbolo(Fraction(a), Fraction(b))  # mirar solo los numeradores

        def amplificada(t: str, num: int, den: int) -> str:
            return f"{t} ya tiene denominador {m}" if den == m else f"{t} se amplifica a {num}/{m}"

        escritas = f"{amplificada(tx, A, d1)} y {amplificada(ty, B, d2)}"
        retro = (
            "Con distinto denominador no basta mirar los numeradores: primero escribe las dos "
            "fracciones con el mismo denominador."
        )
        return _ejercicio(
            self,
            3,
            f"¿Qué signo va entre {tx} y {ty}?",
            "comparar",
            sim,
            [
                f"Se escriben con el mismo denominador, {m}.",
                f"{escritas[0].upper()}{escritas[1:]}.",
                f"Como {A} {SIMBOLO_EN_PALABRAS[sim]} {B}, {tx} {sim} {ty}.",
            ],
            _errores_texto(
                sim,
                [
                    (ingenuo, "comparó solo los numeradores", retro),
                    (None if sim == "=" else {"<": ">", ">": "<"}[sim], "comparó al revés", retro),
                    (
                        None if sim == "=" else "=",
                        "pensó que eran equivalentes",
                        "Escríbelas con el mismo denominador y compara los numeradores.",
                    ),
                ],
            ),
            [
                "Para comparar fracciones con distinto denominador, escríbelas con el mismo "
                "denominador.",
                f"Un denominador común de {d1} y {d2} es {m}.",
                f"{escritas[0].upper()}{escritas[1:]}. Ahora compara los numeradores.",
            ],
            {"valores": [tx, ty]},
        )


# 5B-OA10: fracciones de denominador 2, 4, 5, 10 y 100 como decimales, y al revés --------

NOMBRE_DECIMAL = {10: "décimos", 100: "centésimos"}


def _cuadricula(v: Fraction) -> dict:
    """Cuadrícula de 10 × 10 con v pintado: cada cuadrado es un centésimo (v < 1)."""
    return {"tipo": "cuadricula-decimal", "parametros": {"pintadas": int(v * 100)}}


class FraccionDecimal:
    id = "5B-OA10-fraccion-decimal"
    unidad_id = "5B-OA10"
    version = 2  # v2: cuadrícula de 100 en los niveles 1 y 2

    def instanciar(self, nivel: int, azar: random.Random) -> EjercicioGenerado:
        # N1: denominador 10 o 100 a decimal · N2: denominador 2, 4 o 5 a decimal (amplificando)
        # · N3: un decimal a fracción.
        if nivel == 1:
            return self._directa(azar)
        if nivel == 2:
            return self._amplificando(azar)
        return self._a_fraccion(azar)

    def _directa(self, azar: random.Random) -> EjercicioGenerado:
        d = azar.choice((10, 100))
        n = azar.randint(1, d - 1)
        v = Fraction(n, d)
        respuesta = decimal_cl(v)
        k = 1 if d == 10 else 2
        nombre = NOMBRE_DECIMAL[d]
        escrita = fijo(v, k)
        cifras = "una cifra" if k == 1 else "dos cifras"
        return _ejercicio(
            self,
            1,
            f"Escribe {n}/{d} como número decimal.",
            "numerico",
            respuesta,
            [
                f"{n}/{d} son {n} {nombre}.",
                f"Los {nombre} se escriben con {cifras} después de la coma: {escrita}"
                + (f", es decir, {respuesta}." if escrita != respuesta else "."),
            ],
            _errores(
                respuesta,
                [
                    c
                    for c in [
                        (
                            decimal_cl(Fraction(n, d * 10)),
                            "puso un cero de más",
                            f"Los {nombre} ocupan {cifras} después de la coma, no más.",
                        ),
                        (
                            decimal_cl(Fraction(n, d // 10)) if d == 100 else None,
                            "puso un cero de menos",
                            f"Los {nombre} ocupan {cifras} después de la coma.",
                        ),
                        (
                            f"{n},{d}",
                            "juntó numerador y denominador con una coma",
                            "La fracción no se escribe poniendo una coma entre sus números: "
                            "piensa en "
                            "cuántos décimos o centésimos son.",
                        ),
                    ]
                    if c[0]
                ],
            ),
            [
                "Un décimo se escribe con una cifra después de la coma; un centésimo, con dos.",
                f"El denominador es {d}: son {nombre}.",
                f"Son {n} {nombre}: escríbelo de modo que ocupe {cifras} después de la coma.",
            ],
            representacion=_cuadricula(v),
        )

    def _amplificando(self, azar: random.Random) -> EjercicioGenerado:
        while True:
            d = azar.choice((2, 4, 5))
            n = azar.randint(1, d - 1)
            if gcd(n, d) == 1:
                break
        D = 100 if d == 4 else 10
        k = D // d
        N = n * k
        v = Fraction(n, d)
        respuesta = decimal_cl(v)
        nombre = NOMBRE_DECIMAL[D]
        return _ejercicio(
            self,
            2,
            f"Escribe {n}/{d} como número decimal.",
            "numerico",
            respuesta,
            [
                f"Se amplifica por {k} para que el denominador sea {D}: {n}/{d} = {N}/{D}.",
                f"{N}/{D} son {N} {nombre}: {respuesta}.",
            ],
            _errores(
                respuesta,
                [
                    (
                        f"0,{n}{d}",
                        "juntó numerador y denominador",
                        "Primero amplifica para que el denominador sea 10 o 100.",
                    ),
                    (
                        f"{n},{d}",
                        "juntó numerador y denominador con una coma",
                        "Primero amplifica para que el denominador sea 10 o 100.",
                    ),
                    (
                        decimal_cl(Fraction(n, 10)),
                        "escribió el numerador después de la coma",
                        "El numerador solo no basta: primero amplifica para que el "
                        "denominador sea 10 "
                        "o 100.",
                    ),
                ],
            ),
            [
                "Amplifica la fracción para que el denominador sea 10 o 100.",
                f"Multiplica el numerador y el denominador por {k}.",
                f"Al amplificar quedan {N} {nombre}. Ahora escríbelo con coma.",
            ],
            representacion=_cuadricula(v),
        )

    def _a_fraccion(self, azar: random.Random) -> EjercicioGenerado:
        while True:
            d = azar.choice((2, 4, 5, 10, 100))
            n = azar.randint(1, d - 1)
            v = Fraction(n, d)
            if v.denominator == d:
                break
        k = decimales(v)
        D = 10**k
        N = int(v * D)
        respuesta = f"{v.numerator}/{v.denominator}"
        nombre = NOMBRE_DECIMAL[D]
        texto = decimal_cl(v)
        return _ejercicio(
            self,
            3,
            f"Escribe {texto} como fracción.",
            "fraccion",
            respuesta,
            [
                f"{texto} son {N} {nombre}: {N}/{D}.",
                f"Se simplifica: {N}/{D} = {respuesta}."
                if D != v.denominator
                else f"La fracción es {respuesta}.",
            ],
            _errores(
                respuesta,
                [
                    c
                    for c in [
                        (
                            f"{N}/{D * 10}",
                            "puso un cero de más en el denominador",
                            f"Con {'una cifra' if k == 1 else 'dos cifras'} después de la coma, el "
                            f"denominador es {D}.",
                        ),
                        (
                            f"{N}/{D // 10}" if k == 2 else None,
                            "puso un cero de menos en el denominador",
                            f"Con dos cifras después de la coma, el denominador es {D}.",
                        ),
                        (
                            f"{D}/{N}",
                            "invirtió la fracción",
                            "El número que va después de la coma es el numerador, arriba.",
                        ),
                    ]
                    if c[0]
                ],
            ),
            [
                "Un decimal con una cifra después de la coma son décimos; con dos, centésimos.",
                f"Fíjate cuántas cifras hay después de la coma: son {nombre}.",
                f"Son {N} {nombre}: escribe la fracción con numerador {N} y denominador {D}, "
                "y simplifícala si se puede.",
            ],
        )


# 5B-OA11: comparar y ordenar decimales hasta la milésima ---------------------------------


def _ingenuo(v: Fraction) -> tuple[int, int]:
    """Cómo compara un niño que lee las cifras decimales como un número natural: 0,45 > 0,5."""
    entero = int(v)
    k = decimales(v)
    return entero, int((v - entero) * 10**k)


class CompararDecimales:
    id = "5B-OA11-comparar-decimales"
    unidad_id = "5B-OA11"
    version = 1

    def instanciar(self, nivel: int, azar: random.Random) -> EjercicioGenerado:
        # N1: comparar dos decimales con la misma cantidad de decimales · N2: comparar con
        # distinta cantidad de decimales, donde más cifras no es mayor (0,5 y 0,45) ·
        # N3: ordenar cuatro decimales de hasta tres decimales.
        if nivel == 3:
            return self._ordenar(azar)
        while True:
            entero = azar.randint(0, 9)
            if nivel == 1:
                k1 = k2 = azar.randint(1, 2)
            else:
                k1, k2 = azar.sample((1, 2, 3), 2)
            x = entero + _decimal_al_azar(azar, k1, 0)
            y = entero + _decimal_al_azar(azar, k2, 0)
            if x == y:
                continue
            # N2 es para la trampa clásica: leer las cifras decimales como un número natural
            # (0,45 > 0,5) da el resultado equivocado.
            trampa = simbolo(Fraction(_ingenuo(x)[1]), Fraction(_ingenuo(y)[1])) != simbolo(x, y)
            if nivel == 1 or trampa:
                break
        return self._comparar(x, y)

    def _comparar(self, x: Fraction, y: Fraction) -> EjercicioGenerado:
        sim = simbolo(x, y)
        tx, ty = decimal_cl(x), decimal_cl(y)
        k = max(decimales(x), decimales(y))
        X, Y = int(x * 10**k), int(y * 10**k)
        ingenuo = simbolo(Fraction(_ingenuo(x)[1]), Fraction(_ingenuo(y)[1]))
        palabras = PALABRAS_DECIMALES[k]
        retro = (
            "Que un decimal tenga más cifras no lo hace mayor: completa con ceros para que los "
            "dos tengan la misma cantidad de decimales y compara."
        )
        return _ejercicio(
            self,
            2 if decimales(x) != decimales(y) else 1,
            f"¿Qué signo va entre {tx} y {ty}?",
            "comparar",
            sim,
            [
                f"Se completan con ceros para que los dos tengan {palabras}: {fijo(x, k)} y "
                f"{fijo(y, k)}.",
                f"Como {X} {SIMBOLO_EN_PALABRAS[sim]} {Y}, {tx} {sim} {ty}.",
            ],
            _errores_texto(
                sim,
                [
                    (
                        ingenuo if ingenuo != sim else None,
                        "pensó que el decimal con más cifras es mayor",
                        retro,
                    ),
                    (
                        {"<": ">", ">": "<"}[sim],
                        "comparó al revés",
                        "Compara cifra por cifra desde la coma: décimos con décimos, "
                        "centésimos con "
                        "centésimos.",
                    ),
                    (
                        "=",
                        "pensó que valían lo mismo",
                        "Revisa con cuidado: los dos números no valen lo mismo.",
                    ),
                ],
            ),
            [
                "Para comparar decimales, mira primero la parte entera y después las cifras "
                "decimales, una por una desde la coma.",
                f"Completa con ceros para que los dos tengan {palabras}: {fijo(x, k)} y "
                f"{fijo(y, k)}.",
                f"Ahora compara {X} y {Y}, como si no hubiera coma.",
            ],
            {"valores": [tx, ty]},
        )

    def _ordenar(self, azar: random.Random) -> EjercicioGenerado:
        entero = azar.randint(0, 5)
        valores: set[Fraction] = set()
        while len(valores) < 4:
            valores.add(entero + _decimal_al_azar(azar, azar.randint(1, 3), 0))
        creciente = azar.random() < 0.5
        orden = sorted(valores, reverse=not creciente)
        lista = [decimal_cl(v) for v in orden]
        respuesta = secuencia(lista)
        por_cifras = secuencia(
            [decimal_cl(v) for v in sorted(valores, key=_ingenuo, reverse=not creciente)]
        )
        extremo = "menor" if creciente else "mayor"
        mostrados = mezclados(lista, azar)
        con_ceros = " · ".join(fijo(Fraction(t.replace(",", ".")), 3) for t in mostrados)
        return _ejercicio(
            self,
            3,
            f"Ordena los números de {'menor a mayor' if creciente else 'mayor a menor'}.",
            "ordenar",
            respuesta,
            [
                "Se completan con ceros para que todos tengan tres decimales y se comparan "
                "como números naturales.",
                f"El orden es: {respuesta}.",
            ],
            _errores_texto(
                respuesta,
                [
                    (
                        por_cifras,
                        "pensó que el decimal con más cifras es mayor",
                        "Que un decimal tenga más cifras no lo hace mayor: completa con ceros para "
                        "que todos tengan la misma cantidad de decimales.",
                    ),
                    (secuencia(lista[::-1]), "ordenó al revés", AL_REVES),
                ],
            ),
            [
                "Para ordenar decimales, completa con ceros para que todos tengan la misma "
                "cantidad de decimales.",
                f"Con tres decimales quedan: {con_ceros}. Compáralos como si no hubiera coma.",
                f"El {extremo} es {lista[0]}. Ahora busca el que sigue.",
            ],
            {"valores": mostrados},
        )
