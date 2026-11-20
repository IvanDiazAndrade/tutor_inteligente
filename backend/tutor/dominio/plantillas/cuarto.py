"""Plantillas paramétricas de 4° básico (modelo_dominio.md §4).

Los niveles de las plantillas nuevas (4B-OA2, OA3, OA5 y OA6) son una propuesta para la ficha
de cada plantilla (tarea 57): se aprueban con la herramienta del revisor antes de servirse.
"""

import random

from tutor.dominio.plantillas.base import EjercicioGenerado, _errores, _sin_revelar, miles

UNIDADES, DECENAS, CENTENAS = 0, 1, 2
NOMBRES_COLUMNA = ("Unidades", "Decenas", "Centenas")
SINGULAR = ("unidad", "decena", "centena")
PLURAL = ("unidades", "decenas", "centenas")

COMPROBAR_DIVISION = (
    "Comprueba multiplicando: tu respuesta por el divisor tiene que dar el dividendo."
)


def _cifras(n: int) -> list[int]:
    """Cifras de n desde las unidades: 634 -> [4, 3, 6]."""
    return [int(c) for c in reversed(str(n))]


# 4B-OA2: cálculo mental de multiplicaciones hasta 10 × 10 y divisiones correspondientes ---


class CalculoMentalTablas:
    id = "4B-OA2-tablas"
    unidad_id = "4B-OA2"
    version = 1
    TABLAS_FACILES = (2, 5, 10)
    TABLAS_DIFICILES = (3, 4, 6, 7, 8, 9)

    def instanciar(self, nivel: int, azar: random.Random) -> EjercicioGenerado:
        # N1: multiplicar por 2, 5 o 10 · N2: multiplicar por cualquier tabla, o dividir por
        # 2, 5 o 10 · N3: dividir por 3, 4, 6, 7, 8 o 9.
        if nivel == 1:
            divide, tabla = False, azar.choice(self.TABLAS_FACILES)
        elif nivel == 2:
            divide = azar.random() < 0.5
            tabla = azar.choice(self.TABLAS_FACILES) if divide else azar.randint(2, 10)
        else:
            divide, tabla = True, azar.choice(self.TABLAS_DIFICILES)
        otro = azar.randint(2, 10)
        producto = tabla * otro
        if divide:
            return self._division(nivel, tabla, otro, producto)
        return self._multiplicacion(nivel, tabla, otro, producto)

    def _multiplicacion(self, nivel: int, tabla: int, otro: int, producto: int):
        respuesta = str(producto)
        # Estrategias del OA: doblar, agregar un cero, mitad de por 10, doble del doble, contar.
        if tabla == 2:
            estrategia = "Multiplicar por 2 es calcular el doble."
            paso = f"El doble de {otro} es {otro} + {otro} = {producto}."
            pista_final = f"Suma {otro} + {otro}."
        elif tabla == 10:
            estrategia = "Multiplicar por 10 es agregar un cero a la derecha del número."
            paso = f"A {otro} se le agrega un cero: {producto}."
            pista_final = f"Escribe {otro} y agrégale un cero a la derecha."
        elif tabla == 5:
            estrategia = "Multiplicar por 5 es la mitad de multiplicar por 10."
            paso = f"{otro} × 10 = {otro * 10}, y la mitad de {otro * 10} es {producto}."
            pista_final = f"{otro} × 10 = {otro * 10}. Ahora calcula la mitad de {otro * 10}."
        elif tabla == 4:
            estrategia = "Multiplicar por 4 es calcular el doble del doble."
            paso = f"El doble de {otro} es {otro * 2}, y el doble de {otro * 2} es {producto}."
            pista_final = f"El doble de {otro} es {otro * 2}. Ahora calcula el doble de {otro * 2}."
        else:
            estrategia = (
                f"Multiplicar es sumar el mismo número varias veces: cuenta de {tabla} en {tabla}."
            )
            anterior = tabla * (otro - 1)
            paso = f"{tabla} × {otro - 1} = {anterior}, y {anterior} + {tabla} = {producto}."
            pista_final = f"{tabla} × {otro - 1} = {tabla * (otro - 1)}. Súmale {tabla} más."
        return EjercicioGenerado(
            unidad_id=self.unidad_id,
            plantilla_id=self.id,
            nivel=nivel,
            enunciado=f"Calcula {otro} × {tabla}.",
            formato_respuesta="numerico",
            respuesta_final=respuesta,
            solucion_referencia=[
                f"Es la tabla del {tabla}. {estrategia}",
                paso,
                f"Entonces {otro} × {tabla} = {producto}.",
            ],
            errores_comunes=_errores(
                respuesta,
                [
                    (
                        str(otro + tabla),
                        "sumó en vez de multiplicar",
                        "Fíjate en el signo: es una multiplicación, no una suma.",
                    ),
                    (
                        str(tabla * (otro - 1)),
                        "contó un salto de menos",
                        "Casi: te faltó contar una vez más en la tabla.",
                    ),
                    (
                        str(tabla * (otro + 1)),
                        "contó un salto de más",
                        "Casi: contaste una vez de más en la tabla.",
                    ),
                ],
            ),
            pistas=[
                _sin_revelar(f"Piensa en la tabla del {tabla}.", respuesta, "Piensa en la tabla."),
                _sin_revelar(estrategia, respuesta, "Usa una estrategia que conozcas."),
                _sin_revelar(pista_final, respuesta, "Ya casi: haz el último cálculo."),
            ],
        )

    def _division(self, nivel: int, tabla: int, cociente: int, dividendo: int):
        respuesta = str(cociente)
        return EjercicioGenerado(
            unidad_id=self.unidad_id,
            plantilla_id=self.id,
            nivel=nivel,
            enunciado=f"Calcula {dividendo} : {tabla}.",
            formato_respuesta="numerico",
            respuesta_final=respuesta,
            solucion_referencia=[
                f"Dividir por {tabla} es buscar qué número multiplicado por {tabla} "
                f"da {dividendo}.",
                f"En la tabla del {tabla}: {cociente} × {tabla} = {dividendo}.",
                f"Entonces {dividendo} : {tabla} = {cociente}.",
            ],
            errores_comunes=_errores(
                respuesta,
                [
                    (str(cociente + 1), "se pasó en la tabla", COMPROBAR_DIVISION),
                    (str(cociente - 1), "se quedó corto en la tabla", COMPROBAR_DIVISION),
                    (
                        str(dividendo - tabla),
                        "restó en vez de dividir",
                        "Fíjate en el signo: es una división, no una resta.",
                    ),
                ],
            ),
            pistas=[
                _sin_revelar(
                    f"Dividir es lo contrario de multiplicar. Piensa en la tabla del {tabla}.",
                    respuesta,
                    "Dividir es lo contrario de multiplicar. Piensa en la tabla del divisor.",
                ),
                _sin_revelar(
                    f"Busca qué número multiplicado por {tabla} da {dividendo}.",
                    respuesta,
                    "Busca qué número multiplicado por el divisor da el dividendo.",
                ),
                _sin_revelar(
                    f"{cociente - 1} × {tabla} = {tabla * (cociente - 1)}: "
                    f"todavía no llegas a {dividendo}. Prueba con el número siguiente.",
                    respuesta,
                    f"Recorre la tabla del divisor hasta llegar a {dividendo}.",
                ),
            ],
        )


