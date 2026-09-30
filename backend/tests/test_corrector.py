"""Corrector programático: casos de modelo_dominio.md §3."""

from dataclasses import dataclass, field
from typing import Any

import pytest

from tutor.dominio.corrector import corregir


@dataclass
class Ej:
    formato_respuesta: str
    respuesta_final: str
    regla_validacion: dict[str, Any] = field(default_factory=dict)
    errores_comunes: list[dict[str, Any]] = field(default_factory=list)


def estado(respuesta: str, ejercicio: Ej) -> str:
    return corregir(respuesta, ejercicio).estado


# Números ---------------------------------------------------------------------------------


@pytest.mark.parametrize("respuesta", ["0,5", "0.5", ",5", "0,50", " 0,5 ", "0,500"])
def test_coma_punto_y_ceros_finales_valen_igual(respuesta):
    assert estado(respuesta, Ej("numerico", "0,5")) == "correcta"


def test_aritmetica_exacta_sin_flotantes():
    # 0,1 + 0,2 = 0,3 exacto: con floats sería 0.30000000000000004.
    assert estado("0,3", Ej("numerico", "0,3")) == "correcta"
    assert estado("0,30000000000000004", Ej("numerico", "0,3")) == "incorrecta"


def test_punto_de_miles_y_signo_peso():
    ejercicio = Ej("numerico", "12500")
    for respuesta in ["12500", "12.500", "$12.500", "12.500 pesos", "$ 12500"]:
        assert estado(respuesta, ejercicio) == "correcta", respuesta


def test_punto_ambiguo_se_resuelve_con_la_respuesta_esperada():
    assert estado("1.500", Ej("numerico", "1500")) == "correcta"  # mil quinientos
    assert estado("1.5", Ej("numerico", "1,5")) == "correcta"  # uno coma cinco
    assert estado("1.500", Ej("numerico", "1,5")) == "correcta"  # 1,500 = 1,5


def test_texto_no_numerico_no_cuenta_como_intento():
    resultado = corregir("dos", Ej("numerico", "2"))
    assert resultado.estado == "formato_invalido"
    assert not resultado.cuenta_como_intento


# Fracciones ------------------------------------------------------------------------------


def test_fraccion_exacta_y_equivalente_aceptada_por_defecto():
    ejercicio = Ej("fraccion", "3/4")
    assert corregir("3/4", ejercicio).forma_distinta is False
    equivalente = corregir("6/8", ejercicio)
    assert equivalente.estado == "correcta" and equivalente.forma_distinta


def test_si_la_forma_es_el_objetivo_la_equivalente_no_vale():
    """5B-OA7 (simplificar) y 6B-OA5 (impropia ↔ mixto): aceptaEquivalentes = false."""
    ejercicio = Ej("fraccion", "3/4", regla_validacion={"aceptaEquivalentes": False})
    assert estado("3/4", ejercicio) == "correcta"
    assert estado("6/8", ejercicio) == "incorrecta"


def test_numeros_mixtos():
    ejercicio = Ej("fraccion", "1 1/2")
    assert estado("1 1/2", ejercicio) == "correcta"
    assert estado("3/2", ejercicio) == "correcta"
    ejercicio_forma = Ej("fraccion", "1 1/2", regla_validacion={"aceptaEquivalentes": False})
    assert estado("3/2", ejercicio_forma) == "incorrecta"


def test_denominador_cero_es_formato_invalido():
    resultado = corregir("3/0", Ej("fraccion", "3/4"))
    assert resultado.estado == "formato_invalido"
    assert "0" in resultado.mensaje


def test_detecta_el_error_comun_de_sumar_denominadores():
    error = {
        "respuesta": "3/8",
        "causa": "sumó también los denominadores",
        "retroalimentacion": "…",
    }
    resultado = corregir("3/8", Ej("fraccion", "3/4", errores_comunes=[error]))
    assert resultado.estado == "incorrecta"
    assert resultado.error_comun["causa"] == "sumó también los denominadores"


def test_incorrecta_sin_patron_conocido():
    error = {"respuesta": "3/8", "causa": "x", "retroalimentacion": "x"}
    resultado = corregir("2/4", Ej("fraccion", "3/4", errores_comunes=[error]))
    assert resultado.estado == "incorrecta" and resultado.error_comun is None


def test_error_comun_numerico():
    errores = [{"respuesta": "27", "causa": "siguió dividiendo de más", "retroalimentacion": "…"}]
    resultado = corregir("27", Ej("numerico", "26", errores_comunes=errores))
    assert resultado.error_comun["causa"] == "siguió dividiendo de más"


# Ordenar y comparar ----------------------------------------------------------------------


def test_ordenar_compara_la_secuencia_completa():
    ejercicio = Ej("ordenar", "0,25; 1/2; 0,75; 1 1/2")
    assert estado("0,25; 0,5; 3/4; 3/2", ejercicio) == "correcta"
    assert estado("1/2; 0,25; 0,75; 1 1/2", ejercicio) == "incorrecta"


def test_comparar_con_simbolos():
    ejercicio = Ej("comparar", "=")  # 6/8 vs 3/4
    assert estado("=", ejercicio) == "correcta"
    assert estado("<", ejercicio) == "incorrecta"
    assert estado("mayor", ejercicio) == "formato_invalido"
