"""Plantillas paramétricas de 4° básico (modelo_dominio.md §4)."""

import random
from fractions import Fraction

from tutor.dominio.plantillas_base import EjercicioGenerado, Ficha, circulo, miles, recta


def _cifras(n: int) -> list[int]:
    """Cifras de un número, de las unidades hacia arriba."""
    return [int(c) for c in reversed(str(n))]


def _suma_sin_reserva(a: int, b: int) -> int:
    """El error de no llevar la reserva: cada columna se suma por separado."""
    largo = max(len(str(a)), len(str(b)))
    return sum(((a // 10**i + b // 10**i) % 10) * 10**i for i in range(largo))


def _resta_sin_canje(a: int, b: int) -> int:
    """El error de restar en cada columna la cifra menor a la mayor, sin canjear."""
    largo = max(len(str(a)), len(str(b)))
    return sum(abs(a // 10**i % 10 - b // 10**i % 10) * 10**i for i in range(largo))


def _producto_sin_reserva(a: int, factor: int) -> int:
    """El error de multiplicar sin llevar la reserva."""
    return sum((c * factor % 10) * 10**i for i, c in enumerate(_cifras(a)))


POSICIONES = ["unidades", "decenas", "centenas", "unidades de mil"]


class ValorPosicional(Ficha):
    id = "4B-OA1-valor-posicional"
    unidad_id = "4B-OA1"

    def instanciar(self, nivel: int, azar: random.Random) -> EjercicioGenerado:
        # N1: componer · N2: valor de un dígito · N3: ordenar números hasta 10.000.
        if nivel == 1:
            return self._componer(azar)
        if nivel == 2:
            return self._valor_digito(azar)
        numeros = set()
        base = azar.randint(1, 8) * 1000
        while len(numeros) < 4:
            numeros.add(base + azar.randint(0, 1999))
        return self._ordenar(
            3,
            [(Fraction(n), miles(n)) for n in numeros],
            azar,
            ["Se compara primero la cifra de más a la izquierda y, si es igual, la siguiente."],
            "Fíjate bien: el primero tiene que ser el más pequeño.",
            [
                "Compara primero las unidades de mil de cada número.",
                "Si las unidades de mil son iguales, compara las centenas.",
                f"El menor de todos es {miles(min(numeros))}. Sigue con los demás.",
            ],
        )

    def _componer(self, azar: random.Random) -> EjercicioGenerado:
        m, c = azar.randint(1, 9), azar.randint(1, 9)
        d, u = azar.sample(range(1, 10), 2)
        n = m * 1000 + c * 100 + d * 10 + u
        return self._crear(
            1,
            f"Escribe con cifras el número que tiene {m} unidades de mil, {c} centenas, "
            f"{d} decenas y {u} unidades.",
            "numerico",
            str(n),
            [
                f"{m} unidades de mil son {miles(m * 1000)}.",
                f"{c} centenas son {c * 100}.",
                f"{d} decenas son {d * 10} y {u} unidades son {u}.",
                f"Se juntan: {miles(m * 1000)} + {c * 100} + {d * 10} + {u} = {miles(n)}.",
            ],
            [
                (
                    str(m * 1000 + c * 100 + u * 10 + d),
                    "intercambió las decenas y las unidades",
                    "Revisa el orden: las decenas van antes que las unidades.",
                ),
                (
                    str(m + c + d + u),
                    "sumó las cifras",
                    "No hay que sumar las cifras: cada una ocupa su lugar en el número.",
                ),
            ],
            [
                "Cada posición tiene su lugar: unidades de mil, centenas, decenas y unidades.",
                "Escribe las cifras en orden, partiendo por las unidades de mil.",
                f"El número parte con {m} y luego {c}. Te faltan las decenas y las unidades.",
            ],
        )

    def _valor_digito(self, azar: random.Random) -> EjercicioGenerado:
        cifras = azar.sample(range(1, 10), 4)
        n = int("".join(map(str, cifras)))
        posicion = azar.randint(1, 3)
        digito = _cifras(n)[posicion]
        valor = digito * 10**posicion
        return self._crear(
            2,
            f"¿Cuánto vale el dígito {digito} en el número {miles(n)}?",
            "numerico",
            str(valor),
            [
                f"El dígito {digito} está en las {POSICIONES[posicion]}.",
                f"Entonces vale {miles(valor)}.",
            ],
            [
                (
                    str(digito),
                    "dio el dígito sin considerar su posición",
                    "El valor del dígito depende del lugar donde está.",
                ),
                (
                    str(digito * 10 ** (posicion + 1)),
                    "contó una posición de más",
                    "Cuenta otra vez las posiciones desde la derecha.",
                ),
                (
                    str(digito * 10 ** (posicion - 1)),
                    "contó una posición de menos",
                    "Cuenta otra vez las posiciones desde la derecha.",
                ),
            ],
            [
                "Mira en qué posición está el dígito.",
                "De derecha a izquierda: unidades, decenas, centenas y unidades de mil.",
                f"El dígito está en las {POSICIONES[posicion]}.",
            ],
        )


class TablasMentales(Ficha):
    id = "4B-OA2-tablas"
    unidad_id = "4B-OA2"

    def instanciar(self, nivel: int, azar: random.Random) -> EjercicioGenerado:
        # N1: tablas del 2, 5 y 10 · N2: todas las tablas · N3: divisiones inversas.
        if nivel == 3:
            return self._division(azar)
        a = azar.choice([2, 5, 10]) if nivel == 1 else azar.randint(3, 9)
        b = azar.randint(2, 10)
        producto = a * b
        return self._crear(
            nivel,
            f"Calcula {a} × {b}.",
            "numerico",
            str(producto),
            [f"{a} × {b} es sumar {a} un total de {b} veces.", f"{a} × {b} = {producto}."],
            [
                (str(a + b), "sumó en vez de multiplicar", "Fíjate en el signo: es una ×."),
                (
                    str(a * (b + 1)),
                    "contó una vez de más",
                    "Casi: cuenta bien cuántas veces se repite el número.",
                ),
                (
                    str(a * (b - 1)),
                    "contó una vez de menos",
                    "Casi: cuenta bien cuántas veces se repite el número.",
                ),
            ],
            [
                "Multiplicar es sumar varias veces el mismo número.",
                f"Puedes sumar {a} una y otra vez, {b} veces en total.",
                (
                    f"{a} × {b - 1} = {a * (b - 1)}. Te falta sumar {a} una vez más.",
                    "Parte de la multiplicación anterior de la tabla y suma una vez más.",
                ),
            ],
        )

    def _division(self, azar: random.Random) -> EjercicioGenerado:
        a, b = azar.randint(2, 9), azar.randint(2, 10)
        p = a * b
        return self._crear(
            3,
            f"Calcula {p} : {a}.",
            "numerico",
            str(b),
            [f"Se busca qué número multiplicado por {a} da {p}.", f"{p} : {a} = {b}."],
            [
                (str(p - a), "restó en vez de dividir", "Fíjate en el signo: es una división."),
                (
                    str(b + 1),
                    "se pasó en la tabla",
                    "Comprueba tu respuesta multiplicándola por el divisor.",
                ),
            ],
            [
                (
                    "Dividir es lo contrario de multiplicar.",
                    "Dividir es repartir en partes iguales.",
                ),
                (
                    f"¿Qué número multiplicado por {a} da {p}?",
                    "Busca qué número multiplicado por el divisor da el dividendo.",
                ),
                (
                    f"Recita la tabla del {a} hasta llegar a {p}.",
                    "Recita la tabla del divisor hasta llegar al dividendo.",
                ),
            ],
        )


class SumaResta(Ficha):
    id = "4B-OA3-suma-resta"
    unidad_id = "4B-OA3"

    def instanciar(self, nivel: int, azar: random.Random) -> EjercicioGenerado:
        # N1: sin reserva ni canje · N2: con reserva o canje · N3: hasta 4 sumandos.
        if nivel == 3:
            return self._varios_sumandos(azar)
        if azar.random() < 0.5:
            while True:
                a, b = azar.randint(101, 899), azar.randint(101, 899)
                lleva = _suma_sin_reserva(a, b) != a + b
                if a + b <= 1000 and lleva == (nivel == 2):
                    return self._operacion(nivel, a, b, "+", a + b, _suma_sin_reserva(a, b))
        while True:
            a, b = azar.randint(201, 999), azar.randint(101, 899)
            if b >= a:
                continue
            canjea = _resta_sin_canje(a, b) != a - b
            if canjea == (nivel == 2):
                return self._operacion(nivel, a, b, "−", a - b, _resta_sin_canje(a, b))

    def _operacion(
        self, nivel: int, a: int, b: int, signo: str, resultado: int, sin_llevar: int
    ) -> EjercicioGenerado:
        es_suma = signo == "+"
        errores = [
            (
                str(sin_llevar),
                "no llevó la reserva" if es_suma else "restó sin canjear",
                "Revisa las columnas donde el resultado pasa de 9."
                if es_suma
                else "Si la cifra de arriba es menor, tienes que canjear de la columna siguiente.",
            ),
            (
                str(a - b if es_suma else a + b),
                "restó en vez de sumar" if es_suma else "sumó en vez de restar",
                "Fíjate en el signo de la operación.",
            ),
        ]
        ordenes = "Se suman" if es_suma else "Se restan"
        return self._crear(
            nivel,
            f"Calcula {a} {signo} {b}.",
            "numerico",
            str(resultado),
            [
                "Se escribe un número debajo del otro, alineando las posiciones.",
                f"{ordenes} unidades, decenas y centenas, en ese orden.",
                f"{a} {signo} {b} = {miles(resultado)}.",
            ],
            errores,
            [
                "Escribe un número debajo del otro, con las posiciones alineadas.",
                "Empieza por las unidades, luego las decenas y al final las centenas.",
                (
                    f"En las unidades tienes {a % 10} {signo} {b % 10}. Sigue con las demás.",
                    "Revisa primero la columna de las unidades y sigue con las demás.",
                ),
            ],
        )

    def _varios_sumandos(self, azar: random.Random) -> EjercicioGenerado:
        cantidad = azar.choice([3, 4])
        sumandos = [azar.randint(11, 1000 // cantidad) for _ in range(cantidad)]
        total = sum(sumandos)
        texto = " + ".join(map(str, sumandos))
        parcial = sum(sumandos[:2])
        return self._crear(
            3,
            f"Calcula {texto}.",
            "numerico",
            str(total),
            [
                f"Primero, {sumandos[0]} + {sumandos[1]} = {parcial}.",
                f"Se suman los demás de a uno: {texto} = {miles(total)}.",
            ],
            [
                (
                    str(total - sumandos[-1]),
                    "olvidó el último sumando",
                    "Revisa que hayas sumado todos los números.",
                ),
            ],
            [
                "Puedes sumar de a dos números, en orden.",
                f"Parte con {sumandos[0]} + {sumandos[1]}.",
                (
                    f"{sumandos[0]} + {sumandos[1]} = {parcial}. Ahora suma lo que falta.",
                    "Suma el resultado que llevas con el número que sigue.",
                ),
            ],
        )


class Multiplicacion(Ficha):
    id = "4B-OA5-multiplicacion"
    unidad_id = "4B-OA5"

    def instanciar(self, nivel: int, azar: random.Random) -> EjercicioGenerado:
        # N1: sin reserva · N2: con reserva · N3: con la propiedad distributiva.
        factor = azar.randint(2, 4) if nivel == 1 else azar.randint(2, 9)
        if nivel == 1:
            maximo = 9 // factor
            a = int("".join(str(azar.randint(1, maximo)) for _ in range(3)))
        else:
            cifras = [azar.randint(1, 9) for _ in range(3)]
            a = int("".join(map(str, cifras)))
            while _producto_sin_reserva(a, factor) == a * factor:
                a = int("".join(str(azar.randint(1, 9)) for _ in range(3)))
        c, d, u = a // 100 * 100, a // 10 % 10 * 10, a % 10
        producto = a * factor
        pregunta = (
            f"Para calcular {a} × {factor} se separa {a} en {c} + {d} + {u}. ¿Cuál es el resultado?"
            if nivel == 3
            else f"Calcula {a} × {factor}."
        )
        return self._crear(
            nivel,
            pregunta,
            "numerico",
            str(producto),
            [
                f"{u} × {factor} = {u * factor}.",
                f"{d} × {factor} = {d * factor}.",
                f"{c} × {factor} = {miles(c * factor)}.",
                f"Se suman: {miles(c * factor)} + {d * factor} + {u * factor} = {miles(producto)}.",
            ],
            [
                (
                    str(_producto_sin_reserva(a, factor)),
                    "no llevó la reserva",
                    "Si un producto pasa de 9, lo que sobra se suma en la columna siguiente.",
                ),
                (str(a + factor), "sumó en vez de multiplicar", "Fíjate en el signo: es una ×."),
                (
                    str(c * factor),
                    "multiplicó solo las centenas",
                    "Multiplica también las decenas y las unidades.",
                ),
            ],
            [
                f"Multiplica por {factor} cada posición: unidades, decenas y centenas.",
                f"Empieza con {u} × {factor}.",
                f"Ahora suma {c} × {factor}, {d} × {factor} y {u} × {factor}.",
            ],
        )


class Division(Ficha):
    id = "4B-OA6-division"
    unidad_id = "4B-OA6"

    def instanciar(self, nivel: int, azar: random.Random) -> EjercicioGenerado:
        # N1: divisor 2 a 5 · N2: divisor 2 a 9 · N3: la división como multiplicación inversa.
        divisor = azar.randint(2, 5) if nivel == 1 else azar.randint(3, 9)
        cociente = azar.randint(10 // divisor + 1, 99 // divisor)
        dividendo = cociente * divisor
        pregunta = (
            f"¿Qué número multiplicado por {divisor} da {dividendo}?"
            if nivel == 3
            else f"Calcula {dividendo} : {divisor}."
        )
        return self._crear(
            nivel,
            pregunta,
            "numerico",
            str(cociente),
            [
                f"Se busca qué número multiplicado por {divisor} da {dividendo}.",
                f"{cociente} × {divisor} = {dividendo}, así que el resultado es {cociente}.",
            ],
            [
                (
                    str(dividendo - divisor),
                    "restó en vez de dividir",
                    "Hay que ver cuántas veces cabe, no restarlo una sola vez.",
                ),
                (
                    str(cociente + 1),
                    "se pasó en una vez",
                    "Comprueba multiplicando tu respuesta por el divisor.",
                ),
            ],
            [
                "Dividir es repartir en partes iguales.",
                (
                    f"Piensa en la tabla del {divisor}.",
                    "Piensa en la tabla de multiplicar del divisor.",
                ),
                (
                    f"{divisor} × 10 = {divisor * 10}. ¿Cuánto te falta para llegar a {dividendo}?"
                    if dividendo > divisor * 10
                    else f"Recita la tabla del {divisor} hasta llegar a {dividendo}.",
                    "Recita la tabla del divisor hasta llegar al dividendo.",
                ),
            ],
        )


class ConceptoFraccion(Ficha):
    id = "4B-OA8-concepto-fraccion"
    unidad_id = "4B-OA8"
    DENOMINADORES = [2, 3, 4, 5, 6, 8, 10, 12]

    def instanciar(self, nivel: int, azar: random.Random) -> EjercicioGenerado:
        # N1: parte de un todo (círculo) · N2: ubicar en la recta · N3: comparar.
        if nivel == 3:
            return self._comparacion(azar)
        d = azar.choice(self.DENOMINADORES)
        a = azar.randint(1, d - 1)
        respuesta = f"{a}/{d}"
        if nivel == 1:
            return self._crear(
                1,
                f"Un círculo está dividido en {d} partes iguales y algunas están pintadas. "
                "¿Qué fracción está pintada?",
                "fraccion",
                respuesta,
                [
                    f"El círculo tiene {d} partes iguales: ese es el denominador.",
                    f"Hay {a} partes pintadas: ese es el numerador.",
                    f"La fracción pintada es {respuesta}.",
                ],
                [
                    (
                        f"{d - a}/{d}",
                        "contó las partes sin pintar",
                        "Cuenta solo las partes que tienen color.",
                    ),
                    (
                        f"{a}/{d - a}",
                        "comparó lo pintado con lo no pintado",
                        "El número de abajo es el total de partes del círculo.",
                    ),
                ],
                [
                    "El número de abajo dice en cuántas partes iguales está dividido el todo.",
                    "El número de arriba dice cuántas partes están pintadas.",
                    f"Abajo va {d}. Ahora cuenta las partes pintadas.",
                ],
                representacion=circulo(d, a),
            )
        return self._crear(
            2,
            f"Una recta va de 0 a 1 y está dividida en {d} partes iguales. "
            "¿Qué fracción marca el punto?",
            "fraccion",
            respuesta,
            [
                f"De 0 a 1 hay {d} tramos iguales: el denominador es {d}.",
                f"Desde el 0 hasta el punto hay {a} tramos.",
                f"El punto marca {respuesta}.",
            ],
            [
                (
                    f"{a}/{d + 1}",
                    "contó las marcas en vez de los tramos",
                    "Cuenta los espacios entre las marcas, no las marcas.",
                ),
                (
                    f"{d - a}/{d}",
                    "contó desde el 1 hacia atrás",
                    "Cuenta los tramos partiendo desde el 0.",
                ),
            ],
            [
                "Cuenta cuántos tramos iguales hay entre 0 y 1.",
                "Ese número de tramos es el denominador.",
                f"Abajo va {d}. Ahora cuenta los tramos desde 0 hasta el punto.",
            ],
            representacion=recta(1, d, a),
        )

    def _comparacion(self, azar: random.Random) -> EjercicioGenerado:
        if azar.random() < 0.5:
            d = azar.choice([d for d in self.DENOMINADORES if d >= 4])
            a, b = azar.sample(range(1, d), 2)
            return self._comparar(
                3,
                f"{a}/{d}",
                f"{b}/{d}",
                (Fraction(a, d), Fraction(b, d)),
                [f"Las dos fracciones tienen {d} partes iguales.", "Se comparan los numeradores."],
                "se confundió con el sentido del signo",
                "La abertura del signo mira hacia la fracción mayor.",
                [
                    "Mira los denominadores: ¿son iguales?",
                    "Si son iguales, gana la fracción con más partes.",
                    "Compara solo los números de arriba.",
                ],
            )
        n = azar.randint(1, 3)
        d1, d2 = azar.sample([d for d in self.DENOMINADORES if d > n], 2)
        return self._comparar(
            3,
            f"{n}/{d1}",
            f"{n}/{d2}",
            (Fraction(n, d1), Fraction(n, d2)),
            ["Las dos tienen el mismo numerador.", "Con más partes, cada parte es más pequeña."],
            "creyó que un denominador mayor da una fracción mayor",
            "Mientras más partes tiene el todo, más pequeña es cada parte.",
            [
                "Mira los numeradores: ¿son iguales?",
                "Imagina dos pizzas iguales cortadas en distinta cantidad de trozos.",
                "Mientras más trozos, más pequeño es cada uno.",
            ],
        )