# 4B-OA3: adición y sustracción hasta 1 000 -------------------------------------------------


def _suma_columnas(sumandos: list[int]) -> tuple[list[str], list[int], int]:
    """Algoritmo de la suma en columnas. Devuelve los pasos, las cifras del resultado (desde
    las unidades) y cuántas reservas hubo."""
    total = sum(sumandos)
    pasos: list[str] = []
    cifras: list[int] = []
    reserva = reservas = 0
    for columna in range(len(str(total))):
        digitos = [_cifras(s)[columna] for s in sumandos if len(str(s)) > columna]
        terminos = ([f"{reserva} de reserva"] if reserva else []) + [str(d) for d in digitos]
        suma = reserva + sum(digitos)
        nombre = NOMBRES_COLUMNA[columna]
        if not digitos:
            pasos.append(f"{nombre}: se escribe la reserva, {reserva}.")
        elif suma >= 10:
            pasos.append(
                f"{nombre}: {' + '.join(terminos)} = {suma}. "
                f"Se escribe {suma % 10} y se reserva {suma // 10}."
            )
        else:
            pasos.append(f"{nombre}: {' + '.join(terminos)} = {suma}. Se escribe {suma}.")
        cifras.append(suma % 10)
        reservas += suma >= 10
        reserva = suma // 10
    return pasos, cifras, reservas


