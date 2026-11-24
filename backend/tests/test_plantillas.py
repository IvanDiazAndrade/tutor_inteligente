"""Plantillas paramétricas: cada instancia debe ser correcta por construcción (AD-9)."""

import random
import re
from fractions import Fraction

import pytest

from tutor.dominio.columnas import separar_bloque
from tutor.dominio.corrector import corregir, fraccion
from tutor.dominio.plantillas import PLANTILLAS, EjercicioGenerado, menciona
from tutor.dominio.plantillas.base import huella
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
            retro = error["retroalimentacion"]
            assert not revela(retro, e.respuesta_final, e.enunciado), (e, error)
        assert len(e.pistas) == 3
        # Ninguna pista revela la respuesta final (RF-P3; la pista 3 queda a un paso del final).
        # Se usa el mismo filtro del tutor, que también ve 1.800 en 1800 o 6/8 en 3/4: una pista
        # que lo dispare se serviría como el mensaje de respaldo genérico.
        # De una operación en columnas se revisa la frase (el bloque, en test_columnas.py).
        for pista in (separar_bloque(p)[0] for p in e.pistas):
            assert not menciona(pista, e.respuesta_final), (e.enunciado, pista)
            assert not revela(pista, e.respuesta_final, e.enunciado), (e.enunciado, pista)
        assert revela(e.solucion_referencia[-1], e.respuesta_final)
        assert e.unidad_id == PLANTILLAS[plantilla_id].unidad_id and e.nivel == nivel


@pytest.mark.parametrize("plantilla_id", PLANTILLAS)
@pytest.mark.parametrize("nivel", [1, 2, 3])
def test_cada_celda_tiene_variedad_para_el_banco(plantilla_id, nivel):
    """El banco pide 5 ejercicios distintos por celda (modelo_dominio.md §5). 4B-OA9 nivel 1
    solo admite 4 (pendientes.md §9)."""
    distintos = {
        huella(e.enunciado, e.representacion, e.regla_validacion)
        for e in _instancias(plantilla_id, nivel)
    }
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


# Plantillas de 5° y 6° básico: rangos de cada nivel ----------------------------------------


def _decimales_de(texto: str) -> list[Fraction]:
    return [Fraction(n.replace(",", ".")) for n in re.findall(r"\d+(?:,\d+)?", texto)]


@pytest.mark.parametrize("nivel", [1, 2, 3])
def test_multiplicacion_2x2_respeta_los_rangos_de_cada_nivel(nivel):
    for e in _instancias("5B-OA3-mult-2x2", nivel):
        a, b = _enteros(e.enunciado)
        assert 10 <= a <= 99 and 10 <= b <= 99 and a % 10
        assert e.respuesta_final == str(a * b)
        if nivel == 1:
            assert b % 10 == 0
        else:
            assert b % 10
            assert (a <= 49 and b <= 49) if nivel == 2 else a >= 51


@pytest.mark.parametrize("nivel", [1, 2, 3])
def test_operatoria_combinada_da_el_resultado_correcto(nivel):
    for e in _instancias("5B-OA5-combinada", nivel):
        expresion = e.enunciado.removeprefix("Calcula ").removesuffix(".")
        python = expresion.replace("×", "*").replace("−", "-").replace(":", "//")
        assert e.respuesta_final == str(eval(python))  # noqa: S307 (expresión generada aquí)
        assert int(e.respuesta_final) > 0
        if nivel == 3:
            assert ":" in expresion
        else:
            assert ":" not in expresion


@pytest.mark.parametrize("nivel", [1, 2, 3])
def test_fracciones_distinto_denominador_respetan_los_rangos(nivel):
    from math import lcm

    for e in _instancias("5B-OA9-distinto-den", nivel):
        a, d1, b, d2 = _enteros(e.enunciado)
        assert d1 != d2 and d1 <= 12 and d2 <= 12 and lcm(d1, d2) <= 24
        resta = "−" in e.enunciado
        valor = Fraction(a, d1) - Fraction(b, d2) if resta else Fraction(a, d1) + Fraction(b, d2)
        assert fraccion(e.respuesta_final) == valor and 0 < valor < 1
        assert resta == (nivel == 3)
        multiplo = lcm(d1, d2) == max(d1, d2)
        if nivel == 1:
            assert multiplo
        elif nivel == 2:
            assert not multiplo


