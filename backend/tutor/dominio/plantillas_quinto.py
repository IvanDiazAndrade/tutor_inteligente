"""Plantillas paramétricas de 5° básico (modelo_dominio.md §4). 5B-OA4 está en plantillas.py."""

import random
from fractions import Fraction
from math import gcd, lcm

from tutor.dominio.plantillas_base import (
    EjercicioGenerado,
    Ficha,
    circulo,
    cuadricula,
    decimal,
    miles,
)

POSICIONES = [
    "unidades",
    "decenas",
    "centenas",
    "unidades de mil",
    "decenas de mil",
    "centenas de mil",
    "unidades de millón",
    "decenas de millón",
    "centenas de millón",
]


class NumerosGrandes(Ficha):
    id = "5B-OA1-numeros-grandes"
    unidad_id = "5B-OA1"

    def instanciar(self, nivel: int, azar: random.Random) -> EjercicioGenerado:
        # N1: valor de un dígito · N2: forma expandida · N3: aproximar u ordenar.
        if nivel == 1:
            return self._valor_digito(azar)
        if nivel == 2:
            return self._expandida(azar)
        return self._aproximar(azar) if azar.random() < 0.5 else self._orden(azar)

    def _valor_digito(self, azar: random.Random) -> EjercicioGenerado:
        cifras = azar.sample(range(1, 10), azar.randint(6, 9))
        n = int("".join(map(str, cifras)))
        posicion = azar.randint(3, len(cifras) - 1)
        digito = int(str(n)[-1 - posicion])
        valor = digito * 10**posicion
        return self._crear(
            1,
            f"¿Cuánto vale el dígito {digito} en el número {miles(n)}?",
            "numerico",
            str(valor),
            [f"El dígito {digito} está en las {POSICIONES[posicion]}.", f"Vale {miles(valor)}."],
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
            ],
            [
                "Mira en qué posición está el dígito.",
                "Los puntos separan los grupos de tres cifras: unidades, miles y millones.",
                f"El dígito está en las {POSICIONES[posicion]}.",
            ],
        )

    def _expandida(self, azar: random.Random) -> EjercicioGenerado:
        largo = azar.randint(7, 9)
        cifras = [azar.randint(1, 9)] + [
            azar.randint(1, 9) if azar.random() < 0.6 else 0 for _ in range(largo - 1)
        ]
        n = int("".join(map(str, cifras)))
        sumandos = [c * 10 ** (largo - 1 - i) for i, c in enumerate(cifras) if c]
        texto = " + ".join(miles(s) for s in sumandos)
        sin_ceros = int("".join(str(c) for c in cifras if c))
        return self._crear(
            2,
            f"Escribe con cifras el número {texto}.",
            "numerico",
            str(n),
            ["Cada sumando aporta una cifra en su posición.", f"El número es {miles(n)}."],
            [
                (
                    str(sin_ceros),
                    "olvidó los ceros de las posiciones vacías",
                    "Si una posición no aparece en la suma, ahí va un 0.",
                ),
            ],
            [
                "Cada sumando aporta una sola cifra, en su posición.",
                "Si una posición no aparece en la suma, ahí va un 0.",
                f"El número tiene {largo} cifras en total.",
            ],
        )

    def _aproximar(self, azar: random.Random) -> EjercicioGenerado:
        n = azar.randint(1_000_000, 999_999_999)
        posicion = azar.choice([3, 4, 5, 6])
        potencia = 10**posicion
        abajo = n // potencia * potencia
        arriba = abajo + potencia
        aproximado = arriba if n % potencia >= potencia // 2 else abajo
        siguiente = str(n)[-posicion]
        return self._crear(
            3,
            f"Aproxima {miles(n)} a la posición de las {POSICIONES[posicion]}.",
            "numerico",
            str(aproximado),
            [
                f"Se mira la cifra a la derecha de las {POSICIONES[posicion]}: es {siguiente}.",
                "Si es 5 o más se sube; si es menor, se deja igual.",
                f"El número aproximado es {miles(aproximado)}.",
            ],
            [
                (
                    str(abajo),
                    "cortó el número sin mirar la cifra siguiente",
                    "Mira la cifra de la derecha: si es 5 o más, se sube.",
                ),
                (
                    str(arriba),
                    "subió sin que correspondiera",
                    "Mira la cifra de la derecha: si es menor que 5, se deja igual.",
                ),
            ],
            [
                f"Busca la posición de las {POSICIONES[posicion]}.",
                "Mira la cifra que está justo a su derecha.",
                f"Esa cifra es {siguiente}. ¿Es 5 o más?",
            ],
        )

    def _orden(self, azar: random.Random) -> EjercicioGenerado:
        base = azar.randint(1, 900) * 1_000_000
        numeros = set()
        while len(numeros) < 4:
            numeros.add(base + azar.randint(0, 9_999_999))
        return self._ordenar(
            3,
            [(Fraction(n), miles(n)) for n in numeros],
            azar,
            ["Se comparan las cifras de izquierda a derecha, en la misma posición."],
            "Fíjate bien: el primero tiene que ser el más pequeño.",
            [
                "Mira primero cuántas cifras tiene cada número.",
                "Si tienen las mismas cifras, compara de izquierda a derecha.",
                f"El menor de todos es {miles(min(numeros))}. Sigue con los demás.",
            ],
        )


