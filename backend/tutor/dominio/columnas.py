"""Suma y resta en columnas, escritas con caracteres, para las pistas (modelo_dominio.md §2).

Una pista puede llevar, después de su frase, un bloque con la operación como en el cuaderno:

    Unidades: 5 + 5 = 10. Escribe el 0 abajo y la reserva 1 pasa a las decenas.
        1
      1 2 5
    + 1 2 5
    ───────
          0

El bloque va separado de la frase por un salto de línea y siempre tiene la misma forma: una
línea de marcas (reservas o canjes, puede ir vacía), los números, la raya y el resultado. La app
lo muestra con letra de ancho fijo para que las columnas queden alineadas, y el LLM nunca lo
reescribe: solo reformula la frase (ver `separar_bloque`).

Cada pista resuelve más columnas (de derecha a izquierda), pero nunca todas: la columna de más
a la izquierda que tiene una cifra del resultado queda siempre sin resolver, así el bloque no
muestra la respuesta.
"""

import re
from dataclasses import dataclass

POSICIONES = ["unidades", "decenas", "centenas", "unidades de mil", "decenas de mil"]
RAYA = "─"


def separar_bloque(pista: str) -> tuple[str, str | None]:
    """("frase", "bloque") si la pista trae una operación en columnas; si no, (pista, None)."""
    frase, _, bloque = pista.partition("\n")
    return frase, (bloque or None)


def con_bloque(frase: str, bloque: str | None) -> str:
    return f"{frase}\n{bloque}" if bloque else frase


def _cifra(n: int, i: int) -> int:
    return n // 10**i % 10


def _largo(n: int) -> int:
    return len(str(n))


def columnas_visibles(resultado: int, pedidas: int) -> int:
    """Cuántas columnas se pueden mostrar resueltas sin dejar ver el resultado completo: hasta
    antes de su cifra de más a la izquierda."""
    return max(0, min(pedidas, _largo(resultado) - 1))


def _dibujar(
    columnas: int,
    ancho: int,
    marcas: dict[int, int],
    filas: list[tuple[str, int]],
    resultado: dict[int, int],
) -> str:
    """Arma el bloque. Las columnas se cuentan desde la derecha (0 = unidades); cada una ocupa
    `ancho` caracteres y la primera posición de cada fila es el signo."""

    def fila(signo: str, valores: dict[int, int]) -> str:
        return _fila(columnas, ancho, signo, valores)

    lineas = [fila(" ", marcas)]
    for signo, numero in filas:
        lineas.append(fila(signo, _cifras_de(numero)))
    lineas.append(RAYA * (1 + ancho * columnas))
    lineas.append(fila(" ", resultado))
    return "\n".join(lineas)


def _fila(columnas: int, ancho: int, signo: str, valores: dict[int, int]) -> str:
    celdas = (
        str(valores[i]).rjust(ancho) if i in valores else " " * ancho
        for i in reversed(range(columnas))
    )
    return (signo + "".join(celdas)).rstrip()


def _cifras_de(numero: int, corrido: int = 0) -> dict[int, int]:
    """{columna: cifra} de un número; `corrido` lo desplaza a la izquierda (columnas vacías)."""
    return {i + corrido: _cifra(numero, i) for i in range(_largo(numero))}


# Suma ------------------------------------------------------------------------------------


@dataclass(frozen=True)
class ColumnaSuma:
    posicion: int
    cifras: list[int]  # cifras de los sumandos en esta columna (sin los que no llegan)
    reserva_entrante: int
    total: int  # cifras + reserva entrante
    escribe: int
    reserva_saliente: int