def _resta_columnas(minuendo: int, sustraendo: int) -> tuple[list[str], list[int], int, bool]:
    """Algoritmo de la resta con canje. Devuelve los pasos, las cifras del resultado (desde
    las unidades), cuántos canjes hubo y si alguno tuvo que pasar por un cero."""
    arriba = _cifras(minuendo)
    abajo = _cifras(sustraendo) + [0] * (len(arriba) - len(str(sustraendo)))
    pasos: list[str] = []
    cifras: list[int] = []
    canjes, por_cero = 0, False
    for col in range(len(arriba)):
        nombre = NOMBRES_COLUMNA[col]
        if arriba[col] < abajo[col]:
            antes = arriba[col]
            prestador = col + 1
            while arriba[prestador] == 0:
                prestador += 1
            if prestador == col + 1:
                canje = f"se canjea 1 {SINGULAR[col + 1]} por 10 {PLURAL[col]}"
            else:
                por_cero = True
                canje = (
                    f"como no hay {PLURAL[col + 1]}, se canjea 1 {SINGULAR[prestador]} "
                    f"por 10 {PLURAL[prestador - 1]} y luego 1 {SINGULAR[col + 1]} "
                    f"por 10 {PLURAL[col]}"
                )
            for k in range(prestador, col, -1):
                arriba[k] -= 1
                arriba[k - 1] += 10
            canjes += 1
            pasos.append(
                f"{nombre}: {antes} es menor que {abajo[col]}. {canje[0].upper()}{canje[1:]}: "
                f"{arriba[col]} − {abajo[col]} = {arriba[col] - abajo[col]}."
            )
        else:
            pasos.append(f"{nombre}: {arriba[col]} − {abajo[col]} = {arriba[col] - abajo[col]}.")
        cifras.append(arriba[col] - abajo[col])
    return pasos, cifras, canjes, por_cero


def _sin_reserva(sumandos: list[int]) -> int:
    """Error "olvidó la reserva": cada columna se suma y se escribe solo su última cifra."""
    columnas = max(len(str(s)) for s in sumandos)
    return sum(
        (sum(_cifras(s)[c] for s in sumandos if len(str(s)) > c) % 10) * 10**c
        for c in range(columnas)
    )


def _reserva_completa(sumandos: list[int]) -> int:
    """Error "escribió la suma de cada columna completa": 48 + 37 -> 7 | 15 -> 715."""
    columnas = max(len(str(s)) for s in sumandos)
    partes = [
        str(sum(_cifras(s)[c] for s in sumandos if len(str(s)) > c))
        for c in reversed(range(columnas))
    ]
    return int("".join(partes))


def _menor_del_mayor(minuendo: int, sustraendo: int) -> int:
    """Error clásico de la resta: en cada columna resta la cifra menor de la mayor."""
    arriba = _cifras(minuendo)
    abajo = _cifras(sustraendo) + [0] * (len(arriba) - len(str(sustraendo)))
    return sum(abs(a - b) * 10**c for c, (a, b) in enumerate(zip(arriba, abajo, strict=True)))


def _canje_sin_descontar(minuendo: int, sustraendo: int) -> int:
    """Error: canjea para poder restar, pero no descuenta lo canjeado de la columna siguiente."""
    arriba = _cifras(minuendo)
    abajo = _cifras(sustraendo) + [0] * (len(arriba) - len(str(sustraendo)))
    return sum(
        ((a + 10 if a < b else a) - b) * 10**c
        for c, (a, b) in enumerate(zip(arriba, abajo, strict=True))
    )