@pytest.mark.parametrize("nivel", [1, 2, 3])
def test_decimales_suma_y_resta_respetan_los_rangos(nivel):
    from tutor.dominio.plantillas.base import decimales

    for e in _instancias("5B-OA12-decimales", nivel):
        x, y = _decimales_de(e.enunciado)
        valor = x - y if "−" in e.enunciado else x + y
        assert valor > 0
        assert corregir(e.respuesta_final.replace(",", "."), Corregible(e)).estado == "correcta"
        assert Fraction(e.respuesta_final.replace(",", ".")) == valor
        k1, k2 = decimales(x), decimales(y)
        if nivel == 1:
            assert k1 == k2 == 1
        else:
            assert k1 != k2 and max(k1, k2) == nivel


@pytest.mark.parametrize("nivel", [1, 2, 3])
def test_decimales_por_natural_respetan_los_rangos(nivel):
    from tutor.dominio.plantillas.base import decimales

    for e in _instancias("6B-OA7-mult-div-decimales", nivel):
        texto = e.enunciado.replace("1.000", "1000")
        x, y = _decimales_de(texto)
        valor = x * y if "×" in texto else x / y
        assert Fraction(e.respuesta_final.replace(",", ".")) == valor
        assert decimales(valor) <= 3
        if nivel == 1:
            assert y in (10, 100, 1000)
        else:
            assert 2 <= y <= 9 and ("×" in texto) == (nivel == 2)


# Ordenar, comparar y formas que son el objetivo ------------------------------------------


@pytest.mark.parametrize("plantilla_id", PLANTILLAS)
@pytest.mark.parametrize("nivel", [1, 2, 3])
def test_ordenar_y_comparar_muestran_los_valores_sin_la_respuesta(plantilla_id, nivel):
    for e in _instancias(plantilla_id, nivel):
        valores = e.regla_validacion.get("valores")
        if e.formato_respuesta == "ordenar":
            orden = e.respuesta_final.split("; ")
            assert sorted(valores) == sorted(orden) and len(valores) >= 3
            assert valores not in (orden, orden[::-1])  # desordenados
        elif e.formato_respuesta == "comparar":
            assert len(valores) == 2 and e.respuesta_final in ("<", "=", ">")
            assert all(v in e.enunciado for v in valores)
        else:
            assert valores is None


def test_comparar_decimales_nivel_2_siempre_es_la_trampa_de_las_cifras():
    for e in _instancias("5B-OA11-comparar-decimales", 2):
        causas = {err["causa"] for err in e.errores_comunes}
        assert "pensó que el decimal con más cifras es mayor" in causas


@pytest.mark.parametrize("nivel", [1, 2])
def test_amplificar_y_simplificar_exigen_la_forma_pedida(nivel):
    for e in _instancias("5B-OA7-equivalentes", nivel):
        assert e.regla_validacion["aceptaEquivalentes"] is False
        original = re.findall(r"\d+/\d+", e.enunciado)[0]
        resultado = corregir(original, Corregible(e))
        assert resultado.estado == "incorrecta"  # vale lo mismo, pero no es lo pedido
        assert resultado.error_comun["causa"] in ("no amplificó la fracción", "no simplificó")


def test_el_banco_distingue_ejercicios_con_el_mismo_enunciado():
    circulos = {
        huella(e.enunciado, e.representacion, e.regla_validacion)
        for e in _instancias("4B-OA8-fracciones", 1)
        if "círculo" in e.enunciado
    }
    assert len(circulos) >= 5  # el enunciado es siempre el mismo


def test_la_figura_corresponde_a_la_respuesta():
    tipos = set()
    for e in _instancias("4B-OA8-fracciones", 1):
        p = e.representacion["parametros"]
        tipos.add(e.representacion["tipo"])
        if e.representacion["tipo"] == "recta-numerica":
            assert (p["minimo"], p["maximo"]) == (0, 1)
            assert e.respuesta_final == f"{p['punto']}/{p['divisiones']}"
        else:
            assert e.respuesta_final == f"{p['partesDestacadas'][0]}/{p['denominador']}"
    assert tipos == {"fraccion-circulo", "recta-numerica"}
    for nivel in (1, 2):
        for e in _instancias("5B-OA10-fraccion-decimal", nivel):
            pintadas = e.representacion["parametros"]["pintadas"]
            assert Fraction(pintadas, 100) == Fraction(e.respuesta_final.replace(",", "."))


@pytest.mark.parametrize(
    ("plantilla_id", "niveles"),
    [
        ("4B-OA3-suma-resta", (1, 2, 3)),
        ("4B-OA5-mult-3x1", (1, 2, 3)),
        ("4B-OA6-div-2d", (2,)),
        ("5B-OA3-mult-2x2", (2, 3)),
        ("5B-OA4-div-resto", (1, 2, 3)),
    ],
)
def test_las_pistas_muestran_la_operacion_en_columnas(plantilla_id, niveles):
    for nivel in niveles:
        for e in _instancias(plantilla_id, nivel):
            assert all(separar_bloque(p)[1] for p in e.pistas), e