def columnas_suma(sumandos: list[int]) -> list[ColumnaSuma]:
    largo = max(map(_largo, sumandos))
    reserva = 0
    resultado = []
    for i in range(largo):
        cifras = [_cifra(s, i) for s in sumandos if _largo(s) > i]
        total = sum(cifras) + reserva
        resultado.append(ColumnaSuma(i, cifras, reserva, total, total % 10, total // 10))
        reserva = total // 10
    return resultado


def suma_vertical(sumandos: list[int], resueltas: int) -> str:
    """Suma en columnas con las `resueltas` columnas de la derecha ya hechas (y sus reservas
    escritas arriba de la columna siguiente)."""
    total = sum(sumandos)
    resueltas = columnas_visibles(total, resueltas)
    pasos = columnas_suma(sumandos)
    marcas = {p.posicion + 1: p.reserva_saliente for p in pasos[:resueltas] if p.reserva_saliente}
    abajo = {p.posicion: p.escribe for p in pasos[:resueltas]}
    filas = [(" ", s) for s in sumandos[:-1]] + [("+", sumandos[-1])]
    return _dibujar(_largo(total), 2, marcas, filas, abajo)


def explicar_columna_suma(columna: ColumnaSuma) -> str:
    """Explica una columna: «Decenas: 4 + 7 + 1 de reserva = 12. Escribe el 2 abajo y la
    reserva 1 pasa a las centenas.»"""
    nombre = POSICIONES[columna.posicion]
    suma = " + ".join(map(str, columna.cifras))
    if columna.reserva_entrante:
        suma += f" + {columna.reserva_entrante} de reserva"
    texto = f"{nombre.capitalize()}: {suma} = {columna.total}. Escribe el {columna.escribe} abajo"
    if columna.reserva_saliente:
        siguiente = POSICIONES[columna.posicion + 1]
        return f"{texto} y la reserva {columna.reserva_saliente} pasa a las {siguiente}."
    return f"{texto}."


# Resta -----------------------------------------------------------------------------------


@dataclass(frozen=True)
class ColumnaResta:
    posicion: int
    arriba: int  # cifra de arriba antes de canjear (ya con los canjes de columnas anteriores)
    abajo: int
    presta: int | None  # columna que prestó 1 en el canje (None si no hubo canje)
    escribe: int


def _restar(minuendo: int, sustraendo: int, hasta: int) -> tuple[list[ColumnaResta], dict]:
    """Resuelve las primeras `hasta` columnas. Devuelve los pasos y las cifras de arriba que
    cambiaron por los canjes (para escribirlas sobre la original, como en el cuaderno)."""
    valores = {i: _cifra(minuendo, i) for i in range(_largo(minuendo))}
    cambiadas: dict[int, int] = {}
    pasos = []
    for i in range(hasta):
        arriba, abajo = valores[i], _cifra(sustraendo, i)
        presta = None
        if arriba < abajo:
            j = i + 1
            while valores[j] == 0:  # sobre ceros, el canje viene de más a la izquierda
                j += 1
            valores[j] -= 1
            cambiadas[j] = valores[j]
            for k in range(i + 1, j):
                valores[k] = 9
                cambiadas[k] = 9
            valores[i] += 10
            cambiadas[i] = valores[i]
            presta = j
        pasos.append(ColumnaResta(i, arriba, abajo, presta, valores[i] - abajo))
    return pasos, cambiadas


def columnas_resta(minuendo: int, sustraendo: int) -> list[ColumnaResta]:
    return _restar(minuendo, sustraendo, _largo(minuendo))[0]


def resta_vertical(minuendo: int, sustraendo: int, resueltas: int) -> str:
    """Resta en columnas con las `resueltas` columnas de la derecha ya hechas. Arriba quedan
    escritos los canjes: la cifra que prestó, con 1 menos, y la que recibió, con 10 más."""
    resueltas = columnas_visibles(minuendo - sustraendo, resueltas)
    pasos, cambiadas = _restar(minuendo, sustraendo, resueltas)
    abajo = {p.posicion: p.escribe for p in pasos}
    filas = [(" ", minuendo), ("−", sustraendo)]
    return _dibujar(_largo(minuendo), 3, cambiadas, filas, abajo)


def explicar_columna_resta(columna: ColumnaResta) -> str:
    """Explica una columna: «Unidades: a 2 no se le puede restar 7. Pides 1 a las decenas y el 2
    se convierte en 12. 12 − 7 = 5.» Si en medio hay ceros, dice de qué columna viene el canje."""
    nombre = POSICIONES[columna.posicion].capitalize()
    if columna.presta is None:
        return f"{nombre}: {columna.arriba} − {columna.abajo} = {columna.escribe}."
    origen = POSICIONES[columna.presta]
    ceros = " y las ".join(POSICIONES[i] for i in range(columna.posicion + 1, columna.presta))
    pide = (
        f"Como las {ceros} tienen 0, pides 1 a las {origen}" if ceros else f"Pides 1 a las {origen}"
    )
    nuevo = columna.arriba + 10
    return (
        f"{nombre}: a {columna.arriba} no se le puede restar {columna.abajo}. {pide} y "
        f"el {columna.arriba} se convierte en {nuevo}. {nuevo} − {columna.abajo} = "
        f"{columna.escribe}."
    )


# Pistas completas (las tres de un ejercicio) ----------------------------------------------
#
# Pista 1 = estrategia (la operación ordenada en columnas), 2 = primer paso (las unidades),
# 3 = a un paso del final (todo resuelto salvo la última columna). Si el resultado es tan corto
# que mostrar una columna lo dejaría ver, la pista se queda en la estrategia.


def pistas_suma(sumandos: list[int]) -> list[str]:
    total = sum(sumandos)
    pasos = columnas_suma(sumandos)
    hasta = columnas_visibles(total, max(map(_largo, sumandos)) - 1)
    primera = con_bloque(
        "Escribe los números uno debajo del otro, con las unidades en la misma columna. Se suma "
        "de derecha a izquierda, empezando por las unidades.",
        suma_vertical(sumandos, 0),
    )
    if hasta == 0:
        return [primera, primera, primera]
    segunda = con_bloque(explicar_columna_suma(pasos[0]), suma_vertical(sumandos, 1))
    if hasta == 1:
        reserva = pasos[0].reserva_saliente
        frase = "Ahora suma la columna de las decenas" + (
            f", sin olvidar la reserva {reserva}." if reserva else "."
        )
    else:
        frase = (
            f"{explicar_columna_suma(pasos[hasta - 1])} Te queda la columna de las "
            f"{POSICIONES[hasta]}."
        )
    return [primera, segunda, con_bloque(frase, suma_vertical(sumandos, hasta))]


def pistas_resta(minuendo: int, sustraendo: int) -> list[str]:
    pasos = columnas_resta(minuendo, sustraendo)
    hasta = columnas_visibles(minuendo - sustraendo, _largo(minuendo) - 1)
    primera = con_bloque(
        "Escribe el número mayor arriba y el menor abajo, con las unidades en la misma columna. "
        "Se resta de derecha a izquierda; si la cifra de arriba es menor, le pides a la columna "
        "de la izquierda (canje).",
        resta_vertical(minuendo, sustraendo, 0),
    )
    if hasta == 0:
        return [primera, primera, primera]
    segunda = con_bloque(explicar_columna_resta(pasos[0]), resta_vertical(minuendo, sustraendo, 1))
    if hasta == 1:
        frase = (
            "Ahora resta la columna de las decenas. Antes, fíjate si a la cifra de arriba se le "
            "puede restar la de abajo."
        )
    else:
        frase = (
            f"{explicar_columna_resta(pasos[hasta - 1])} Te queda la columna de las "
            f"{POSICIONES[hasta]}."
        )
    return [primera, segunda, con_bloque(frase, resta_vertical(minuendo, sustraendo, hasta))]


# División (algoritmo completo, como se escribe en Chile) -----------------------------------
#
#     9 7 5 : 3 = 3 2
#   − 9
#   ───
#     0 7
#   − 6
#   ───
#     1 5
#
# Dividendo : divisor = cociente en la primera línea; debajo de cada cifra, el producto que se
# resta, la raya y el resto con la cifra que se baja. Cada pista resuelve más cifras del
# cociente, nunca la última (ni el resto final).


@dataclass(frozen=True)
class PasoDivision:
    fin: int  # índice (desde la izquierda) de la última cifra del dividendo que se usó
    parcial: int  # el número que se divide en este paso
    cifra: int  # cifra del cociente
    producto: int
    resto: int


def pasos_division(dividendo: int, divisor: int) -> list[PasoDivision]:
    cifras = str(dividendo)
    i, parcial = 0, int(cifras[0])
    while parcial < divisor and i < len(cifras) - 1:  # si la primera cifra no alcanza, se toman dos
        i += 1
        parcial = parcial * 10 + int(cifras[i])
    pasos = []
    while True:
        cifra = parcial // divisor
        producto = cifra * divisor
        pasos.append(PasoDivision(i, parcial, cifra, producto, parcial - producto))
        if i == len(cifras) - 1:
            return pasos
        i += 1
        parcial = (parcial - producto) * 10 + int(cifras[i])


def _x(i: int) -> int:
    """Posición (en caracteres) de la cifra i del dividendo: deja 2 espacios para el signo."""
    return 2 + 2 * i


def _numero_hasta(texto: str, fin: int) -> str:
    """Las cifras de `texto` separadas por espacios, con la última bajo la cifra `fin`."""
    return " " * (_x(fin) - 2 * (len(texto) - 1)) + " ".join(texto)


def division_vertical(dividendo: int, divisor: int, resueltas: int) -> str:
    pasos = pasos_division(dividendo, divisor)
    resueltas = max(0, min(resueltas, len(pasos) - 1))
    cociente = "".join(str(p.cifra) for p in pasos[:resueltas])
    lineas = [
        (_numero_hasta(str(dividendo), len(str(dividendo)) - 1) + f" : {divisor} = {cociente}")
    ]
    for j, paso in enumerate(pasos[:resueltas]):
        siguiente = pasos[j + 1]  # existe: nunca se resuelve el último paso
        if paso.cifra == 0 and j > 0:
            # No cabe: 0 en el cociente y se baja otra cifra junto al mismo número.
            lineas[-1] = _numero_hasta(str(siguiente.parcial), siguiente.fin)
            continue
        inicio = _x(paso.fin) - 2 * (len(str(paso.producto)) - 1)
        lineas.append(" " * (inicio - 2) + "− " + " ".join(str(paso.producto)))
        lineas.append(" " * (inicio - 2) + RAYA * (_x(paso.fin) - inicio + 3))
        lineas.append(_numero_hasta(f"{paso.resto}{str(dividendo)[siguiente.fin]}", siguiente.fin))
    return "\n".join(linea.rstrip() for linea in lineas)


def explicar_paso_division(dividendo: int, divisor: int, numero: int) -> str:
    """Explica el paso `numero` (0 = el primero) del algoritmo."""
    pasos = pasos_division(dividendo, divisor)
    paso = pasos[numero]
    cifras = str(dividendo)
    baja = f" Baja el {cifras[paso.fin + 1]}." if numero < len(pasos) - 1 else ""
    if paso.cifra == 0:
        return f"{paso.parcial} es menor que {divisor}: escribe 0 en el cociente.{baja}"
    antes = ""
    if numero == 0 and paso.fin > 0:
        antes = f"Como {cifras[: paso.fin]} es menor que {divisor}, tomas {paso.parcial}. "
    veces = "vez" if paso.cifra == 1 else "veces"
    return (
        f"{antes}El {divisor} cabe {paso.cifra} {veces} en {paso.parcial}: escribe el "
        f"{paso.cifra} en el cociente. Multiplica {paso.cifra} × {divisor} = {paso.producto} y "
        f"resta: {paso.parcial} − {paso.producto} = {paso.resto}.{baja}"
    )


def pistas_division(dividendo: int, divisor: int) -> list[str] | None:
    """Las tres pistas con la división escrita. None si el cociente tiene una sola cifra: ahí
    no hay pasos que mostrar sin dar la respuesta (sirve más la tabla del divisor)."""
    pasos = pasos_division(dividendo, divisor)
    if len(pasos) < 2:
        return None
    hasta = len(pasos) - 1
    primera = con_bloque(
        "Se divide de izquierda a derecha: en cada paso ves cuántas veces cabe el divisor, "
        "multiplicas, restas y bajas la cifra que sigue.",
        division_vertical(dividendo, divisor, 0),
    )
    segunda = con_bloque(
        explicar_paso_division(dividendo, divisor, 0), division_vertical(dividendo, divisor, 1)
    )
    ultimo = pasos[hasta].parcial
    if hasta == 1:
        frase = f"Ahora divide {ultimo} : {divisor}."
    else:
        frase = (
            f"{explicar_paso_division(dividendo, divisor, hasta - 1)} Te queda dividir "
            f"{ultimo} : {divisor}."
        )
    # Por casualidad un número del paso puede ser igual al cociente (53 : 4 = 13 y "divide
    # 13 : 4"): entonces la frase va sin números; el bloque igual muestra el paso.
    cociente = str(dividendo // divisor)
    if _nombra(segunda, cociente):
        segunda = con_bloque(
            "Mira cuántas veces cabe el divisor en las primeras cifras, multiplica y resta.",
            separar_bloque(segunda)[1],
        )
    if _nombra(frase, cociente):
        frase = "Ahora divide el número que quedó abajo."
    return [primera, segunda, con_bloque(frase, division_vertical(dividendo, divisor, hasta))]


def _nombra(texto: str, numero: str) -> bool:
    frase = separar_bloque(texto)[0]
    return re.search(rf"(?<![\d,.]){numero}(?![\d,.])", frase) is not None


# Multiplicación ---------------------------------------------------------------------------
#
# Por una cifra, como la suma: de derecha a izquierda, con las reservas arriba de la columna
# siguiente. Por dos cifras: primero por las unidades, después por las decenas en una fila
# corrida un lugar a la izquierda (con el lugar de las unidades vacío) y al final se suman las
# dos filas; la pista 3 deja las filas hechas y la suma por hacer.


@dataclass(frozen=True)
class ColumnaProducto:
    posicion: int
    cifra: int
    reserva_entrante: int
    total: int  # cifra × factor + reserva entrante
    escribe: int
    reserva_saliente: int


def columnas_producto(numero: int, factor: int) -> list[ColumnaProducto]:
    reserva = 0
    pasos = []
    for i in range(_largo(numero)):
        cifra = _cifra(numero, i)
        total = cifra * factor + reserva
        pasos.append(ColumnaProducto(i, cifra, reserva, total, total % 10, total // 10))
        reserva = total // 10
    return pasos


def producto_vertical(numero: int, factor: int, resueltas: int) -> str:
    """Multiplicación por una cifra con las `resueltas` columnas de la derecha ya hechas."""
    resultado = numero * factor
    resueltas = columnas_visibles(resultado, min(resueltas, _largo(numero) - 1))
    pasos = columnas_producto(numero, factor)
    marcas = {p.posicion + 1: p.reserva_saliente for p in pasos[:resueltas] if p.reserva_saliente}
    abajo = {p.posicion: p.escribe for p in pasos[:resueltas]}
    return _dibujar(_largo(resultado), 2, marcas, [(" ", numero), ("×", factor)], abajo)


def explicar_columna_producto(columna: ColumnaProducto, factor: int) -> str:
    """«Decenas: 3 × 4 = 12, más 1 de reserva = 13. Escribe el 3 abajo y la reserva 1 pasa a
    las centenas.»"""
    nombre = POSICIONES[columna.posicion].capitalize()
    cuenta = f"{columna.cifra} × {factor} = {columna.cifra * factor}"
    if columna.reserva_entrante:
        cuenta += f", más {columna.reserva_entrante} de reserva = {columna.total}"
    texto = f"{nombre}: {cuenta}. Escribe el {columna.escribe} abajo"
    if columna.reserva_saliente:
        siguiente = POSICIONES[columna.posicion + 1]
        return f"{texto} y la reserva {columna.reserva_saliente} pasa a las {siguiente}."
    return f"{texto}."


def pistas_producto(numero: int, factor: int) -> list[str]:
    """Las tres pistas de una multiplicación por una cifra."""
    pasos = columnas_producto(numero, factor)
    hasta = columnas_visibles(numero * factor, _largo(numero) - 1)
    primera = con_bloque(
        "Escribe el número arriba y el factor abajo, bajo las unidades. Se multiplica cada "
        "cifra de derecha a izquierda, empezando por las unidades.",
        producto_vertical(numero, factor, 0),
    )
    if hasta == 0:
        return [primera, primera, primera]
    segunda = con_bloque(
        explicar_columna_producto(pasos[0], factor), producto_vertical(numero, factor, 1)
    )
    if hasta == 1:
        reserva = pasos[0].reserva_saliente
        frase = "Ahora multiplica las decenas" + (
            f" y súmale la reserva {reserva}." if reserva else "."
        )
    else:
        frase = (
            f"{explicar_columna_producto(pasos[hasta - 1], factor)} Te quedan las "
            f"{POSICIONES[hasta]}."
        )
    return [primera, segunda, con_bloque(frase, producto_vertical(numero, factor, hasta))]


def producto_dos_cifras_vertical(numero: int, factor: int, filas_hechas: int) -> str:
    """`numero` × `factor` (de dos cifras) con 0, 1 o 2 filas hechas. Nunca la suma final."""
    unidades, decenas = factor % 10, factor // 10
    columnas = _largo(numero * factor)
    lineas = [
        "",  # sin reservas: en esta multiplicación se escriben solo las filas
        _fila(columnas, 2, " ", _cifras_de(numero)),
        _fila(columnas, 2, "×", _cifras_de(factor)),
        RAYA * (1 + 2 * columnas),
    ]
    if filas_hechas >= 1:
        lineas.append(_fila(columnas, 2, " ", _cifras_de(numero * unidades)))
    if filas_hechas >= 2:
        lineas.append(_fila(columnas, 2, "+", _cifras_de(numero * decenas, corrido=1)))
        lineas.append(RAYA * (1 + 2 * columnas))
        lineas.append("")  # aquí va la suma de las dos filas: la hace el niño
    return "\n".join(lineas)


def pistas_producto_dos_cifras(numero: int, factor: int) -> list[str]:
    """Las tres pistas de una multiplicación por un número de dos cifras (sin 0 en las unidades:
    para multiplicar por una decena exacta sirve más "multiplica y agrega un cero")."""
    unidades, decenas = factor % 10, factor // 10
    return [
        con_bloque(
            "Primero se multiplica por las unidades y después por las decenas, en una fila "
            "corrida un lugar a la izquierda. Al final se suman las dos filas.",
            producto_dos_cifras_vertical(numero, factor, 0),
        ),
        con_bloque(
            f"Primero por las unidades: {numero} × {unidades} = {numero * unidades}.",
            producto_dos_cifras_vertical(numero, factor, 1),
        ),
        con_bloque(
            f"Ahora por las decenas: {numero} × {decenas} = {numero * decenas}. Se escribe "
            "corrido un lugar a la izquierda, con el lugar de las unidades vacío. Te queda "
            "sumar las dos filas.",
            producto_dos_cifras_vertical(numero, factor, 2),
        ),
    ]