class SumaRestaHasta1000:
    id = "4B-OA3-suma-resta"
    unidad_id = "4B-OA3"
    version = 1

    def instanciar(self, nivel: int, azar: random.Random) -> EjercicioGenerado:
        # N1: dos números de 3 cifras, sin reserva ni canje · N2: con reserva o canje ·
        # N3: suma de 3 o 4 sumandos con al menos dos reservas, o resta con dos canjes o con
        # un canje que pasa por un cero. Resultados entre 100 y 999.
        if azar.random() < 0.5:
            return self._suma(nivel, azar)
        return self._resta(nivel, azar)

    def _suma(self, nivel: int, azar: random.Random) -> EjercicioGenerado:
        while True:
            if nivel < 3:
                sumandos = [azar.randint(100, 899), azar.randint(10 if nivel == 2 else 100, 899)]
            else:
                sumandos = [azar.randint(100, 499)] + [
                    azar.randint(5, 299) for _ in range(azar.choice((2, 3)))
                ]
            total = sum(sumandos)
            if not 100 <= total <= 999:
                continue
            pasos, cifras, reservas = _suma_columnas(sumandos)
            if (nivel == 1 and reservas == 0) or (nivel == 2 and reservas >= 1):
                break
            if nivel == 3 and reservas >= 2:
                break
        respuesta = str(total)
        operacion = " + ".join(str(s) for s in sumandos)
        candidatos = [
            (
                str(_sin_reserva(sumandos)),
                "olvidó la reserva",
                "Revisa las reservas: cuando una columna suma 10 o más, "
                "se reserva para la columna siguiente.",
            ),
            (
                str(_reserva_completa(sumandos)),
                "escribió la suma de cada columna completa",
                "En cada columna se escribe una sola cifra; lo demás se reserva.",
            ),
        ]
        if len(sumandos) == 2:
            candidatos.append(
                (
                    str(abs(sumandos[0] - sumandos[1])),
                    "restó en vez de sumar",
                    "Fíjate en el signo: aquí hay que sumar.",
                )
            )
        return EjercicioGenerado(
            unidad_id=self.unidad_id,
            plantilla_id=self.id,
            nivel=nivel,
            enunciado=f"Calcula {operacion}.",
            formato_respuesta="numerico",
            respuesta_final=respuesta,
            solucion_referencia=[*pasos, f"El resultado es {total}."],
            errores_comunes=_errores(respuesta, candidatos),
            pistas=[
                "Escribe los números uno debajo del otro: unidades con unidades, "
                "decenas con decenas y centenas con centenas.",
                _sin_revelar(pasos[0], respuesta, "Empieza sumando la columna de las unidades."),
                _sin_revelar(
                    f"Las unidades del resultado son {cifras[UNIDADES]} y las decenas son "
                    f"{cifras[DECENAS]}. Ahora suma las centenas.",
                    respuesta,
                    "Ya tienes las unidades y las decenas. Ahora suma las centenas.",
                ),
            ],
        )

    def _resta(self, nivel: int, azar: random.Random) -> EjercicioGenerado:
        while True:
            minuendo = azar.randint(200, 999)
            sustraendo = azar.randint(10 if nivel > 1 else 100, minuendo - 100)
            if nivel == 3 and azar.random() < 0.5:
                minuendo = minuendo // 100 * 100 + minuendo % 10  # un cero en las decenas
                if minuendo - sustraendo < 100:
                    continue
            pasos, cifras, canjes, por_cero = _resta_columnas(minuendo, sustraendo)
            if (nivel == 1 and canjes == 0) or (nivel == 2 and canjes == 1 and not por_cero):
                break
            if nivel == 3 and (canjes >= 2 or por_cero):
                break
        resultado = minuendo - sustraendo
        respuesta = str(resultado)
        return EjercicioGenerado(
            unidad_id=self.unidad_id,
            plantilla_id=self.id,
            nivel=nivel,
            enunciado=f"Calcula {minuendo} − {sustraendo}.",
            formato_respuesta="numerico",
            respuesta_final=respuesta,
            solucion_referencia=[*pasos, f"El resultado es {resultado}."],
            errores_comunes=_errores(
                respuesta,
                [
                    (
                        str(_menor_del_mayor(minuendo, sustraendo)),
                        "restó la cifra menor de la mayor en cada columna",
                        "Siempre se resta la cifra de abajo a la de arriba. "
                        "Si arriba hay menos, hay que canjear.",
                    ),
                    (
                        str(_canje_sin_descontar(minuendo, sustraendo)),
                        "canjeó sin descontar",
                        "Cuando canjeas, la columna que presta queda con 1 menos.",
                    ),
                    (
                        str(minuendo + sustraendo),
                        "sumó en vez de restar",
                        "Fíjate en el signo: aquí hay que restar.",
                    ),
                ],
            ),
            pistas=[
                "Escribe el número mayor arriba y resta columna por columna, empezando por "
                "las unidades. Si arriba hay menos que abajo, canjea.",
                _sin_revelar(pasos[0], respuesta, "Empieza restando la columna de las unidades."),
                _sin_revelar(
                    f"Las unidades del resultado son {cifras[UNIDADES]} y las decenas son "
                    f"{cifras[DECENAS]}. Ahora resta las centenas.",
                    respuesta,
                    "Ya tienes las unidades y las decenas. Ahora resta las centenas.",
                ),
            ],
        )


