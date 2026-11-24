"""Lecciones breves por unidad (RF-D9) y unidades con ejercicios disponibles."""

from pathlib import Path

import pytest

from tutor.catalogo import RUTA_POR_DEFECTO as CATALOGO
from tutor.catalogo import leer_catalogo
from tutor.lecciones import leer_lecciones


def test_cada_unidad_del_catalogo_tiene_su_leccion():
    unidades = {u.id for u in leer_catalogo(CATALOGO)}
    lecciones = leer_lecciones()

    assert set(lecciones) == unidades
    assert all(2 <= len(x.partes) <= 4 for x in lecciones.values())


def test_una_unidad_con_dos_lecciones_se_rechaza(tmp_path: Path):
    entrada = """
  - unidad_id: 4B-OA1
    titulo: t
    resumen: r
    partes:
      - {titulo: a, explicacion: b, practica: c}
      - {titulo: a, explicacion: b, practica: c}"""
    archivo = tmp_path / "lecciones.yaml"
    archivo.write_text("lecciones:" + entrada + entrada, encoding="utf-8")

    with pytest.raises(ValueError, match="más de una"):
        leer_lecciones(archivo)


def test_ve_las_lecciones_de_su_curso_y_los_anteriores(cliente, cabecera):
    respuesta = cliente.get("/estudiante/lecciones", headers=cabecera)

    assert respuesta.status_code == 200
    lecciones = respuesta.json()
    assert {x["curso"] for x in lecciones} == {4, 5}
    assert len(lecciones) == 8 + 11
    primera = lecciones[0]
    assert (primera["unidadId"], primera["numero"]) == ("4B-OA1", 1)
    assert set(primera["partes"][0]) == {"titulo", "explicacion", "practica"}
    quinto = [x["numero"] for x in lecciones if x["curso"] == 5]
    assert quinto == list(range(1, 12))


def test_las_unidades_indican_si_ya_tienen_ejercicios(cliente, cabecera):
    unidades = cliente.get("/estudiante/unidades", headers=cabecera).json()

    # El banco de pruebas solo tiene la plantilla de división con resto aprobada.
    assert [u["id"] for u in unidades if u["conEjercicios"]] == ["5B-OA4"]
