from pathlib import Path

import pytest
from sqlalchemy import func, select

from tutor.catalogo import RUTA_POR_DEFECTO, cargar_catalogo, leer_catalogo
from tutor.modelos import Unidad


def test_el_archivo_tiene_las_24_unidades_del_anillo_1():
    unidades = leer_catalogo(RUTA_POR_DEFECTO)

    por_curso = {c: [u.id for u in unidades if u.curso == c] for c in (4, 5, 6)}
    assert len(unidades) == 24
    assert len(por_curso[4]) == 8 and len(por_curso[5]) == 11 and len(por_curso[6]) == 5
    # Orden correlativo dentro de cada curso.
    for curso in (4, 5, 6):
        ordenes = sorted(u.orden for u in unidades if u.curso == curso)
        assert ordenes == list(range(1, len(ordenes) + 1))


def test_ids_repetidos_se_rechazan(tmp_path: Path):
    archivo = tmp_path / "catalogo.yaml"
    entrada = """
  - id: 4B-OA1
    curso: 4
    orden: 1
    basal: true
    oa_texto_oficial: texto
    descripcion_ciudadana: texto
    rango_numerico: {}"""
    archivo.write_text("unidades:" + entrada + entrada, encoding="utf-8")

    with pytest.raises(ValueError, match="repetidos"):
        leer_catalogo(archivo)


def test_la_carga_es_idempotente(sesion):
    unidades = leer_catalogo(RUTA_POR_DEFECTO)

    cargar_catalogo(sesion, unidades)
    cargar_catalogo(sesion, unidades)

    assert sesion.scalar(select(func.count()).select_from(Unidad)) == 24
    assert sesion.get(Unidad, "5B-OA7").descripcion_ciudadana == "Fracciones equivalentes"
