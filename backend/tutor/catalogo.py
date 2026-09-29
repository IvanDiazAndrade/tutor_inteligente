"""Carga del catálogo curricular desde datos/ (RNF-M2).

Uso: python -m tutor.catalogo [ruta.yaml]

Inserta o actualiza cada unidad por su id, así que se puede ejecutar las veces que haga falta.
No borra unidades que ya no estén en el archivo: para sacar una de la rotación se marca
`activa: false`, porque puede tener intentos y ejercicios asociados.
"""

import sys
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from tutor.db import SessionLocal
from tutor.modelos import Unidad

RUTA_POR_DEFECTO = Path(__file__).resolve().parent.parent / "datos" / "catalogo_anillo1.yaml"


class UnidadCatalogo(BaseModel):
    """Una entrada del archivo; se valida antes de tocar la base de datos."""

    id: str = Field(pattern=r"^[4-6]B-OA\d{1,2}$")
    curso: int = Field(ge=4, le=6)
    orden: int = Field(ge=1)
    basal: bool
    anillo: int = Field(default=1, ge=1, le=2)
    oa_texto_oficial: str = Field(min_length=1)
    descripcion_ciudadana: str = Field(min_length=1)
    rango_numerico: dict[str, Any]
    activa: bool = True


def leer_catalogo(ruta: Path) -> list[UnidadCatalogo]:
    datos = yaml.safe_load(ruta.read_text(encoding="utf-8"))
    unidades = [UnidadCatalogo.model_validate(u) for u in datos["unidades"]]
    ids = [u.id for u in unidades]
    if len(ids) != len(set(ids)):
        raise ValueError("El catálogo tiene ids repetidos.")
    for u in unidades:
        if not u.id.startswith(f"{u.curso}B-"):
            raise ValueError(f"{u.id}: el curso del id no coincide con curso={u.curso}.")
    return unidades


def cargar_catalogo(sesion: Session, unidades: list[UnidadCatalogo]) -> int:
    """Inserta o actualiza las unidades. Devuelve cuántas se procesaron."""
    filas = [u.model_dump() for u in unidades]
    sentencia = insert(Unidad).values(filas)
    sentencia = sentencia.on_conflict_do_update(
        index_elements=[Unidad.id],
        set_={c: sentencia.excluded[c] for c in filas[0] if c != "id"},
    )
    sesion.execute(sentencia)
    sesion.commit()
    return len(filas)


def pendientes_de_transcribir(sesion: Session) -> int:
    return sesion.scalar(
        select(func.count())
        .select_from(Unidad)
        .where(Unidad.oa_texto_oficial.startswith("[TRANSCRIBIR]"))
    )


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")  # tildes correctas en la consola de Windows
    ruta = Path(sys.argv[1]) if len(sys.argv) > 1 else RUTA_POR_DEFECTO
    unidades = leer_catalogo(ruta)
    with SessionLocal() as sesion:
        n = cargar_catalogo(sesion, unidades)
        pendientes = pendientes_de_transcribir(sesion)
    print(f"Catálogo cargado: {n} unidades desde {ruta.name}.")
    if pendientes:
        print(f"Aviso: {pendientes} unidades aún no tienen el texto oficial del OA (RF-D2).")


if __name__ == "__main__":
    main()
