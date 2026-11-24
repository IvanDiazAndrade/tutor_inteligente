"""Suma y resta en columnas para las pistas (tutor/dominio/columnas.py)."""

import random

import pytest

from tutor.dominio.columnas import (
    RAYA,
    columnas_resta,
    columnas_suma,
    con_bloque,
    division_vertical,
    pasos_division,
    pistas_division,
    pistas_producto,
    pistas_producto_dos_cifras,
    pistas_resta,
    pistas_suma,
    producto_dos_cifras_vertical,
    producto_vertical,
    resta_vertical,
    separar_bloque,
    suma_vertical,
)
from tutor.mensajes import revela


def test_suma_con_reserva_como_en_el_cuaderno():
    assert suma_vertical([125, 125], 1) == "\n".join(
        [
            "    1",
            "  1 2 5",
            "+ 1 2 5",
            "───────",
            "      0",
        ]
    )


def test_resta_con_canje_sobre_ceros():
    # 900 − 373: las decenas tienen 0, el canje viene de las centenas (9 → 8, 0 → 9, 0 → 10).
    assert resta_vertical(900, 373, 1) == "\n".join(
        [
            "   8  9 10",
            "   9  0  0",
            "−  3  7  3",
            "──────────",
            "         7",
        ]
    )
    assert [c.presta for c in columnas_resta(900, 373)] == [2, None, None]


def test_separar_y_juntar_el_bloque():
    bloque = suma_vertical([12, 9], 0)
    assert separar_bloque(con_bloque("Ordena en columnas.", bloque)) == (
        "Ordena en columnas.",
        bloque,
    )
    assert separar_bloque("Sin columnas.") == ("Sin columnas.", None)


def _lineas(bloque: str) -> tuple[str, list[str], str]:
    """Marcas, filas de números y resultado (las filas van entre las marcas y la raya)."""
    lineas = bloque.split("\n")
    raya = next(i for i, linea in enumerate(lineas) if linea.startswith(RAYA))
    return lineas[0], lineas[1:raya], lineas[raya + 1]


def _cifras_visibles(linea: str, ancho: int, columnas: int) -> dict[int, int]:
    """{columna: cifra} de una fila del bloque (columna 0 = unidades)."""
    linea = linea.ljust(1 + ancho * columnas)
    celdas = [linea[1 + ancho * k : 1 + ancho * (k + 1)] for k in range(columnas)]
    return {columnas - 1 - k: int(c) for k, c in enumerate(celdas) if c.strip()}


CASOS_SUMA = [
    [azar.randint(1, 999) for _ in range(azar.choice([2, 3, 4]))]
    for azar in [random.Random(semilla) for semilla in range(300)]
]
CASOS_RESTA = [
    tuple(sorted(random.Random(semilla).sample(range(1, 1000), 2), reverse=True))
    for semilla in range(300)
]


