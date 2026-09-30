"""Banco de ejercicios paramétricos: registro, aprobación única y reposición de celdas."""

import random

import pytest
from sqlalchemy import select

from tutor.catalogo import RUTA_POR_DEFECTO, cargar_catalogo, leer_catalogo
from tutor.dominio.banco import (
    STOCK_OBJETIVO,
    aprobar_plantilla,
    registrar_plantillas,
    reponer_parametricos,
    stock_por_celda,
)
from tutor.modelos import Ejercicio, Plantilla


@pytest.fixture
def banco(sesion):
    cargar_catalogo(sesion, leer_catalogo(RUTA_POR_DEFECTO))
    registrar_plantillas(sesion)
    return sesion


def test_sin_aprobar_no_se_genera_nada(banco):
    assert reponer_parametricos(banco, random.Random(1)) == {}
    assert stock_por_celda(banco) == {}


def test_una_plantilla_aprobada_llena_sus_tres_celdas(banco):
    aprobar_plantilla(banco, "5B-OA4-div-resto", revisor="Equipo")

    agregados = reponer_parametricos(banco, random.Random(1))

    esperado = {("5B-OA4", n): STOCK_OBJETIVO for n in (1, 2, 3)}
    assert agregados == esperado
    assert stock_por_celda(banco) == esperado
    ejercicio = banco.scalars(select(Ejercicio)).first()
    assert ejercicio.fuente == "parametrica" and ejercicio.estado == "activo"
    assert ejercicio.plantilla_id == "5B-OA4-div-resto" and len(ejercicio.pistas) == 3


def test_reponer_solo_completa_lo_que_falta_y_sin_repetir(banco):
    aprobar_plantilla(banco, "4B-OA9-suma-igual-den", revisor="Equipo")
    reponer_parametricos(banco, random.Random(2))

    assert reponer_parametricos(banco, random.Random(3)) == {}  # nada nuevo que agregar
    for nivel in (1, 2, 3):
        enunciados = banco.scalars(
            select(Ejercicio.enunciado).where(
                Ejercicio.unidad_id == "4B-OA9", Ejercicio.nivel == nivel
            )
        ).all()
        assert len(enunciados) == len(set(enunciados))  # nunca repite un enunciado
        assert len(enunciados) <= STOCK_OBJETIVO


def test_una_celda_con_pocos_ejercicios_posibles_no_se_rellena_con_repetidos(banco):
    """Límite del diseño (§4.2): en el nivel 1 de 4B-OA9 (denominador ≤ 4 y resultado propio)
    solo existen 4 ejercicios distintos, menos que el stock objetivo de 5."""
    aprobar_plantilla(banco, "4B-OA9-suma-igual-den", revisor="Equipo")
    reponer_parametricos(banco, random.Random(4))

    assert stock_por_celda(banco)[("4B-OA9", 1)] == 4


def test_cambiar_la_version_obliga_a_aprobar_de_nuevo(banco):
    aprobar_plantilla(banco, "5B-OA4-div-resto", revisor="Equipo")
    banco.get(Plantilla, "5B-OA4-div-resto").version = 0  # simula que el código avanzó de versión
    banco.commit()

    registrar_plantillas(banco)

    fila = banco.get(Plantilla, "5B-OA4-div-resto")
    banco.refresh(fila)
    assert fila.version == 1 and not fila.aprobada


def test_aprobar_una_plantilla_inexistente(banco):
    with pytest.raises(ValueError, match="No existe"):
        aprobar_plantilla(banco, "no-existe", revisor="Equipo")
