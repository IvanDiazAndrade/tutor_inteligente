"""Unidades con progreso y sesiones de práctica (CU-2)."""

import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from tutor.catalogo import RUTA_POR_DEFECTO, cargar_catalogo, leer_catalogo
from tutor.modelos import Apoderado, DominioOA, Estudiante
from tutor.seguridad import crear_token


@pytest.fixture
def estudiante(sesion) -> Estudiante:
    cargar_catalogo(sesion, leer_catalogo(RUTA_POR_DEFECTO))
    estudiante = Estudiante(
        apoderado=Apoderado(email="p@ejemplo.cl", password_hash="x"),
        alias="Vale",
        curso=5,
        pin_hash="x",
    )
    sesion.add(estudiante)
    sesion.commit()
    return estudiante


def _cabecera(estudiante: Estudiante) -> dict[str, str]:
    return {"Authorization": f"Bearer {crear_token(estudiante.id, 'estudiante')}"}


def _dominio(sesion, estudiante, unidad_id: str, indice: str, dias: int) -> None:
    sesion.add(
        DominioOA(
            estudiante_id=estudiante.id,
            unidad_id=unidad_id,
            indice=Decimal(indice),
            fecha_ultimo_intento=datetime.now(UTC) - timedelta(days=dias),
        )
    )
    sesion.commit()


def test_ve_su_curso_y_los_anteriores_pero_no_los_superiores(cliente, estudiante):
    unidades = cliente.get("/estudiante/unidades", headers=_cabecera(estudiante)).json()

    cursos = {u["curso"] for u in unidades}
    assert cursos == {4, 5}
    assert len(unidades) == 8 + 11
    assert unidades[0]["descripcion"] == "Leer y escribir números hasta 10.000"


def test_sin_historial_sugiere_la_primera_unidad_de_su_curso(cliente, estudiante):
    unidades = cliente.get("/estudiante/unidades", headers=_cabecera(estudiante)).json()

    sugeridas = [u for u in unidades if u["sugerida"]]
    assert [u["id"] for u in sugeridas] == ["5B-OA1"]
    assert sugeridas[0]["etiqueta"] == "nueva"
    assert all(u["estrellas"] == 0 for u in unidades)


def test_estrellas_etiquetas_y_sugerencia_segun_el_dominio(cliente, sesion, estudiante):
    _dominio(sesion, estudiante, "5B-OA1", "0.90", dias=2)
    _dominio(sesion, estudiante, "5B-OA7", "0.64", dias=25)  # más de 21 días: para repasar

    por_id = {
        u["id"]: u
        for u in cliente.get("/estudiante/unidades", headers=_cabecera(estudiante)).json()
    }

    assert por_id["5B-OA1"]["estrellas"] == 3 and por_id["5B-OA1"]["etiqueta"] == "dominada"
    assert por_id["5B-OA7"]["estrellas"] == 2 and por_id["5B-OA7"]["etiqueta"] == "repasar"
    assert por_id["5B-OA7"]["sugerida"]
    assert por_id["5B-OA3"]["etiqueta"] == "nueva"


def test_abrir_y_cerrar_una_sesion(cliente, estudiante):
    cabecera = _cabecera(estudiante)
    abierta = cliente.post("/estudiante/sesiones", headers=cabecera)
    assert abierta.status_code == 201 and abierta.json()["fin"] is None

    cerrada = cliente.post(f"/estudiante/sesiones/{abierta.json()['id']}/cierre", headers=cabecera)
    assert cerrada.status_code == 200 and cerrada.json()["fin"] is not None


def test_no_puede_cerrar_una_sesion_ajena(cliente, estudiante):
    ajena = cliente.post(
        f"/estudiante/sesiones/{uuid.uuid4()}/cierre", headers=_cabecera(estudiante)
    )
    assert ajena.status_code == 404


def test_perfil_con_alias_curso_y_puntos(cliente, estudiante):
    perfil = cliente.get("/estudiante/perfil", headers=_cabecera(estudiante)).json()
    assert perfil["alias"] == "Vale" and perfil["curso"] == 5 and perfil["puntajeTotal"] == 0
