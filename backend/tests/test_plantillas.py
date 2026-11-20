"""Plantillas paramétricas: cada instancia debe ser correcta por construcción (AD-9)."""

import random
import re
from fractions import Fraction

import pytest

from tutor.dominio.corrector import corregir, fraccion
from tutor.dominio.plantillas import PLANTILLAS, EjercicioGenerado, menciona
from tutor.mensajes import revela

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
            # La retroalimentación local tampoco revela (si lo hiciera, el filtro la cambiaría).
            assert not revela(error["retroalimentacion"], e.respuesta_final), (e, error)
        assert len(e.pistas) == 3
        # Ninguna pista revela la respuesta final (RF-P3; la pista 3 queda a un paso del final).
        # Se usa el mismo filtro del tutor, que también ve 1.800 en 1800 o 6/8 en 3/4: una pista
        # que lo dispare se serviría como el mensaje de respaldo genérico.
        for pista in e.pistas:
            assert not menciona(pista, e.respuesta_final), (e.enunciado, pista)
            assert not revela(pista, e.respuesta_final), (e.enunciado, pista)
        assert revela(e.solucion_referencia[-1], e.respuesta_final)
        assert e.unidad_id == PLANTILLAS[plantilla_id].unidad_id and e.nivel == nivel


@pytest.mark.parametrize("plantilla_id", PLANTILLAS)
@pytest.mark.parametrize("nivel", [1, 2, 3])
def test_cada_celda_tiene_variedad_para_el_banco(plantilla_id, nivel):
    """El banco pide 5 enunciados distintos por celda (modelo_dominio.md §5). 4B-OA9 nivel 1
    solo admite 4 (pendientes.md §9)."""
    distintos = {e.enunciado for e in _instancias(plantilla_id, nivel)}
    minimo = 4 if (plantilla_id, nivel) == ("4B-OA9-suma-igual-den", 1) else 5
    assert len(distintos) >= minimo


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


# Plantillas de 4° básico: rangos de cada nivel --------------------------------------------


def _enteros(texto: str) -> list[int]:
    return [int(n.replace(".", "")) for n in re.findall(r"\d+(?:\.\d{3})*", texto)]


@pytest.mark.parametrize("nivel", [1, 2, 3])
def test_tablas_respetan_los_rangos_de_cada_nivel(nivel):
    for e in _instancias("4B-OA2-tablas", nivel):
        a, b = _enteros(e.enunciado)
        if "×" in e.enunciado:
            assert nivel < 3 and 2 <= a <= 10 and 2 <= b <= 10
            assert e.respuesta_final == str(a * b)
            if nivel == 1:
                assert b in (2, 5, 10)
        else:
            assert nivel > 1 and a % b == 0 and 2 <= a // b <= 10
            assert e.respuesta_final == str(a // b)
            assert b in ((2, 5, 10) if nivel == 2 else (3, 4, 6, 7, 8, 9))


def test_tablas_nivel_2_mezcla_multiplicar_y_dividir():
    assert {"×" in e.enunciado for e in _instancias("4B-OA2-tablas", 2)} == {True, False}


@pytest.mark.parametrize("nivel", [1, 2, 3])
def test_suma_y_resta_respetan_los_rangos_de_cada_nivel(nivel):
    from tutor.dominio.plantillas.cuarto import _resta_columnas, _suma_columnas

    for e in _instancias("4B-OA3-suma-resta", nivel):
        numeros = _enteros(e.enunciado)
        if "−" in e.enunciado:
            a, b = numeros
            resultado = a - b
            _, _, canjes, por_cero = _resta_columnas(a, b)
            if nivel == 1:
                assert canjes == 0
            elif nivel == 2:
                assert canjes == 1 and not por_cero
            else:
                assert canjes >= 2 or por_cero
        else:
            resultado = sum(numeros)
            _, _, reservas = _suma_columnas(numeros)
            assert len(numeros) == (2 if nivel < 3 else len(numeros)) and len(numeros) <= 4
            if nivel == 1:
                assert reservas == 0 and all(n >= 100 for n in numeros)
            elif nivel == 2:
                assert reservas >= 1
            else:
                assert len(numeros) >= 3 and reservas >= 2
        assert 100 <= resultado <= 999
        assert e.respuesta_final == str(resultado)


@pytest.mark.parametrize(
    ("operacion", "esperado"),
    [
        ((503, 278), "Como no hay decenas"),  # canje que pasa por un cero
        ((652, 318), "Se canjea 1 decena por 10 unidades"),
    ],
)
def test_resta_explica_el_canje(operacion, esperado):
    from tutor.dominio.plantillas.cuarto import _resta_columnas

    pasos, cifras, _, _ = _resta_columnas(*operacion)
    assert esperado in pasos[0]
    assert int("".join(str(c) for c in reversed(cifras))) == operacion[0] - operacion[1]


@pytest.mark.parametrize("nivel", [1, 2, 3])
def test_multiplicacion_respeta_los_rangos_de_cada_nivel(nivel):
    from tutor.dominio.plantillas.cuarto import _reservas_multiplicacion

    for e in _instancias("4B-OA5-mult-3x1", nivel):
        numero, factor = _enteros(e.enunciado)
        assert 101 <= numero <= 999 and numero % 100 and 2 <= factor <= 9
        assert e.respuesta_final == str(numero * factor)
        reservas = _reservas_multiplicacion(numero, factor)
        if nivel == 1:
            assert reservas == 0
        elif nivel == 2:
            assert reservas == 1
        else:
            assert reservas >= 2 or (reservas >= 1 and numero // 10 % 10 == 0)


def test_multiplicacion_escribe_los_miles_con_punto():
    from tutor.dominio.plantillas.cuarto import Multiplicacion3x1

    for e in _instancias("4B-OA5-mult-3x1", 3):
        if int(e.respuesta_final) >= 1000:
            assert re.search(r"\d\.\d{3}\.$", e.solucion_referencia[-1])
            # El estudiante puede responder con o sin el punto.
            punto = f"{int(e.respuesta_final):,}".replace(",", ".")
            assert corregir(punto, Corregible(e)).estado == "correcta"
            break
    assert Multiplicacion3x1.unidad_id == "4B-OA5"


@pytest.mark.parametrize("nivel", [1, 2, 3])
def test_division_2_cifras_respeta_los_rangos_de_cada_nivel(nivel):
    for e in _instancias("4B-OA6-div-2d", nivel):
        numeros = _enteros(e.enunciado)
        divisor, dividendo = numeros if "multiplicar" in e.enunciado else reversed(numeros)
        cociente = dividendo // divisor
        assert 10 <= dividendo <= 99 and dividendo % divisor == 0
        assert e.respuesta_final == str(cociente)
        if nivel == 1:
            assert 2 <= divisor <= 5 and cociente <= 10
        else:
            assert cociente > 10 and cociente % 10
            if nivel == 2 or "multiplicar" in e.enunciado:
                assert 2 <= divisor <= 5
            else:
                assert 6 <= divisor <= 9


def test_division_2_cifras_nivel_3_a_veces_pregunta_el_factor():
    preguntas = {"multiplicar" in e.enunciado for e in _instancias("4B-OA6-div-2d", 3)}
    assert preguntas == {True, False}
