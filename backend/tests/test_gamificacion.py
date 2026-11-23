"""Gamificación (tarea 64; RF-G1–G4; CU-5, CU-6): puntos, marca personal, estrellas e insignias."""

from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from tests.conftest import UNIDAD
from tests.test_api_ejercicios import _ejercicio, _responder, _servir
from tutor.gamificacion import mensaje, puntos_por
from tutor.modelos import DominioOA, Intento


def _resolver(cliente, cabecera, sesion):
    servido = _servir(cliente, cabecera)
    correcta = _ejercicio(sesion, servido["servidoId"]).respuesta_final
    return _responder(cliente, cabecera, servido["servidoId"], correcta).json()


@pytest.mark.parametrize(
    ("nivel", "pistas", "puntos"),
    [(1, 0, 10), (2, 0, 20), (3, 0, 30), (2, 1, 17), (3, 2, 21), (3, 3, 16), (1, 3, 6)],
)
def test_puntos_ponderados_por_nivel_con_descuento_por_pista(nivel, pistas, puntos):
    assert puntos_por(nivel, pistas) == puntos


def test_con_ayuda_tambien_se_gana_algo():
    assert all(puntos_por(n, 3) > 0 for n in (1, 2, 3))  # RF-P5: el error no se castiga


@pytest.mark.parametrize(
    ("semana", "marca", "esperado"),
    [
        (0, 0, "Empieza cuando quieras"),
        (0, 50, "semana nueva"),
        (60, 50, "Superaste tu marca"),
        (40, 50, "Con 11 puntos más superas tu mejor semana"),
        (30, 0, "primera insignia"),
    ],
)
def test_el_mensaje_compara_solo_contigo_mismo(semana, marca, esperado):
    texto = mensaje(semana, marca, insignias=0)
    assert esperado in texto
    # RF-G3/G4: nada de comparación con otros.
    assert not any(p in texto.lower() for p in ("ranking", "compañeros", "otros", "lugar"))


def test_progreso_sin_practica(cliente, cabecera):
    progreso = cliente.get("/estudiante/progreso", headers=cabecera).json()
    assert progreso["puntosTotal"] == 0 and progreso["puntosSemana"] == 0
    assert progreso["unidades"] == [] and progreso["insignias"] == 0


def test_progreso_suma_los_puntos_de_la_semana(cliente, cabecera, sesion):
    _resolver(cliente, cabecera, sesion)

    progreso = cliente.get("/estudiante/progreso", headers=cabecera).json()
    assert progreso["puntosTotal"] == 20 and progreso["puntosSemana"] == 20
    assert progreso["ejerciciosResueltos"] == 1
    [unidad] = progreso["unidades"]
    assert unidad["id"] == UNIDAD and unidad["estrellas"] == 2 and not unidad["insignia"]


def test_la_marca_es_la_mejor_semana_anterior(cliente, cabecera, sesion, estudiante):
    _resolver(cliente, cabecera, sesion)
    intento = sesion.query(Intento).filter_by(estudiante_id=estudiante.id).one()
    intento.creado_en = datetime.now(UTC) - timedelta(days=14)  # fue hace dos semanas
    sesion.commit()

    progreso = cliente.get("/estudiante/progreso", headers=cabecera).json()
    assert progreso["puntosSemana"] == 0 and progreso["mejorSemanaAnterior"] == 20
    assert "semana nueva" in progreso["mensaje"]


def test_dominar_la_unidad_entrega_la_insignia_una_sola_vez(cliente, cabecera, sesion, estudiante):
    sesion.add(
        DominioOA(
            estudiante_id=estudiante.id,
            unidad_id=UNIDAD,
            indice=Decimal("0.75"),
            nivel_actual=2,
            racha_correctas=0,
            intentos_en_unidad=5,
        )
    )
    sesion.commit()

    respuesta = _resolver(cliente, cabecera, sesion)
    assert respuesta["insignia"] == "Dividir con resto"
    assert "insignia" in respuesta["mensaje"]

    progreso = cliente.get("/estudiante/progreso", headers=cabecera).json()
    assert progreso["insignias"] == 1 and progreso["unidades"][0]["estrellas"] == 3

    # Ya dominada: la siguiente correcta no vuelve a anunciarla.
    assert _resolver(cliente, cabecera, sesion)["insignia"] is None
