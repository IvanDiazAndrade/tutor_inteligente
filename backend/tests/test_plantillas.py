"""Plantillas paramétricas: cada instancia debe ser correcta por construcción (AD-9)."""

import random
import re
from fractions import Fraction

import pytest

from tutor.catalogo import RUTA_POR_DEFECTO, leer_catalogo
from tutor.dominio.corrector import corregir, fraccion, numero
from tutor.dominio.plantillas import PLANTILLAS, EjercicioGenerado, revela

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
            assert not revela(pista, e.respuesta_final), (e.enunciado, pista)
        assert revela(e.solucion_referencia[-1], e.respuesta_final), e
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


# Todas las plantillas ------------------------------------------------------------------------

SOLO_LLM = {"4B-OA7", "5B-OA6", "5B-OA13", "6B-OA2", "6B-OA8"}  # modelo_dominio.md §4
EXCEPCIONES_STOCK = {("4B-OA9-suma-igual-den", 1)}  # limitado por diseño (test_banco)


def test_hay_una_plantilla_por_cada_unidad_parametrica_o_mixta():
    unidades = {u.id for u in leer_catalogo(RUTA_POR_DEFECTO)}
    assert {p.unidad_id for p in PLANTILLAS.values()} == unidades - SOLO_LLM


@pytest.mark.parametrize("plantilla_id", PLANTILLAS)
@pytest.mark.parametrize("nivel", [1, 2, 3])
def test_cada_celda_alcanza_el_stock_sin_repetir_enunciados(plantilla_id, nivel):
    if (plantilla_id, nivel) in EXCEPCIONES_STOCK:
        pytest.skip("celda limitada por diseño")
    enunciados = {e.enunciado for e in _instancias(plantilla_id, nivel)}
    assert len(enunciados) >= 5


@pytest.mark.parametrize("plantilla_id", PLANTILLAS)
@pytest.mark.parametrize("nivel", [1, 2, 3])
def test_las_respuestas_se_pueden_escribir_en_la_app(plantilla_id, nivel):
    for e in _instancias(plantilla_id, nivel):
        r = e.respuesta_final
        if e.formato_respuesta == "numerico":
            assert re.fullmatch(r"\d+(,\d+)?", r), e  # sin punto de miles ni signo negativo
            assert len(r) <= 12  # lo que admite la casilla
        elif e.formato_respuesta == "fraccion":
            assert re.fullmatch(r"\d+( \d+/\d+)?|\d+/\d+", r), e
            assert all(len(n) <= 4 for n in re.findall(r"\d+", r)), e
        elif e.formato_respuesta == "comparar":
            assert r in {"<", "=", ">"}
        else:
            # La app arma la respuesta tocando los valores presentados, en orden.
            valores = e.representacion["parametros"]["valores"]
            assert sorted(valores) == sorted(r.split("; ")), e
            assert "; ".join(valores) != r, "no puede venir ya ordenado"
            assert corregir(r, Corregible(e)).estado == "correcta"


@pytest.mark.parametrize("plantilla_id", PLANTILLAS)
@pytest.mark.parametrize("nivel", [1, 2, 3])
def test_las_figuras_son_coherentes(plantilla_id, nivel):
    for e in _instancias(plantilla_id, nivel):
        if e.representacion is None:
            continue
        tipo, p = e.representacion["tipo"], e.representacion["parametros"]
        if tipo == "fraccion-circulo":
            assert sum(p["partesDestacadas"]) <= p["denominador"] <= 12, e
        elif tipo == "recta-numerica":
            assert p["minimo"] == 0 and 0 < p["punto"] < p["divisiones"], e
            valor = Fraction(p["punto"] * p["maximo"], p["divisiones"])
            assert fraccion(e.respuesta_final) == valor, e
        elif tipo == "cuadricula-decimal":
            assert 0 < p["pintadas"] < 100, e
            valor = Fraction(p["pintadas"], 100)
            assert numero(e.respuesta_final) == valor, e
        else:
            assert tipo == "valores-ordenar", e


@pytest.mark.parametrize("nivel", [1, 2, 3])
def test_operaciones_coinciden_con_un_calculo_independiente(nivel):
    """Recalcula desde el enunciado, sin usar la plantilla, las unidades de cálculo directo."""
    operar = {"+": lambda a, b: a + b, "−": lambda a, b: a - b, "×": lambda a, b: a * b}
    operar[":"] = lambda a, b: a / b
    expresion = re.compile(r"^Calcula ([\d.,]+) ([+−×:]) ([\d.,]+)\.$")
    probados = 0
    for plantilla_id in PLANTILLAS:
        for e in _instancias(plantilla_id, nivel):
            m = expresion.match(e.enunciado)
            if not m or e.formato_respuesta != "numerico":
                continue
            a, signo, b = m.groups()
            assert numero(e.respuesta_final) == operar[signo](numero(a), numero(b)), e
            probados += 1
    assert probados > 0


@pytest.mark.parametrize("nivel", [1, 2, 3])
def test_fracciones_coinciden_con_un_calculo_independiente(nivel):
    expresion = re.compile(r"^Calcula ([\d ]*\d+/\d+) ([+−]) ([\d ]*\d+/\d+)\.$")
    probados = 0
    for plantilla_id in PLANTILLAS:
        for e in _instancias(plantilla_id, nivel):
            m = expresion.match(e.enunciado)
            if not m:
                continue
            a, signo, b = fraccion(m[1]), m[2], fraccion(m[3])
            assert fraccion(e.respuesta_final) == (a + b if signo == "+" else a - b), e
            assert fraccion(e.respuesta_final) > 0, e
            probados += 1
    assert probados > 0


@pytest.mark.parametrize("nivel", [1, 2])
def test_conversiones_exigen_la_forma_pedida(nivel):
    for plantilla_id in ("5B-OA7-equivalencia", "6B-OA5-impropias-mixtos"):
        for e in _instancias(plantilla_id, nivel):
            assert e.regla_validacion["aceptaEquivalentes"] is False, e


@pytest.mark.parametrize("plantilla_id", PLANTILLAS)
@pytest.mark.parametrize("nivel", [1, 2, 3])
def test_toda_respuesta_mixta_tiene_casilla_para_el_entero(plantilla_id, nivel):
    for e in _instancias(plantilla_id, nivel):
        if e.formato_respuesta == "fraccion" and " " in e.respuesta_final:
            assert e.regla_validacion["entradaMixta"] is True, e


@pytest.mark.parametrize("nivel", [2, 3])
def test_decimales_operar_sin_la_coma_da_un_resultado_exacto(nivel):
    for e in _instancias("6B-OA7-decimales", nivel):
        a, n = re.fullmatch(r"Calcula ([\d,]+) [×:] (\d)\.", e.enunciado).groups()
        assert "," in a and "," in e.respuesta_final, e
        assert len(a.split(",")[1]) == len(e.respuesta_final.split(",")[1]), e
        if nivel == 3:
            assert int(a.replace(",", "")) % int(n) == 0, e
