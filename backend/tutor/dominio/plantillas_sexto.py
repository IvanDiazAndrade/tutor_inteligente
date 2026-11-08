"""Plantillas paramétricas de 6° básico (modelo_dominio.md §4)."""

import random
from fractions import Fraction
from math import gcd, lcm

from tutor.dominio.plantillas_base import EjercicioGenerado, Ficha, decimal, miles, mixto, recta


def _propia(azar: random.Random, denominadores: list[int]) -> tuple[int, int]:
    while True:
        d = azar.choice(denominadores)
        a = azar.randint(1, d - 1)
        if gcd(a, d) == 1:
            return a, d


def _decimales(valor: Fraction) -> int:
    texto = decimal(valor)
    return len(texto.split(",")[1]) if "," in texto else 0


class ImpropiasMixtos(Ficha):
    id = "6B-OA5-impropias-mixtos"
    unidad_id = "6B-OA5"

    def instanciar(self, nivel: int, azar: random.Random) -> EjercicioGenerado:
        # N1: mixto a impropia · N2: impropia a mixto · N3: ubicar en la recta.
        # La forma es el objetivo: aceptaEquivalentes = false.
        if nivel == 3:
            return self._en_recta(azar)
        a, d = _propia(azar, [2, 3, 4, 5, 6, 7, 8, 9, 10, 12])
        e = azar.randint(1, 9)
        return self._a_impropia(e, a, d) if nivel == 1 else self._a_mixto(e, a, d)

    def _a_impropia(self, e: int, a: int, d: int) -> EjercicioGenerado:
        n = e * d + a
        respuesta = f"{n}/{d}"
        return self._crear(
            1,
            f"Escribe {e} {a}/{d} como fracción impropia.",
            "fraccion",
            respuesta,
            [
                f"El entero se multiplica por el denominador: {e} × {d} = {e * d}.",
                f"Se suma el numerador: {e * d} + {a} = {n}.",
                f"El denominador no cambia: el resultado es {respuesta}.",
            ],
            [
                (
                    f"{e + a}/{d}",
                    "sumó el entero al numerador",
                    "Primero multiplica el entero por el denominador.",
                ),
                (
                    f"{e * d}/{d}",
                    "olvidó sumar el numerador",
                    "Te falta sumar las partes de la fracción.",
                ),
            ],
            [
                "Piensa cuántas partes tiene cada entero.",
                f"Multiplica {e} × {d}.",
                f"Súmale {a} y deja el mismo denominador.",
            ],
            equivalentes=False,
        )

    def _a_mixto(self, e: int, a: int, d: int) -> EjercicioGenerado:
        n = e * d + a
        respuesta = f"{e} {a}/{d}"
        return self._crear(
            2,
            f"Escribe {n}/{d} como número mixto.",
            "fraccion",
            respuesta,
            [
                f"Se divide {n} : {d}: el cociente es {e} y el resto es {a}.",
                "El cociente es el entero y el resto es el numerador.",
                f"El resultado es {respuesta}.",
            ],
            [
                (
                    f"{a} {e}/{d}",
                    "cambió el cociente por el resto",
                    "El cociente es el entero y el resto va arriba.",
                ),
                (
                    f"{e} {a}/{n}",
                    "usó un denominador equivocado",
                    "El denominador se mantiene igual.",
                ),
            ],
            [
                "Un número mixto tiene una parte entera y una fracción.",
                f"Divide {n} : {d}.",
                f"El cociente es el entero. Lo que sobra va sobre {d}.",
            ],
            equivalentes=False,
            entrada_mixta=True,
        )

    def _en_recta(self, azar: random.Random) -> EjercicioGenerado:
        maximo, d = azar.randint(2, 4), azar.choice([2, 3, 4, 5, 6])
        while True:
            n = azar.randint(d + 1, maximo * d - 1)
            if n % d:
                break
        respuesta = f"{n}/{d}"
        return self._crear(
            3,
            f"Una recta va de 0 a {maximo} y cada entero está dividido en {d} partes iguales. "
            "¿Qué fracción impropia marca el punto?",
            "fraccion",
            respuesta,
            [
                f"Cada entero tiene {d} tramos: el denominador es {d}.",
                f"Desde el 0 hasta el punto hay {n} tramos.",
                f"El punto marca {respuesta}.",
            ],
            [
                (
                    f"{n % d}/{d}",
                    "contó solo desde el último entero",
                    "Cuenta todos los tramos, partiendo desde el 0.",
                ),
                (
                    f"{n}/{d + 1}",
                    "contó las marcas en vez de los tramos",
                    "Cuenta los espacios entre las marcas de un entero, no las marcas.",
                ),
            ],
            [
                "Cuenta cuántos tramos iguales hay en cada entero.",
                f"Ese número es el denominador: {d}.",
                "Ahora cuenta todos los tramos desde 0 hasta el punto.",
            ],
            equivalentes=False,
            representacion=recta(maximo, maximo * d, n),
        )


