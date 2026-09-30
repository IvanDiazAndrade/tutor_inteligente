"""Contratos de la API (Pydantic). En JSON los campos van en camelCase, como en
docs/diagramas_secuencia.md §1; la app genera sus tipos desde el OpenAPI de FastAPI.
"""

import uuid
from datetime import datetime
from typing import Annotated, Literal

from pydantic import AfterValidator, BaseModel, ConfigDict, Field, StringConstraints
from pydantic.alias_generators import to_camel

from tutor.seguridad import MAX_BYTES_BCRYPT


class Esquema(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True)


def _cabe_en_bcrypt(valor: str) -> str:
    if len(valor.encode()) > MAX_BYTES_BCRYPT:
        raise ValueError(f"no puede superar {MAX_BYTES_BCRYPT} bytes")
    return valor


Correo = Annotated[
    str,
    StringConstraints(strip_whitespace=True, max_length=254, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$"),
]
Contrasena = Annotated[str, Field(min_length=8), AfterValidator(_cabe_en_bcrypt)]
Pin = Annotated[str, Field(pattern=r"^\d{4}$")]  # PIN corto definido por el apoderado (RF-A3)
Alias = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=30)]
Curso = Annotated[int, Field(ge=4, le=6)]


# Autenticación ---------------------------------------------------------------------------


class RegistroApoderado(Esquema):
    email: Correo
    contrasena: Contrasena


class IngresoApoderado(Esquema):
    email: Correo
    contrasena: str


class IngresoEstudiante(Esquema):
    estudiante_id: uuid.UUID
    pin: Pin


class Token(Esquema):
    token: str
    rol: Literal["apoderado", "estudiante"]


class ApoderadoCreado(Esquema):
    id: uuid.UUID
    email: str


# Perfil del estudiante (CU-9) ------------------------------------------------------------


class EstudianteNuevo(Esquema):
    """Solo datos mínimos: alias y curso (RF-A5, RNF-S2)."""

    alias: Alias
    curso: Curso
    pin: Pin


class EstudianteCambios(Esquema):
    alias: Alias | None = None
    curso: Curso | None = None  # promover de curso conserva el historial (RF-A4)
    pin: Pin | None = None


class PerfilEstudiante(Esquema):
    """Lo que la app guarda para mostrar el perfil en la pantalla de acceso."""

    id: uuid.UUID
    alias: str
    curso: int
    puntaje_total: int


# Unidades y sesiones (CU-2) --------------------------------------------------------------


class UnidadEstudiante(Esquema):
    id: str
    curso: int
    descripcion: str
    estrellas: int = Field(ge=0, le=3)
    etiqueta: Literal["dominada", "repasar", "nueva"] | None
    sugerida: bool


class SesionPractica(Esquema):
    id: uuid.UUID
    inicio: datetime
    fin: datetime | None
