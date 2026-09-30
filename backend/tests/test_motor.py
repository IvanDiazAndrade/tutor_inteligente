"""Motor adaptativo: ejemplos y reglas de modelo_estudiante.md §1-4."""

from datetime import UTC, datetime
from decimal import Decimal

import pytest

from tutor.motor import ESTADO_INICIAL, EstadoMotor, ponderar, registrar_intento

AHORA = datetime(2026, 9, 30, tzinfo=UTC)


@pytest.mark.parametrize(
    ("correcta", "pistas", "esperado"),
    [(False, 0, "0"), (True, 0, "1"), (True, 1, "0.85"), (True, 2, "0.70"), (True, 3, "0.55")],
)
def test_resultado_ponderado(correcta, pistas, esperado):
    assert ponderar(correcta, pistas) == Decimal(esperado)


def test_el_piso_con_pistas_es_04():
    # Con más pistas de las previstas nunca baja de 0,4 si la respuesta es correcta.
    assert ponderar(True, 10) == Decimal("0.4")


def test_ejemplo_trazado_del_documento():
    """Tabla de §2: estudiante que entra por primera vez a 4B-OA9."""
    pasos = [
        (True, 0, "0.750", 2, None),
        (True, 1, "0.800", 2, None),
        (True, 0, "0.900", 3, "sube"),  # índice ≥ 0,8 y racha 3
        (False, 0, "0.630", 3, None),  # desde aquí α = 0,3
        (True, 0, "0.741", 3, None),
    ]
    estado = ESTADO_INICIAL
    for correcta, pistas, indice, nivel, cambio in pasos:
        estado, cambio_real = registrar_intento(estado, correcta, pistas, AHORA)
        assert estado.indice == Decimal(indice)
        assert estado.nivel == nivel
        assert cambio_real == cambio


def test_tres_correctas_en_frio_suben_de_inmediato():
    estado = ESTADO_INICIAL
    for _ in range(3):
        estado, cambio = registrar_intento(estado, True, 0, AHORA)
    assert estado.nivel == 3 and cambio == "sube" and estado.indice == Decimal("0.938")


def test_un_fallo_en_frio_ya_baja_al_nivel_1():
    """Con α = 0,5, el primer fallo deja el índice en 0,25 (< 0,4) y bajar no exige racha (§3).
    Nota: el ejemplo de §4 dice "en el segundo fallo"; las reglas de §3 lo bajan en el primero."""
    estado, cambio = registrar_intento(ESTADO_INICIAL, False, 0, AHORA)
    assert estado.indice == Decimal("0.250") and estado.nivel == 1 and cambio == "baja"


def test_no_sube_sin_racha_de_tres():
    estado = EstadoMotor(indice=Decimal("0.95"), nivel=2, racha=0, intentos=10)
    estado, cambio = registrar_intento(estado, True, 0, AHORA)
    assert cambio is None and estado.racha == 1 and estado.nivel == 2


def test_la_racha_se_reinicia_con_un_error_y_con_el_cambio_de_nivel():
    estado = EstadoMotor(indice=Decimal("0.9"), nivel=2, racha=2, intentos=10)
    subido, cambio = registrar_intento(estado, True, 0, AHORA)
    assert cambio == "sube" and subido.racha == 0
    fallado, _ = registrar_intento(estado, False, 0, AHORA)
    assert fallado.racha == 0


def test_en_el_nivel_3_dominado_no_hay_adonde_subir():
    estado = EstadoMotor(indice=Decimal("0.95"), nivel=3, racha=5, intentos=20)
    estado, cambio = registrar_intento(estado, True, 0, AHORA)
    assert cambio is None and estado.nivel == 3


def test_en_el_nivel_1_no_hay_adonde_bajar():
    estado = EstadoMotor(indice=Decimal("0.1"), nivel=1, racha=0, intentos=20)
    estado, cambio = registrar_intento(estado, False, 0, AHORA)
    assert cambio is None and estado.nivel == 1


def test_zona_estable_sin_cambios_de_nivel():
    """Histéresis 0,4-0,8 (§3): practicar en la zona media no mueve el nivel."""
    estado = EstadoMotor(indice=Decimal("0.6"), nivel=2, racha=0, intentos=10)
    for correcta in [True, False, True, False, True]:
        estado, cambio = registrar_intento(estado, correcta, 0, AHORA)
        assert cambio is None
    assert estado.nivel == 2