@pytest.mark.parametrize("sumandos", CASOS_SUMA)
def test_suma_vertical_cuadra_con_la_cuenta_y_no_muestra_el_total(sumandos):
    total = sum(sumandos)
    columnas = len(str(total))
    for resueltas in range(4):
        marcas, filas, abajo = _lineas(suma_vertical(sumandos, resueltas))
        # Los números quedan alineados por la derecha, en su columna.
        assert [
            sum(c * 10**i for i, c in _cifras_visibles(f, 2, columnas).items()) for f in filas
        ] == sumandos
        visibles = _cifras_visibles(abajo, 2, columnas)
        assert all(total // 10**i % 10 == c for i, c in visibles.items())
        assert len(visibles) < columnas  # nunca el resultado completo
        reservas = {p.posicion + 1: p.reserva_saliente for p in columnas_suma(sumandos)}
        assert all(reservas[i] == c for i, c in _cifras_visibles(marcas, 2, columnas).items())


@pytest.mark.parametrize(("minuendo", "sustraendo"), CASOS_RESTA)
def test_resta_vertical_cuadra_con_la_cuenta_y_no_muestra_el_resultado(minuendo, sustraendo):
    resultado = minuendo - sustraendo
    columnas = len(str(minuendo))
    for resueltas in range(4):
        _, filas, abajo = _lineas(resta_vertical(minuendo, sustraendo, resueltas))
        assert [
            sum(c * 10**i for i, c in _cifras_visibles(f, 3, columnas).items()) for f in filas
        ] == [minuendo, sustraendo]
        visibles = _cifras_visibles(abajo, 3, columnas)
        assert all(resultado // 10**i % 10 == c for i, c in visibles.items())
        assert len(visibles) < len(str(resultado)) or not visibles


@pytest.mark.parametrize(("minuendo", "sustraendo"), CASOS_RESTA)
def test_los_canjes_dejan_cifras_que_se_pueden_restar(minuendo, sustraendo):
    pasos = columnas_resta(minuendo, sustraendo)
    assert sum(p.escribe * 10**p.posicion for p in pasos) == minuendo - sustraendo
    assert all(0 <= p.escribe <= 9 for p in pasos)


@pytest.mark.parametrize("sumandos", CASOS_SUMA[:100])
def test_pistas_de_suma_no_revelan_el_total(sumandos):
    pistas = pistas_suma(sumandos)
    assert len(pistas) == 3
    assert all(separar_bloque(p)[1] for p in pistas)
    assert not any(revela(separar_bloque(p)[0], str(sum(sumandos))) for p in pistas)


@pytest.mark.parametrize(("minuendo", "sustraendo"), CASOS_RESTA[:100])
def test_pistas_de_resta_no_revelan_el_resultado(minuendo, sustraendo):
    pistas = pistas_resta(minuendo, sustraendo)
    assert len(pistas) == 3
    assert not any(revela(separar_bloque(p)[0], str(minuendo - sustraendo)) for p in pistas)


def test_division_como_se_escribe_en_chile():
    assert division_vertical(975, 3, 2) == "\n".join(
        [
            "  9 7 5 : 3 = 32",
            "− 9",
            "───",
            "  0 7",
            "  − 6",
            "  ───",
            "    1 5",
        ]
    )
    # Si la primera cifra no alcanza se toman dos; un 0 en el cociente baja otra cifra.
    assert pasos_division(156, 4)[0].parcial == 15
    assert division_vertical(618, 3, 2).split("\n")[-1] == "    1 8"


CASOS_DIVISION = [
    (random.Random(s).randint(10, 999), random.Random(s + 1000).randint(2, 9)) for s in range(300)
]


@pytest.mark.parametrize(("dividendo", "divisor"), CASOS_DIVISION)
def test_division_cuadra_y_nunca_muestra_el_cociente_ni_el_resto_finales(dividendo, divisor):
    cociente, resto = divmod(dividendo, divisor)
    pasos = pasos_division(dividendo, divisor)
    assert int("".join(str(p.cifra) for p in pasos)) == cociente
    assert pasos[-1].resto == resto
    assert all(p.producto == p.cifra * divisor and 0 <= p.resto < divisor for p in pasos)
    for resueltas in range(4):
        bloque = division_vertical(dividendo, divisor, resueltas)
        mostrado = bloque.split("\n")[0].split("=")[1].strip()
        assert len(mostrado) < len(str(cociente)) or not mostrado
        assert str(cociente).startswith(mostrado)
        # El último paso (su producto y el resto final) nunca se escribe.
        restas = [linea for linea in bloque.split("\n") if linea.lstrip().startswith("−")]
        assert len(restas) < len(pasos)


@pytest.mark.parametrize(("dividendo", "divisor"), CASOS_DIVISION[:100])
def test_pistas_de_division_no_revelan_el_cociente(dividendo, divisor):
    pistas = pistas_division(dividendo, divisor)
    if dividendo // divisor < 10:
        assert pistas is None
        return
    assert not any(revela(separar_bloque(p)[0], str(dividendo // divisor)) for p in pistas)


@pytest.mark.parametrize("semilla", range(300))
def test_producto_por_una_cifra_cuadra_y_no_muestra_el_resultado(semilla):
    azar = random.Random(semilla)
    numero, factor = azar.randint(11, 999), azar.randint(2, 9)
    producto = numero * factor
    columnas = len(str(producto))
    for resueltas in range(4):
        _, filas, abajo = _lineas(producto_vertical(numero, factor, resueltas))
        assert [
            sum(c * 10**i for i, c in _cifras_visibles(f, 2, columnas).items()) for f in filas
        ] == [numero, factor]
        visibles = _cifras_visibles(abajo, 2, columnas)
        assert all(producto // 10**i % 10 == c for i, c in visibles.items())
        assert len(visibles) < columnas
    pistas = pistas_producto(numero, factor)
    assert not any(revela(separar_bloque(p)[0], str(producto)) for p in pistas)


def test_producto_por_dos_cifras_deja_vacio_el_lugar_de_las_unidades():
    assert producto_dos_cifras_vertical(18, 22, 2) == "\n".join(
        [
            "",
            "    1 8",
            "×   2 2",
            "───────",
            "    3 6",
            "+ 3 6",
            "───────",
            "",
        ]
    )


@pytest.mark.parametrize("semilla", range(300))
def test_producto_por_dos_cifras_muestra_las_filas_y_nunca_el_total(semilla):
    azar = random.Random(semilla)
    numero, factor = azar.randint(11, 99), azar.choice([f for f in range(11, 100) if f % 10])
    producto = numero * factor
    columnas = len(str(producto))
    lineas = producto_dos_cifras_vertical(numero, factor, 2).split("\n")
    primera = _cifras_visibles(lineas[4], 2, columnas)
    segunda = _cifras_visibles(lineas[5], 2, columnas)
    assert sum(c * 10**i for i, c in primera.items()) == numero * (factor % 10)
    assert 0 not in segunda  # el lugar de las unidades queda vacío
    assert sum(c * 10**i for i, c in segunda.items()) == numero * (factor // 10) * 10
    assert lineas[-1] == ""  # la suma de las filas la hace el niño
    pistas = pistas_producto_dos_cifras(numero, factor)
    assert not any(revela(separar_bloque(p)[0], str(producto)) for p in pistas)
