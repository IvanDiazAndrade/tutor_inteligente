"""Lecciones breves por unidad (RF-D9).

Son contenido estático, igual para todos los estudiantes: se leen de datos/lecciones_anillo1.yaml
la primera vez que se piden y no van a la base de datos. Cambiar un texto es editar el archivo y
reiniciar el servidor (RNF-M2).
"""

from functools import cache
from pathlib import Path

import yaml
from pydantic import BaseModel, Field

RUTA_POR_DEFECTO = Path(__file__).resolve().parent.parent / "datos" / "lecciones_anillo1.yaml"


class Parte(BaseModel):
    titulo: str = Field(min_length=1)
    explicacion: str = Field(min_length=1)
    practica: str = Field(min_length=1)


class Leccion(BaseModel):
    unidad_id: str = Field(pattern=r"^[4-6]B-OA\d{1,2}$")
    titulo: str = Field(min_length=1)
    resumen: str = Field(min_length=1)
    partes: list[Parte] = Field(min_length=2, max_length=5)
    revisado_por: str | None = None  # null mientras el equipo no la revise (borrador)


def leer_lecciones(ruta: Path = RUTA_POR_DEFECTO) -> dict[str, Leccion]:
    """Lecciones por id de unidad. Falla si el archivo es inválido o repite una unidad."""
    datos = yaml.safe_load(ruta.read_text(encoding="utf-8"))
    lecciones = [Leccion.model_validate(x) for x in datos["lecciones"]]
    ids = [x.unidad_id for x in lecciones]
    if len(ids) != len(set(ids)):
        raise ValueError("Hay unidades con más de una lección.")
    return {x.unidad_id: x for x in lecciones}


@cache
def lecciones() -> dict[str, Leccion]:
    return leer_lecciones()