# 4B-OA5: multiplicación de 3 cifras por 1 cifra ----------------------------------------


class Multiplicacion3x1:
    id = "4B-OA5-mult-3x1"
    unidad_id = "4B-OA5"
    version = 1

    def instanciar(self, nivel: int, azar: random.Random) -> EjercicioGenerado:
        # N1: sin reserva (cada cifra por el factor da menos de 10) · N2: con reserva ·
        # N3: con reserva en dos o más posiciones, o con un cero en las decenas.
        while True:
            factor = azar.randint(2, 4) if nivel == 1 else azar.randint(3, 9)
            numero = azar.randint(101, 999)
            if numero % 100 == 0:
                continue  # 400 × 6 no tiene nada que descomponer
            cifras = _cifras(numero)
            reservas = _reservas_multiplicacion(numero, factor)
            if nivel == 1 and reservas == 0:
                break
            if nivel == 2 and reservas == 1:
                break
            if nivel == 3 and reservas >= 1 and (reservas >= 2 or cifras[DECENAS] == 0):
                break
        producto = numero * factor
        respuesta = str(producto)
        partes = [c * 10**i for i, c in reversed(list(enumerate(cifras))) if c]
        parciales = [p * factor for p in partes]
        descomposicion = " + ".join(miles(p) for p in partes)
        productos = [f"{miles(p)} × {factor} = {miles(p * factor)}" for p in partes]
        return EjercicioGenerado(
            unidad_id=self.unidad_id,
            plantilla_id=self.id,
            nivel=nivel,
            enunciado=f"Calcula {numero} × {factor}.",
            formato_respuesta="numerico",
            respuesta_final=respuesta,
            solucion_referencia=[
                f"Se descompone {numero} en {descomposicion}.",
                *[f"{p}." for p in productos],
                f"Se suman los resultados: {' + '.join(miles(p) for p in parciales)} "
                f"= {miles(producto)}.",
            ],
            errores_comunes=_errores(
                respuesta,
                [
                    (
                        str(
                            cifras[CENTENAS] * factor * 100
                            + (cifras[DECENAS] * factor % 10) * 10
                            + cifras[UNIDADES] * factor % 10
                        ),
                        "olvidó la reserva",
                        "Revisa las reservas: si una cifra por el factor da 10 o más, "
                        "se reserva para la posición siguiente.",
                    ),
                    (
                        str(
                            cifras[CENTENAS] * 100
                            + (cifras[DECENAS] * 10 + cifras[UNIDADES]) * factor
                        ),
                        "no multiplicó las centenas",
                        "Todas las cifras del número se multiplican por el factor, "
                        "también las centenas.",
                    ),
                    (
                        str(numero + factor),
                        "sumó en vez de multiplicar",
                        "Fíjate en el signo: es una multiplicación, no una suma.",
                    ),
                ],
            ),
            pistas=[
                "Descompón el número de tres cifras en centenas, decenas y unidades, "
                "y multiplica cada parte por el factor.",
                _sin_revelar(
                    f"Descompón {numero} en {descomposicion}.",
                    respuesta,
                    "Descompón el número en centenas, decenas y unidades.",
                ),
                _sin_revelar(
                    f"{', '.join(productos[:-1])} y {productos[-1]}. Ahora súmalos.",
                    respuesta,
                    "Multiplica cada parte por el factor y suma los resultados.",
                ),
            ],
        )


