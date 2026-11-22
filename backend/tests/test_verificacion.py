"""Capas 1 y 2 del pipeline de ejercicios verbales (modelo_dominio.md §8): funciones puras."""

import pytest

from tutor.dominio.verificacion import (
    operaciones,
    respuesta_canonica,
    verificar,
    verificar_aritmetica,
    verificar_forma,
)
from tutor.llm.adaptador import EjercicioLLM, ErrorComunLLM

RANGO_DINERO = {"monto_min": 100, "monto_max": 10000, "multiplo_de": 10}


def _ejercicio(**cambios) -> EjercicioLLM:
    """Un problema de dinero de 4° básico bien hecho; cada prueba cambia una sola cosa."""
    datos = dict(
        enunciado=(
            "Sofía compra un cuaderno de $1.200 y un lápiz de $350. Paga con $2.000. "
            "¿Cuánto dinero recibe de vuelto?"
        ),
        formato_respuesta="numerico",
        respuesta_final="$450",
        solucion_referencia=[
            "Primero se suma lo que gasta: 1.200 + 350 = 1.550.",
            "Después se resta del billete: 2.000 − 1.550 = 450.",
            "Sofía recibe $450 de vuelto.",
        ],
        errores_comunes=[
            ErrorComunLLM(
                respuesta="1.550",
                causa="respondió lo que gastó",
                retroalimentacion="Eso es lo que gastó. La pregunta es cuánto le devuelven.",
            ),
            ErrorComunLLM(
                respuesta="3.550",
                causa="sumó todo",
                retroalimentacion="El vuelto se calcula restando lo gastado.",
            ),
        ],
        pistas=[
            "Primero averigua cuánto gasta en total.",
            "Suma el precio del cuaderno y el del lápiz.",
            "Ahora resta ese total al dinero con que paga.",
        ],
    )
    datos.update(cambios)
    return EjercicioLLM(**datos)


def test_un_problema_bien_hecho_pasa_las_dos_capas():
    assert verificar(_ejercicio(), curso=4, rango=RANGO_DINERO) is None


@pytest.mark.parametrize(
    ("texto", "esperado"),
    [
        ("1.200 + 350 = 1.550", True),
        ("0,1 + 0,2 = 0,3", True),  # exacto: nunca floats
        ("3/4 + 1/8 = 7/8", True),
        ("1 1/2 + 2/4 = 2", True),
        ("(1.200 + 800) × 2 = 4.000", True),
        ("1.200 + 800 × 2 = 2.800", True),  # prioridad de la multiplicación
        ("750 : 3 = 250", True),
        ("2.000 − 1.550 = 450", True),
        ("1.200 + 350 = 1.650", False),
        ("3/4 + 1/8 = 4/12", False),
    ],
)
def test_cada_operacion_se_recalcula_exacta(texto, esperado):
    [(_, calculado, escrito, _)] = operaciones(texto)
    assert (calculado == escrito) is esperado


def test_paso_aritmetico_incorrecto_se_descarta():
    pasos = ["1.200 + 350 = 1.650.", "2.000 − 1.650 = 350.", "Recibe $350."]
    motivo = verificar_aritmetica(_ejercicio(solucion_referencia=pasos, respuesta_final="350"))
    assert "paso aritmético incorrecto" in motivo


def test_un_numero_inventado_se_descarta():
    pasos = ["1.200 + 500 = 1.700.", "2.000 − 1.700 = 300.", "Recibe $300."]
    motivo = verificar_aritmetica(_ejercicio(solucion_referencia=pasos, respuesta_final="300"))
    assert "500" in motivo and "no está en el enunciado" in motivo


def test_la_respuesta_tiene_que_ser_el_resultado_de_la_solucion():
    motivo = verificar_aritmetica(_ejercicio(respuesta_final="$550"))
    assert motivo == "la respuesta final no es el resultado de la solución"


def test_sin_operaciones_no_se_puede_verificar():
    pasos = ["Se suman los precios.", "Se resta del billete.", "Recibe $450."]
    motivo = verificar_aritmetica(_ejercicio(solucion_referencia=pasos))
    assert motivo == "la solución no tiene operaciones que se puedan verificar"


def test_problema_de_fracciones():
    ej = _ejercicio(
        enunciado="Ana comió 1/4 de una pizza y Luis 2/4. ¿Qué fracción comieron entre los dos?",
        formato_respuesta="fraccion",
        respuesta_final="3/4",
        solucion_referencia=["1/4 + 2/4 = 3/4.", "Entre los dos comieron 3/4."],
        errores_comunes=[
            ErrorComunLLM(
                respuesta="3/8",
                causa="sumó los denominadores",
                retroalimentacion="Con igual denominador, solo se suman los numeradores.",
            )
        ],
    )
    assert verificar(ej, curso=4, rango={}) is None


@pytest.mark.parametrize(
    ("cambio", "motivo"),
    [
        ({"pistas": ["Suma los precios.", "Recibe 450.", "Resta."]}, "la pista 2 revela"),
        ({"enunciado": "Sofía " * 61 + "¿cuánto? $1.200 $350 $2.000"}, "palabras"),
        (
            {"enunciado": "Sofía tiene $1.200, $350 y $2.000 dólares. Calcula el vuelto."},
            "no hace una pregunta",
        ),
        (
            {"enunciado": "Sofía paga $2.000 por $1.200 y $350 en dólares. ¿Cuánto vuelto?"},
            "moneda",
        ),
        (
            {"enunciado": "Un cuaderno de $1.200, un lápiz de $350; paga $20.000. ¿Vuelto?"},
            "fuera del rango",
        ),
        (
            {"enunciado": "Un cuaderno de $1.205, un lápiz de $345; paga $2.000. ¿Vuelto?"},
            "múltiplo de 10",
        ),
        (
            {
                "errores_comunes": [
                    ErrorComunLLM(respuesta="450", causa="-", retroalimentacion="Revisa.")
                ]
            },
            "vale lo mismo que la respuesta",
        ),
        (
            {
                "errores_comunes": [
                    ErrorComunLLM(
                        respuesta="1.550", causa="-", retroalimentacion="La respuesta es 450."
                    )
                ]
            },
            "retroalimentación de error revela",
        ),
    ],
)
def test_capa_de_forma(cambio, motivo):
    assert motivo in verificar_forma(_ejercicio(**cambio), curso=4, rango=RANGO_DINERO)


def test_la_respuesta_se_guarda_sin_signo_peso_ni_punto_de_miles():
    # Si se guardara "$3.800", el corrector leería 3.800 con tres decimales (3,8).
    assert respuesta_canonica("$3.800", "numerico") == "3800"
    assert respuesta_canonica("2,50", "numerico") == "2,5"
    assert respuesta_canonica("1  1 / 2", "fraccion") == "1 1/2"
