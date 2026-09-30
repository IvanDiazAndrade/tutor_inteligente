"""Plantillas paramétricas: cada instancia debe ser correcta por construcción (AD-9)."""

import random
import re
from fractions import Fraction

import pytest

from tutor.dominio.corrector import corregir, fraccion
from tutor.dominio.plantillas import PLANTILLAS, EjercicioGenerado, menciona

INSTANCIAS_POR_NIVEL = 300


def _instancias(plantilla_id: str, nivel: int) -> list[EjercicioGenerado]:
    azar = random.Random(f"{plantilla_id}-{nivel}")  # semilla fija: pruebas reproducibles
    return [PLANTILLAS[plantilla_id].instanciar(nivel, azar) for _ in range(INSTANCIAS_POR_NIVEL)]


class Corregible:
    """Adapta un EjercicioGenerado a lo que espera el corrector."""

    def __init__(self, e: EjercicioGenerado):
        self.formato_respuesta = e.formato_respuesta
        self.respuesta_final = e.respuesta_final
        self.regla_validacion = e.regla_validacion
        self.errores_comunes = e.errores_comunes


@pytest.mark.parametrize("plantilla_id", PLANTILLAS)
@pytest.mark.parametrize("nivel", [1, 2, 3])
def test_toda_instancia_es_coherente(plantilla_id, nivel):
    for e in _instancias(plantilla_id, nivel):
        corregible = Corregible(e)
        assert corregir(e.respuesta_final, corregible).estado == "correcta", e
        for error in e.errores_comunes:
            resultado = corregir(error["respuesta"], corregible)
            assert resultado.estado == "incorrecta", (e.enunciado, error)
            assert resultado.error_comun == error
        assert len(e.pistas) == 3
        # Ninguna pista revela la respuesta final (RF-P3; la pista 3 queda a un paso del final).
        for pista in e.pistas:
            assert not menciona(pista, e.respuesta_final), (e.enunciado, pista)
        assert menciona(e.solucion_referencia[-1], e.respuesta_final)
        assert e.unidad_id == PLANTILLAS[plantilla_id].unidad_id and e.nivel == nivel


@pytest.mark.parametrize("nivel", [1, 2, 3])
def test_division_respeta_los_rangos_de_cada_nivel(nivel):
    for e in _instancias("5B-OA4-div-resto", nivel):
        dividendo, divisor = map(int, re.findall(r"\d+", e.enunciado)[:2])
        assert 100 <= dividendo <= 999
        cociente, resto = divmod(dividendo, divisor)
        if nivel == 1:
            assert 2 <= divisor <= 5 and resto == 0  # N1: división exacta
        else:
            assert 2 <= divisor <= 9 and resto > 0
        esperado = resto if "resto" in e.enunciado else cociente
        assert e.respuesta_final == str(esperado)
        if nivel < 3:
            assert "cociente" in e.enunciado


def test_division_nivel_3_pregunta_a_veces_el_resto():
    preguntas = {"resto" in e.enunciado for e in _instancias("5B-OA4-div-resto", 3)}
    assert preguntas == {True, False}


@pytest.mark.parametrize("nivel", [1, 2, 3])
def test_fracciones_respetan_los_rangos_de_cada_nivel(nivel):
    for e in _instancias("4B-OA9-suma-igual-den", nivel):
        a, d1, b, d2 = map(int, re.findall(r"\d+", e.enunciado))
        assert d1 == d2 and d1 in (2, 3, 4, 5, 6, 8, 10, 12)
        resta = "−" in e.enunciado
        valor = Fraction(a - b if resta else a + b, d1)
        assert fraccion(e.respuesta_final) == valor
        if nivel == 1:
            assert d1 <= 4 and e.representacion is not None  # N1: siempre pictórico
        if nivel < 3:
            assert not resta and a + b < d1  # resultado propio
        elif not resta:
            assert a + b == d1  # N3: suma con resultado igual a 1
        if e.representacion:
            assert e.representacion["parametros"] == {"denominador": d1, "partesDestacadas": [a, b]}


def test_fracciones_nivel_2_muestra_la_figura_solo_a_veces():
    con_figura = {e.representacion is not None for e in _instancias("4B-OA9-suma-igual-den", 2)}
    assert con_figura == {True, False}