def _reservas_multiplicacion(numero: int, factor: int) -> int:
    """Cuántas posiciones dejan reserva en el algoritmo de la multiplicación."""
    reservas = reserva = 0
    for cifra in _cifras(numero)[:-1]:  # la última posición escribe todo, sin reservar
        producto = cifra * factor + reserva
        reserva = producto // 10
        reservas += reserva > 0
    return reservas


# 4B-OA6: división de 2 cifras por 1 cifra ------------------------------------------------


class Division2x1:
    id = "4B-OA6-div-2d"
    unidad_id = "4B-OA6"
    version = 1

    def instanciar(self, nivel: int, azar: random.Random) -> EjercicioGenerado:
        # N1: dentro de las tablas (cociente hasta 10, divisor 2-5) · N2: cociente mayor que
        # 10 y divisor 2-5, por descomposición · N3: cociente mayor que 10 con divisor 6-9, o la
        # misma división planteada como multiplicación con un factor desconocido.
        inversa = False
        while True:
            if nivel == 1:
                divisor, cociente = azar.randint(2, 5), azar.randint(2, 10)
            elif nivel == 2 or (inversa := azar.random() < 0.5):
                divisor, cociente = azar.randint(2, 5), azar.randint(11, 49)
            else:
                divisor, cociente = azar.randint(6, 9), azar.randint(11, 16)
            dividendo = divisor * cociente
            if 10 <= dividendo <= 99 and (nivel == 1 or cociente % 10):
                break
        respuesta = str(cociente)
        if inversa:
            enunciado = f"¿Por qué número hay que multiplicar {divisor} para obtener {dividendo}?"
        else:
            enunciado = f"Calcula {dividendo} : {divisor}."

        errores = [
            (str(cociente + 1), "se pasó en la cuenta", COMPROBAR_DIVISION),
            (str(cociente - 1), "se quedó corto en la cuenta", COMPROBAR_DIVISION),
            (
                str(dividendo - divisor),
                "restó en vez de dividir",
                "Aquí hay que repartir en partes iguales: es una división, no una resta.",
            ),
        ]
        if nivel == 1:
            solucion = [
                f"Piensa en la tabla del {divisor}.",
                f"{cociente} × {divisor} = {dividendo}.",
                f"Entonces {dividendo} : {divisor} = {cociente}.",
            ]
            pistas = [
                _sin_revelar(
                    f"Dividir es lo contrario de multiplicar. Piensa en la tabla del {divisor}.",
                    respuesta,
                    "Dividir es lo contrario de multiplicar. Piensa en la tabla del divisor.",
                ),
                _sin_revelar(
                    f"Busca qué número multiplicado por {divisor} da {dividendo}.",
                    respuesta,
                    "Busca qué número multiplicado por el divisor da el dividendo.",
                ),
                _sin_revelar(
                    f"{cociente - 1} × {divisor} = {divisor * (cociente - 1)}: todavía no "
                    f"llegas a {dividendo}. Prueba con el número siguiente.",
                    respuesta,
                    f"Recorre la tabla del divisor hasta llegar a {dividendo}.",
                ),
            ]
        else:
            grande = dividendo // (10 * divisor) * 10 * divisor  # múltiplo de 10 × divisor
            resto = dividendo - grande
            q1, q2 = grande // divisor, resto // divisor
            solucion = [
                f"Se descompone {dividendo} en {grande} + {resto}, dos números fáciles de "
                f"dividir por {divisor}.",
                f"{grande} : {divisor} = {q1}.",
                f"{resto} : {divisor} = {q2}.",
                f"{q1} + {q2} = {cociente}. Entonces {dividendo} : {divisor} = {cociente}.",
            ]
            errores.append(
                (
                    str(q1 + resto),
                    "dividió solo una de las partes",
                    "Las dos partes del número se dividen por el divisor antes de sumarlas.",
                )
            )
            primera = (
                f"Esta pregunta es una división: {dividendo} : {divisor}. " if inversa else ""
            ) + f"Descompón {dividendo} en dos partes fáciles de dividir por {divisor}."
            pistas = [
                _sin_revelar(
                    primera,
                    respuesta,
                    "Descompón el dividendo en dos partes fáciles de dividir por el divisor.",
                ),
                _sin_revelar(
                    f"Descompón {dividendo} en {grande} + {resto}.",
                    respuesta,
                    "Separa el dividendo en decenas fáciles de dividir y lo que queda.",
                ),
                _sin_revelar(
                    f"{grande} : {divisor} = {q1} y {resto} : {divisor} = {q2}. Ahora súmalos.",
                    respuesta,
                    "Divide cada parte por el divisor y suma los resultados.",
                ),
            ]
        return EjercicioGenerado(
            unidad_id=self.unidad_id,
            plantilla_id=self.id,
            nivel=nivel,
            enunciado=enunciado,
            formato_respuesta="numerico",
            respuesta_final=respuesta,
            solucion_referencia=solucion,
            errores_comunes=_errores(respuesta, errores),
            pistas=pistas,
        )