class Multiplicacion2x2(Ficha):
    id = "5B-OA3-multiplicacion"
    unidad_id = "5B-OA3"

    def instanciar(self, nivel: int, azar: random.Random) -> EjercicioGenerado:
        # N1: por un múltiplo de 10 · N2: dos dígitos × dos dígitos · N3: estimar.
        if nivel == 3:
            return self._estimar(azar)
        a = azar.randint(11, 49) if nivel == 1 else azar.randint(11, 99)
        if nivel == 1:
            b = azar.randint(2, 9) * 10
        else:
            b = azar.randint(11, 99)
            while b % 10 == 0:
                b = azar.randint(11, 99)
        decenas, unidades = b // 10 * 10, b % 10
        producto = a * b
        pasos = [f"{a} × {unidades} = {a * unidades}."] if unidades else []
        pasos += [f"{a} × {decenas} = {miles(a * decenas)}."]
        if unidades:
            pasos.append(f"Se suman: {a * unidades} + {miles(a * decenas)} = {miles(producto)}.")
        else:
            pasos.append(f"El resultado es {miles(producto)}.")
        return self._crear(
            nivel,
            f"Calcula {a} × {b}.",
            "numerico",
            str(producto),
            pasos,
            [
                (
                    str(a * unidades + a * (decenas // 10)),
                    "olvidó el cero del segundo producto",
                    "Al multiplicar por las decenas, el resultado se corre un lugar.",
                ),
                (str(a + b), "sumó en vez de multiplicar", "Fíjate en el signo: es una ×."),
            ],
            [
                f"Separa {b} en decenas y unidades." if unidades else f"{b} es {b // 10} × 10.",
                f"Multiplica {a} por cada parte."
                if unidades
                else f"Multiplica {a} × {b // 10} y agrega un cero.",
                f"Ahora suma {a} × {unidades} y {a} × {decenas}."
                if unidades
                else "No olvides el cero del final.",
            ],
        )

    def _estimar(self, azar: random.Random) -> EjercicioGenerado:
        a, b = azar.randint(12, 94), azar.randint(12, 94)
        while a % 10 == 0 or b % 10 == 0:
            a, b = azar.randint(12, 94), azar.randint(12, 94)
        ra, rb = (a + 5) // 10 * 10, (b + 5) // 10 * 10
        estimacion = ra * rb
        return self._crear(
            3,
            f"Estima {a} × {b} redondeando cada factor a la decena más cercana.",
            "numerico",
            str(estimacion),
            [
                f"{a} se redondea a {ra} y {b} se redondea a {rb}.",
                f"{ra} × {rb} = {miles(estimacion)}.",
            ],
            [
                (
                    str(a * b),
                    "calculó el producto exacto",
                    "Aquí no se pide el exacto: primero redondea cada número.",
                ),
                (
                    str(a // 10 * 10 * (b // 10 * 10)),
                    "cortó las unidades en vez de redondear",
                    "Si la unidad es 5 o más, se redondea hacia arriba.",
                ),
            ],
            [
                "Redondea cada factor a la decena más cercana.",
                f"Si la unidad es 5 o más, se sube a la decena siguiente: mira {a} y {b}.",
                f"{a} se redondea a {ra}. Haz lo mismo con el otro factor.",
            ],
        )


class OperatoriaCombinada(Ficha):
    id = "5B-OA5-combinada"
    unidad_id = "5B-OA5"

    def instanciar(self, nivel: int, azar: random.Random) -> EjercicioGenerado:
        # N1: una × con + o − · N2: paréntesis o división · N3: tres operaciones.
        a, b, c = azar.randint(2, 30), azar.randint(2, 9), azar.randint(2, 9)
        if nivel == 1:
            return self._sin_parentesis(a, b, c)
        if nivel == 2:
            if azar.random() < 0.5:
                return self._con_parentesis(a, b, c)
            return self._con_division(a, b, c)
        d = azar.randint(1, 9)
        if azar.random() < 0.5:
            return self._dos_productos(b, c, azar.randint(2, 9), azar.randint(2, 9))
        return self._parentesis_y_resta(a, b, c, d)

    def _sin_parentesis(self, a: int, b: int, c: int) -> EjercicioGenerado:
        resultado = a + b * c
        return self._crear(
            1,
            f"Calcula {a} + {b} × {c}.",
            "numerico",
            str(resultado),
            [
                f"Primero la multiplicación: {b} × {c} = {b * c}.",
                f"Luego, {a} + {b * c} = {resultado}.",
            ],
            [
                (
                    str((a + b) * c),
                    "calculó de izquierda a derecha",
                    "La multiplicación se hace antes que la suma.",
                ),
            ],
            [
                "La multiplicación y la división se hacen antes que la suma y la resta.",
                f"Parte con {b} × {c}.",
                f"Ahora suma {a} al resultado de {b} × {c}.",
            ],
        )

    def _con_parentesis(self, a: int, b: int, c: int) -> EjercicioGenerado:
        resultado = (a + b) * c
        return self._crear(
            2,
            f"Calcula ({a} + {b}) × {c}.",
            "numerico",
            str(resultado),
            [
                f"Primero el paréntesis: {a} + {b} = {a + b}.",
                f"Luego, {a + b} × {c} = {resultado}.",
            ],
            [
                (
                    str(a + b * c),
                    "no respetó el paréntesis",
                    "Lo que está entre paréntesis se calcula primero.",
                ),
            ],
            [
                "Lo que está entre paréntesis se calcula primero.",
                f"Parte con {a} + {b}.",
                f"Ahora multiplica por {c} lo que te dio el paréntesis.",
            ],
        )

    def _con_division(self, a: int, b: int, c: int) -> EjercicioGenerado:
        dividendo = b * c
        resultado = a + c
        errores = [
            (
                str(a + dividendo),
                "ignoró la división",
                "Falta dividir: hazlo antes de sumar.",
            ),
        ]
        if (a + dividendo) % b == 0:
            errores.append(
                (
                    str((a + dividendo) // b),
                    "calculó de izquierda a derecha",
                    "La división se hace antes que la suma.",
                )
            )
        return self._crear(
            2,
            f"Calcula {a} + {dividendo} : {b}.",
            "numerico",
            str(resultado),
            [f"Primero la división: {dividendo} : {b} = {c}.", f"Luego, {a} + {c} = {resultado}."],
            errores,
            [
                "La división se hace antes que la suma.",
                f"Parte con {dividendo} : {b}.",
                f"Ahora suma {a} al resultado de esa división.",
            ],
        )

    def _dos_productos(self, a: int, b: int, c: int, d: int) -> EjercicioGenerado:
        resultado = a * b + c * d
        return self._crear(
            3,
            f"Calcula {a} × {b} + {c} × {d}.",
            "numerico",
            str(resultado),
            [
                f"{a} × {b} = {a * b}.",
                f"{c} × {d} = {c * d}.",
                f"{a * b} + {c * d} = {resultado}.",
            ],
            [
                (
                    str((a * b + c) * d),
                    "calculó de izquierda a derecha",
                    "Las dos multiplicaciones se hacen antes que la suma.",
                ),
            ],
            [
                "Primero se hacen las dos multiplicaciones.",
                f"Calcula {a} × {b} y {c} × {d}.",
                "Ahora suma los dos resultados.",
            ],
        )

    def _parentesis_y_resta(self, a: int, b: int, c: int, d: int) -> EjercicioGenerado:
        resultado = (a + b) * c - d
        return self._crear(
            3,
            f"Calcula ({a} + {b}) × {c} − {d}.",
            "numerico",
            str(resultado),
            [
                f"Primero el paréntesis: {a} + {b} = {a + b}.",
                f"Luego la multiplicación: {a + b} × {c} = {(a + b) * c}.",
                f"Al final la resta: {(a + b) * c} − {d} = {resultado}.",
            ],
            [
                (
                    str(a + b * c - d),
                    "no respetó el paréntesis",
                    "Lo que está entre paréntesis se calcula primero.",
                ),
            ],
            [
                "El orden es: paréntesis, multiplicación y al final la resta.",
                f"Parte con {a} + {b}.",
                f"Multiplica ese resultado por {c} y después resta {d}.",
            ],
        )


def _propia_irreducible(azar: random.Random, denominadores: list[int]) -> tuple[int, int]:
    while True:
        d = azar.choice(denominadores)
        a = azar.randint(1, d - 1)
        if gcd(a, d) == 1:
            return a, d


class Equivalencia(Ficha):
    id = "5B-OA7-equivalencia"
    unidad_id = "5B-OA7"

    def instanciar(self, nivel: int, azar: random.Random) -> EjercicioGenerado:
        # N1: amplificar · N2: simplificar · N3: comparar con distinto denominador.
        # En amplificar y simplificar la forma es el objetivo: aceptaEquivalentes = false.
        if nivel == 3:
            return self._comparacion(azar)
        a, d = _propia_irreducible(azar, [2, 3, 4, 5, 6, 7, 8, 9, 10])
        k = azar.randint(2, 6)
        if nivel == 1:
            return self._amplificar(a, d, k)
        return self._simplificar(a, d, k)

    def _amplificar(self, a: int, d: int, k: int) -> EjercicioGenerado:
        respuesta = f"{a * k}/{d * k}"
        return self._crear(
            1,
            f"Amplifica {a}/{d} por {k}.",
            "fraccion",
            respuesta,
            [
                "Amplificar es multiplicar arriba y abajo por el mismo número.",
                f"Arriba: {a} × {k} = {a * k}. Abajo: {d} × {k} = {d * k}.",
                f"El resultado es {respuesta}.",
            ],
            [
                (
                    f"{a + k}/{d + k}",
                    "sumó en vez de multiplicar",
                    "Amplificar es multiplicar, no sumar.",
                ),
                (
                    f"{a * k}/{d}",
                    "multiplicó solo el numerador",
                    "Hay que multiplicar también el número de abajo.",
                ),
                (
                    f"{a}/{d * k}",
                    "multiplicó solo el denominador",
                    "Hay que multiplicar también el número de arriba.",
                ),
            ],
            [
                "Amplificar es multiplicar arriba y abajo por el mismo número.",
                f"Multiplica el número de arriba por {k}.",
                f"Ahora multiplica también el número de abajo por {k}.",
            ],
            equivalentes=False,
            representacion=circulo(d, a),
        )

    def _simplificar(self, a: int, d: int, k: int) -> EjercicioGenerado:
        respuesta = f"{a}/{d}"
        return self._crear(
            2,
            f"Simplifica {a * k}/{d * k} hasta que no se pueda más.",
            "fraccion",
            respuesta,
            [
                f"Los dos números se pueden dividir por {k}.",
                f"Arriba: {a * k} : {k} = {a}. Abajo: {d * k} : {k} = {d}.",
                f"El resultado es {respuesta}.",
            ],
            [
                (
                    f"{a}/{d * k}",
                    "dividió solo el numerador",
                    "Hay que dividir también el número de abajo.",
                ),
                (
                    f"{a * k}/{d}",
                    "dividió solo el denominador",
                    "Hay que dividir también el número de arriba.",
                ),
            ],
            [
                "Busca un número que divida al numerador y al denominador a la vez.",
                f"Prueba dividiendo los dos números por {k}.",
                "Revisa si todavía se puede dividir arriba y abajo por el mismo número.",
            ],
            equivalentes=False,
        )

    def _comparacion(self, azar: random.Random) -> EjercicioGenerado:
        a, b = _propia_irreducible(azar, [2, 3, 4, 5, 6, 8, 10, 12])
        if azar.random() < 0.2:
            k = azar.randint(2, 4)
            c, d = a * k, b * k
        else:
            c, d = _propia_irreducible(azar, [2, 3, 4, 5, 6, 8, 10, 12])
            while d == b:
                c, d = _propia_irreducible(azar, [2, 3, 4, 5, 6, 8, 10, 12])
        comun = lcm(b, d)
        izquierda = a * comun // b
        derecha = c * comun // d
        return self._comparar(
            3,
            f"{a}/{b}",
            f"{c}/{d}",
            (Fraction(a, b), Fraction(c, d)),
            [
                f"Se usa el denominador común {comun}.",
                f"Queda {izquierda}/{comun} y {derecha}/{comun}: se comparan los numeradores.",
            ],
            "comparó sin igualar los denominadores",
            "Para comparar, primero deja las dos fracciones con el mismo denominador.",
            [
                "Para comparar, las dos fracciones deben tener el mismo denominador.",
                f"Busca un múltiplo común de {b} y {d}.",
                f"Puedes usar {comun} como denominador común.",
            ],
        )


class SumaDistintoDenominador(Ficha):
    id = "5B-OA9-distinto-den"
    unidad_id = "5B-OA9"
    MULTIPLOS = [
        (2, 4),
        (2, 6),
        (3, 6),
        (2, 8),
        (4, 8),
        (2, 10),
        (5, 10),
        (3, 12),
        (4, 12),
        (6, 12),
    ]
    OTROS = [(2, 3), (3, 4), (4, 6), (2, 5), (2, 12)]

    def instanciar(self, nivel: int, azar: random.Random) -> EjercicioGenerado:
        # N1: un denominador es múltiplo del otro · N2: cualquier par hasta 12 · N3: resta.
        pares = self.MULTIPLOS if nivel == 1 else self.MULTIPLOS + self.OTROS
        while True:
            b, d = azar.choice(pares)
            if azar.random() < 0.5:
                b, d = d, b
            a, c = azar.randint(1, b - 1), azar.randint(1, d - 1)
            if gcd(a, b) != 1 or gcd(c, d) != 1:
                continue
            comun = lcm(b, d)
            ampliada_a, ampliada_c = a * comun // b, c * comun // d
            if nivel == 3:
                if ampliada_a > ampliada_c:
                    return self._operacion(3, a, b, c, d, "−")
            elif ampliada_a + ampliada_c < comun:
                return self._operacion(nivel, a, b, c, d, "+")

    def _operacion(
        self, nivel: int, a: int, b: int, c: int, d: int, signo: str
    ) -> EjercicioGenerado:
        comun = lcm(b, d)
        x, y = a * comun // b, c * comun // d
        resultado = x + y if signo == "+" else x - y
        respuesta = f"{resultado}/{comun}"
        pasos_amplificar = f"Queda {x}/{comun} {signo} {y}/{comun}."
        operar = "Se suman" if signo == "+" else "Se restan"
        juntos = a + c if signo == "+" else abs(a - c)
        errores = [
            (
                f"{juntos}/{comun}",
                "igualó los denominadores sin amplificar los numeradores",
                "Al cambiar el denominador, el numerador también tiene que cambiar.",
            ),
        ]
        if signo == "+":
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
                f"Los denominadores son distintos. Un múltiplo común de {b} y {d} es {comun}.",
                pasos_amplificar,
                f"{operar} los numeradores: {x} {signo} {y} = {resultado}.",
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


class FraccionDecimal(Ficha):
    id = "5B-OA10-fraccion-decimal"
    unidad_id = "5B-OA10"

    def instanciar(self, nivel: int, azar: random.Random) -> EjercicioGenerado:
        # N1: décimos con cuadrícula · N2: denominadores 2, 4 y 5 · N3: de decimal a fracción.
        if nivel == 1:
            a, d = azar.randint(1, 9), 10
        elif nivel == 2:
            a, d = azar.choice(
                [(1, 2), (1, 4), (3, 4), (1, 5), (2, 5), (3, 5), (4, 5), (3, 2), (5, 4)]
            )
        else:
            a, d = azar.choice(
                [(1, 2), (1, 4), (3, 4), (1, 5), (2, 5), (3, 5), (4, 5), (3, 10), (7, 10), (9, 10)]
            )
        if nivel == 3:
            return self._a_fraccion(a, d)
        return self._a_decimal(nivel, a, d)

    def _a_decimal(self, nivel: int, a: int, d: int) -> EjercicioGenerado:
        valor = Fraction(a, d)
        respuesta = decimal(valor)
        destino = 10 if d in (2, 5, 10) else 100
        factor = destino // d
        pasos = (
            [f"{a}/{d} se lee {a} {'décimo' if a == 1 else 'décimos'}.", f"Se escribe {respuesta}."]
            if d == 10
            else [
                f"Se amplifica hasta tener denominador {destino}, multiplicando por {factor}.",
                f"Queda {a * factor}/{destino}, que se escribe {respuesta}.",
            ]
        )
        return self._crear(
            nivel,
            f"Escribe {a}/{d} como número decimal.",
            "numerico",
            respuesta,
            pasos,
            [
                (
                    f"{a},{d}",
                    "juntó el numerador y el denominador con una coma",
                    "La coma no separa los dos números: la fracción es una división.",
                ),
                (
                    decimal(Fraction(a, 100)),
                    "corrió la coma un lugar de más",
                    "Fíjate en cuántos ceros tiene el denominador.",
                ),
            ],
            [
                "Una fracción con denominador 10 o 100 se escribe directo como decimal.",
                "Si el denominador no es 10, amplifica hasta llegar a 10 o 100."
                if d != 10
                else "El denominador 10 significa décimos: una cifra después de la coma.",
                f"Multiplica arriba y abajo por {factor} para llegar a {destino}."
                if d != 10
                else f"El {a} va en la primera posición después de la coma.",
            ],
            representacion=cuadricula(a * 100 // d) if valor < 1 else None,
        )

    def _a_fraccion(self, a: int, d: int) -> EjercicioGenerado:
        valor = Fraction(a, d)
        texto = decimal(valor)
        posiciones = len(texto.split(",")[1])
        potencia = 10**posiciones
        sin_coma = int(valor * potencia)
        respuesta = f"{a}/{d}"
        cifras = "una cifra" if posiciones == 1 else f"{posiciones} cifras"
        pasos = [f"{texto} tiene {cifras} después de la coma."]
        pasos.append(f"Se escribe {sin_coma} sobre {potencia}.")
        if potencia != d:
            pasos.append(f"Simplificando, queda {respuesta}.")
        else:
            pasos.append(f"El resultado es {respuesta}.")
        return self._crear(
            3,
            f"Escribe {texto} como fracción.",
            "fraccion",
            respuesta,
            pasos,
            [
                (
                    f"{sin_coma}/{potencia * 10}",
                    "usó un denominador con un cero de más",
                    "Cuenta las cifras después de la coma: esos son los ceros del denominador.",
                ),
                (
                    f"{potencia}/{sin_coma}",
                    "dio vuelta la fracción",
                    "La potencia de 10 va abajo, en el denominador.",
                ),
            ],
            [
                "Lee el número: ¿hasta qué posición llega después de la coma?",
                "Con una cifra después de la coma el denominador es 10; con dos, es 100.",
                (
                    f"Arriba va el número sin coma y abajo {potencia}. Simplifica si se puede.",
                    "Arriba va el número sin coma. Simplifica si se puede.",
                ),
            ],
        )


class CompararDecimales(Ficha):
    id = "5B-OA11-comparar-decimales"
    unidad_id = "5B-OA11"

    def instanciar(self, nivel: int, azar: random.Random) -> EjercicioGenerado:
        # N1: décimos y centésimos · N2: milésimos · N3: ordenar cuatro decimales.
        if nivel == 3:
            return self._orden(azar)
        posiciones = (1, 2) if nivel == 1 else (2, 3)
        entero = 0 if nivel == 1 else azar.randint(0, 9)
        while True:
            a = Fraction(azar.randint(1, 10 ** posiciones[0] - 1), 10 ** posiciones[0]) + entero
            b = Fraction(azar.randint(1, 10 ** posiciones[1] - 1), 10 ** posiciones[1]) + entero
            cifras_b = decimal(b).split(",")
            if a != b and len(cifras_b) == 2 and len(cifras_b[1]) == posiciones[1]:
                break
        izquierda, derecha = (
            (decimal(a), decimal(b)) if azar.random() < 0.5 else (decimal(b), decimal(a))
        )
        va, vb = (a, b) if izquierda == decimal(a) else (b, a)
        return self._comparar(
            nivel,
            izquierda,
            derecha,
            (va, vb),
            [
                "Se compara la parte entera y después cada posición, de izquierda a derecha.",
                "Se pueden agregar ceros a la derecha para que tengan las mismas cifras.",
            ],
            "comparó mal las posiciones decimales",
            "Compara posición por posición, partiendo por los décimos.",
            [
                "Compara primero la parte entera.",
                "Después compara los décimos, luego los centésimos y luego los milésimos.",
                "Agrega ceros a la derecha para que los dos tengan las mismas cifras.",
            ],
        )

    def _orden(self, azar: random.Random) -> EjercicioGenerado:
        entero = azar.randint(0, 9)
        valores: dict[Fraction, str] = {}
        while len(valores) < 4:
            posiciones = azar.randint(1, 3)
            v = Fraction(azar.randint(1, 10**posiciones - 1), 10**posiciones) + entero
            valores[v] = decimal(v)
        # El error típico: ordenar la parte decimal como si fuera un número entero.
        como_entero = sorted(valores, key=lambda v: int(valores[v].split(",")[1]))
        ordenados = sorted(valores)
        confusion = None
        if como_entero != ordenados:
            confusion = (
                "; ".join(valores[v] for v in como_entero),
                "leyó la parte decimal como un número entero",
                "Más cifras no significa mayor: compara posición por posición.",
            )
        return self._ordenar(
            3,
            [(v, t) for v, t in valores.items()],
            azar,
            ["Se compara la parte entera y después cada posición, de izquierda a derecha."],
            "Fíjate bien: el primero tiene que ser el más pequeño.",
            [
                "Compara los décimos de todos los números.",
                "Si los décimos son iguales, compara los centésimos.",
                f"El menor de todos es {valores[ordenados[0]]}. Sigue con los demás.",
            ],
            confusion,
        )


class SumaRestaDecimales(Ficha):
    id = "5B-OA12-decimales"
    unidad_id = "5B-OA12"

    def instanciar(self, nivel: int, azar: random.Random) -> EjercicioGenerado:
        # N1: décimos · N2: hasta centésimos · N3: hasta milésimos, con distintas cifras.
        pos_a = nivel
        pos_b = 1 if nivel == 1 else azar.randint(1, nivel - 1)
        if azar.random() < 0.5:
            pos_a, pos_b = pos_b, pos_a
        a_raw, b_raw = self._sin_cero_final(azar, pos_a), self._sin_cero_final(azar, pos_b)
        a, b = Fraction(a_raw, 10**pos_a), Fraction(b_raw, 10**pos_b)
        suma = azar.random() < 0.5
        if not suma and a <= b:
            a, b, a_raw, b_raw, pos_a, pos_b = b, a, b_raw, a_raw, pos_b, pos_a
        signo = "+" if suma else "−"
        resultado = a + b if suma else a - b
        mayor = max(pos_a, pos_b)
        sin_alinear = Fraction(a_raw + b_raw if suma else abs(a_raw - b_raw), 10**mayor)
        opuesto = a - b if suma else a + b
        relleno_a = f"{int(a * 10**mayor):0{mayor + 1}d}"
        relleno_b = f"{int(b * 10**mayor):0{mayor + 1}d}"
        con_ceros_a = f"{relleno_a[:-mayor]},{relleno_a[-mayor:]}"
        con_ceros_b = f"{relleno_b[:-mayor]},{relleno_b[-mayor:]}"
        return self._crear(
            nivel,
            f"Calcula {decimal(a)} {signo} {decimal(b)}.",
            "numerico",
            decimal(resultado),
            [
                "Se escribe un número debajo del otro, con las comas alineadas.",
                f"{'Con ceros a la derecha queda' if pos_a != pos_b else 'Queda'} "
                f"{con_ceros_a} {signo} {con_ceros_b}.",
                f"{decimal(a)} {signo} {decimal(b)} = {decimal(resultado)}.",
            ],
            [
                (
                    decimal(sin_alinear),
                    "alineó las cifras por la derecha en vez de alinear las comas",
                    "Lo que se alinea son las comas: décimos con décimos.",
                ),
                (
                    decimal(opuesto),
                    "restó en vez de sumar" if suma else "sumó en vez de restar",
                    "Fíjate en el signo de la operación.",
                ),
            ],
            [
                "Escribe un número debajo del otro, con las comas alineadas.",
                "Si a un número le faltan cifras, agrega ceros a la derecha.",
                f"Queda {con_ceros_a} {signo} {con_ceros_b}. Opera como con números enteros.",
            ],
        )

    @staticmethod
    def _sin_cero_final(azar: random.Random, posiciones: int) -> int:
        """Número escalado cuya última cifra no es 0: 4,710 se escribiría 4,71."""
        while True:
            crudo = azar.randint(10**posiciones + 1, 10 ** (posiciones + 1) - 1)
            if crudo % 10:
                return crudo