class OperatoriaMixtos(Ficha):
    id = "6B-OA6-operatoria"
    unidad_id = "6B-OA6"
    PARES = [(2, 3), (3, 4), (4, 6), (2, 5), (3, 5), (4, 5), (6, 8), (5, 10), (10, 15), (8, 12)]

    def instanciar(self, nivel: int, azar: random.Random) -> EjercicioGenerado:
        # N1: propias · N2: impropias · N3: números mixtos.
        while True:
            b, d = azar.choice(self.PARES)
            if azar.random() < 0.5:
                b, d = d, b
            comun = lcm(b, d)
            if nivel == 3:
                return self._mixtos(azar, b, d)
            if nivel == 1:
                a, c = azar.randint(1, b - 1), azar.randint(1, d - 1)
            else:
                a, c = azar.randint(b + 1, 3 * b), azar.randint(d + 1, 3 * d)
            if gcd(a, b) != 1 or gcd(c, d) != 1:
                continue
            x, y = Fraction(a, b), Fraction(c, d)
            suma = azar.random() < 0.5
            if suma or x > y:
                return self._fracciones(nivel, a, b, c, d, comun, suma)

    def _fracciones(
        self, nivel: int, a: int, b: int, c: int, d: int, comun: int, suma: bool
    ) -> EjercicioGenerado:
        signo = "+" if suma else "−"
        x, y = a * comun // b, c * comun // d
        resultado = x + y if suma else x - y
        respuesta = f"{resultado}/{comun}"
        errores = [
            (
                f"{a + c if suma else abs(a - c)}/{comun}",
                "igualó los denominadores sin amplificar los numeradores",
                "Al cambiar el denominador, el numerador también tiene que cambiar.",
            ),
        ]
        if suma:
            errores.append(
                (
                    f"{a + c}/{b + d}",
                    "sumó numeradores y denominadores",
                    "Con denominadores distintos, primero hay que igualarlos.",
                )
            )
        return self._crear(
            nivel,
            f"Calcula {a}/{b} {signo} {c}/{d}.",
            "fraccion",
            respuesta,
            [
                f"Un múltiplo común de {b} y {d} es {comun}.",
                f"Queda {x}/{comun} {signo} {y}/{comun}.",
                f"El resultado es {respuesta}.",
            ],
            errores,
            [
                "Los denominadores son distintos: primero hay que igualarlos.",
                f"Busca un múltiplo común de {b} y {d}.",
                (
                    f"Usa {comun} como denominador y amplifica las dos fracciones.",
                    "Amplifica las dos fracciones al denominador común.",
                ),
            ],
        )

    def _mixtos(self, azar: random.Random, b: int, d: int) -> EjercicioGenerado:
        while True:
            e1, e2 = azar.randint(1, 5), azar.randint(1, 5)
            a, c = azar.randint(1, b - 1), azar.randint(1, d - 1)
            x, y = e1 + Fraction(a, b), e2 + Fraction(c, d)
            if x != y and gcd(a, b) == 1 and gcd(c, d) == 1:
                break
        if x <= y:
            e1, a, b, e2, c, d, x, y = e2, c, d, e1, a, b, y, x
        suma = azar.random() < 0.5
        signo = "+" if suma else "−"
        valor = x + y if suma else x - y
        respuesta = mixto(valor)
        comun = lcm(b, d)
        izquierda, derecha = f"{e1} {a}/{b}", f"{e2} {c}/{d}"
        impropia_x, impropia_y = int(x * comun), int(y * comun)
        juntos_enteros = e1 + e2 if suma else e1 - e2
        juntos_num = a + c if suma else abs(a - c)
        return self._crear(
            3,
            f"Calcula {izquierda} {signo} {derecha}.",
            "fraccion",
            respuesta,
            [
                f"Se escriben como impropias con denominador {comun}: "
                f"{impropia_x}/{comun} {signo} {impropia_y}/{comun}.",
                f"Se operan los numeradores y queda {int(valor * comun)}/{comun}.",
                f"Como número mixto, el resultado es {respuesta}.",
            ],
            [
                (
                    f"{juntos_enteros} {juntos_num}/{comun}",
                    "igualó los denominadores sin amplificar los numeradores",
                    "Al cambiar el denominador, el numerador también tiene que cambiar.",
                ),
                (
                    f"{juntos_enteros} {juntos_num}/{b + d}",
                    "operó también los denominadores",
                    "Los denominadores no se suman ni se restan: primero se igualan.",
                ),
            ],
            [
                "Puedes convertir los dos números mixtos en fracciones impropias.",
                f"Busca un múltiplo común de {b} y {d}.",
                (
                    f"Usa {comun} como denominador y opera los numeradores.",
                    "Usa el denominador común y opera los numeradores.",
                ),
            ],
            entrada_mixta=True,
        )


