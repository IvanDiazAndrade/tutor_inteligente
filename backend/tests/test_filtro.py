"""Filtro completo de no revelación (modelo_pedagogico.md §6; tarea 66).

Incluye los casos de la prueba directa del filtro del protocolo adversarial (informe TT1):
la respuesta en cifras, en palabras y en formas equivalentes que acepta el corrector.
"""

from fractions import Fraction

import pytest

from tutor.dominio.palabras import cantidades
from tutor.mensajes import RESPALDO, revela, sin_revelar


@pytest.mark.parametrize(
    ("texto", "valor"),
    [
        ("mil doscientos treinta y cuatro", 1234),
        ("dos millones trescientos mil", 2_300_000),
        ("ciento cinco", 105),
        ("noventa y nueve", 99),
        ("tres cuartos", Fraction(3, 4)),
        ("un medio", Fraction(1, 2)),
        ("5 octavos", Fraction(5, 8)),
        ("siete doceavos", Fraction(7, 12)),
        ("dos coma cinco", Fraction(5, 2)),
        ("dos coma cero cinco", Fraction(41, 20)),
        ("cinco décimas", Fraction(1, 2)),
        ("dos enteros y veinticinco centésimas", Fraction(9, 4)),
        ("dos enteros y tres cuartos", Fraction(11, 4)),
        ("dos y medio", Fraction(5, 2)),
    ],
)
def test_lee_numeros_en_palabras(texto, valor):
    assert [c.valor for c in cantidades(texto)] == [valor]


@pytest.mark.parametrize(
    "texto",
    ["un número", "una pizza", "las unidades de mil", "el cuarto paso", "los dos números"],
)
def test_articulos_posiciones_y_ordinales_no_son_cantidades(texto):
    assert cantidades(texto) == []


def test_dos_numeros_seguidos_no_se_suman():
    assert [c.valor for c in cantidades("dos tres")] == [2, 3]


@pytest.mark.parametrize(
    ("texto", "respuesta"),
    [
        # En cifras y en las formas equivalentes que acepta el corrector.
        ("La respuesta es 1800.", "1800"),
        ("Te quedan 1.800 pesos.", "1800"),
        ("Son 6/8 de la pizza.", "3/4"),
        ("Es lo mismo que 0,75.", "3/4"),
        ("Da 2,50.", "2,5"),
        ("Queda 1 1/2.", "3/2"),
        # En palabras.
        ("Te quedan mil ochocientos pesos.", "1800"),
        ("Se comieron tres cuartos de la torta.", "3/4"),
        ("Son seis octavos.", "3/4"),
        ("Son 75 centésimos.", "3/4"),
        ("El resultado es dos coma cinco.", "2,5"),
        ("Son dos enteros y cinco décimas.", "2,5"),
        ("Tiene dos enteros y un cuarto.", "9/4"),
        ("Son cuarenta y cinco.", "45"),
        # Comparar y ordenar.
        ("2,5 es mayor que 2,2.", ">"),
        ("2,2 es menor que 2,5.", ">"),  # dicho al revés también revela
        ("Fíjate: 1/3 < 5/9.", "<"),
        ("El orden es 3/10, 5/10 y 6/10.", "3/10; 5/10; 6/10"),
    ],
)
def test_detecta_la_respuesta(texto, respuesta):
    assert revela(texto, respuesta)
    assert sin_revelar(texto, respuesta) == RESPALDO


@pytest.mark.parametrize(
    ("texto", "respuesta"),
    [
        ("Suma 1 + 3 y mira el denominador.", "3/4"),  # en fracciones, los enteros son operandos
        ("Mira los dos números con cuidado.", "2"),
        ("Usa la tabla del 7.", "56"),
        ("Para comparar, mira primero la cifra de mayor valor.", ">"),
        ("La menor es 3/10. Ahora busca la que sigue.", "3/10; 5/10; 6/10"),
        ("Cuenta las partes pintadas.", "3/4"),
    ],
)
def test_no_bloquea_ayudas_legitimas(texto, respuesta):
    assert not revela(texto, respuesta)


def test_si_el_enunciado_ya_da_el_valor_solo_revela_la_forma_pedida():
    enunciado = "Escribe 59/100 como número decimal."
    assert not revela("Son 59 centésimos: ocupa dos cifras después de la coma.", "0,59", enunciado)
    assert revela("Se escribe 0,59.", "0,59", enunciado)
    # Si el valor está en el enunciado en la misma forma, es coincidencia: el filtro sigue igual.
    enunciado = "Tenía 12 lápices y regaló 6 de ellos. ¿Cuántos le quedan?"
    assert revela("Le quedan seis.", "6", enunciado)