# 4B-OA9: suma y resta de fracciones con igual denominador (§4.2) ------------------------


class SumaIgualDenominador:
    id = "4B-OA9-suma-igual-den"
    unidad_id = "4B-OA9"
    version = 1
    DENOMINADORES = [2, 3, 4, 5, 6, 8, 10, 12]

    def instanciar(self, nivel: int, azar: random.Random) -> EjercicioGenerado:
        # N1: d ≤ 4, siempre pictórico · N2: cualquier d, pictórico la mitad de las veces ·
        # N3: resta, o suma cuyo resultado es 1.
        # En N1 y N2 el resultado es propio (a + b < d), así que d = 2 no sirve: 1/2 + 1/2 = 1.
        opciones = [d for d in self.DENOMINADORES if d >= 3 and (nivel != 1 or d <= 4)]
        d = azar.choice(opciones if nivel < 3 else self.DENOMINADORES)
        resta = nivel == 3 and azar.random() < 0.5
        if resta:
            a = azar.randint(2, d)
            b = azar.randint(1, a - 1)
            resultado = a - b
        elif nivel == 3:
            a = azar.randint(1, d - 1)
            b = d - a
            resultado = d
        else:
            a = azar.randint(1, d - 2)
            b = azar.randint(1, d - a - 1)
            resultado = a + b

        signo = "−" if resta else "+"
        respuesta = f"{resultado}/{d}"
        operacion = "Se restan" if resta else "Se suman"
        solucion = [
            f"Los denominadores ya son iguales ({d}), así que no hay que cambiarlos.",
            f"{operacion} solo los numeradores: {a} {signo} {b} = {resultado}.",
            f"El resultado es {respuesta}.",
        ]
        if resta:
            candidatos = [
                (
                    f"{a + b}/{d}",
                    "sumó en vez de restar",
                    "Fíjate en el signo: aquí hay que restar.",
                ),
            ]
        else:
            candidatos = [
                (
                    f"{a + b}/{2 * d}",
                    "sumó también los denominadores",
                    "Cuando los denominadores son iguales, se mantienen: "
                    "solo se suman los numeradores.",
                ),
                (
                    str(a + b),
                    "ignoró el denominador",
                    "El resultado es una fracción: no olvides el número de abajo.",
                ),
                (
                    f"{a * b}/{d}",
                    "multiplicó los numeradores",
                    "Es una suma: los numeradores se suman, no se multiplican.",
                ),
            ]

        pictorico = not resta and (nivel == 1 or nivel == 3 or azar.random() < 0.5)
        return EjercicioGenerado(
            unidad_id=self.unidad_id,
            plantilla_id=self.id,
            nivel=nivel,
            enunciado=f"Calcula {a}/{d} {signo} {b}/{d}.",
            formato_respuesta="fraccion",
            respuesta_final=respuesta,
            solucion_referencia=solucion,
            errores_comunes=_errores(respuesta, candidatos),
            pistas=[
                "Mira los números de abajo. ¿Qué tienen en común?",
                "Si los denominadores son iguales, el denominador del resultado es el mismo.",
                f"{'Resta' if resta else 'Suma'} solo los numeradores: {a} {signo} {b}. "
                f"El denominador sigue siendo {d}.",
            ],
            representacion=(
                {
                    "tipo": "fraccion-circulo",
                    "parametros": {"denominador": d, "partesDestacadas": [a, b]},
                }
                if pictorico
                else None
            ),
        )