class MultiplicarDividirDecimales(Ficha):
    id = "6B-OA7-decimales"
    unidad_id = "6B-OA7"

    def instanciar(self, nivel: int, azar: random.Random) -> EjercicioGenerado:
        # N1: por 10, 100 o 1.000 · N2: × natural de un dígito · N3: : natural de un dígito.
        if nivel == 1:
            return self._por_potencia(azar)
        # El dividendo y el factor conservan sus cifras decimales: así "operar sin la coma" da un
        # resultado exacto y la coma se ubica contando (0,25 × 2 = 0,5 rompería la regla).
        while True:
            factor = azar.randint(2, 9)
            posiciones = azar.randint(1, 3)
            valor = Fraction(azar.randint(11, 10 ** (posiciones + 1) - 1), 10**posiciones)
            if _decimales(valor) == _decimales(valor * factor) == posiciones:
                break
        if nivel == 2:
            return self._operacion(2, valor, factor, valor * factor, "×", "multiplicar")
        return self._operacion(3, valor * factor, factor, valor, ":", "dividir")

    def _operacion(
        self, nivel: int, a: Fraction, n: int, resultado: Fraction, signo: str, verbo: str
    ) -> EjercicioGenerado:
        texto = decimal(a)
        decimales = _decimales(a)
        sin_coma = int(a * 10**decimales)
        cifras = "una cifra decimal" if decimales == 1 else f"{decimales} cifras decimales"
        return self._crear(
            nivel,
            f"Calcula {texto} {signo} {n}.",
            "numerico",
            decimal(resultado),
            [
                f"Se opera sin la coma: {miles(sin_coma)} {signo} {n}.",
                f"Se pone la coma contando {cifras} desde la derecha.",
                f"{texto} {signo} {n} = {decimal(resultado)}.",
            ],
            [
                (
                    decimal(resultado * 10),
                    "puso la coma un lugar a la derecha",
                    "Revisa dónde va la coma: cuenta las cifras decimales.",
                ),
                (
                    decimal(resultado / 10),
                    "puso la coma un lugar a la izquierda",
                    "Revisa dónde va la coma: cuenta las cifras decimales.",
                ),
            ],
            [
                f"Puedes {verbo} como si no hubiera coma.",
                f"Sin la coma, el cálculo es {miles(sin_coma)} {signo} {n}.",
                f"El resultado lleva {cifras}.",
            ],
        )

    def _por_potencia(self, azar: random.Random) -> EjercicioGenerado:
        ceros = azar.randint(1, 3)
        potencia = 10**ceros
        multiplica = azar.random() < 0.5
        posiciones = azar.randint(1, 3) if multiplica else azar.randint(1, 3 - ceros + 1)
        valor = Fraction(azar.randint(11, 10 ** (posiciones + 1) - 1), 10**posiciones)
        while valor.denominator == 1:
            valor = Fraction(azar.randint(11, 10 ** (posiciones + 1) - 1), 10**posiciones)
        signo = "×" if multiplica else ":"
        resultado = valor * potencia if multiplica else valor / potencia
        contrario = valor / potencia if multiplica else valor * potencia
        hacia = "derecha" if multiplica else "izquierda"
        return self._crear(
            1,
            f"Calcula {decimal(valor)} {signo} {miles(potencia)}.",
            "numerico",
            decimal(resultado),
            [
                f"{miles(potencia)} tiene {ceros} {'cero' if ceros == 1 else 'ceros'}.",
                f"La coma se corre {ceros} {'lugar' if ceros == 1 else 'lugares'} a la {hacia}.",
                f"{decimal(valor)} {signo} {miles(potencia)} = {decimal(resultado)}.",
            ],
            [
                (
                    decimal(contrario),
                    "corrió la coma hacia el lado contrario",
                    "Al multiplicar el número crece; al dividir, se achica.",
                ),
            ],
            [
                "Al multiplicar o dividir por 10, 100 o 1.000 solo se corre la coma.",
                f"Cuenta los ceros de {miles(potencia)}.",
                f"Corre la coma {ceros} {'lugar' if ceros == 1 else 'lugares'} a la {hacia}.",
            ],
        )
