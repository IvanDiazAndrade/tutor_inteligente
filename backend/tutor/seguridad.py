"""Contraseñas, PIN y tokens (RF-A2, RNF-S1).

Contraseñas y PIN se guardan con bcrypt (hash + salt). Los tokens son JWT firmados con
HS256 y llevan solo el id y el rol: ningún dato personal viaja en ellos.
"""

import uuid
from datetime import UTC, datetime, timedelta
from typing import Annotated, Literal

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from tutor.config import get_settings
from tutor.db import get_session
from tutor.modelos import Apoderado, Estudiante

Rol = Literal["apoderado", "estudiante"]
ALGORITMO = "HS256"

# bcrypt solo considera los primeros 72 bytes: se valida el largo antes de llegar aquí.
MAX_BYTES_BCRYPT = 72


def hashear(secreto: str) -> str:
    return bcrypt.hashpw(secreto.encode(), bcrypt.gensalt()).decode()


def verificar(secreto: str, hash_guardado: str) -> bool:
    return bcrypt.checkpw(secreto.encode(), hash_guardado.encode())


def crear_token(sujeto: uuid.UUID, rol: Rol) -> str:
    ajustes = get_settings()
    minutos = (
        ajustes.jwt_minutos_apoderado if rol == "apoderado" else ajustes.jwt_minutos_estudiante
    )
    ahora = datetime.now(UTC)
    carga = {
        "sub": str(sujeto),
        "rol": rol,
        "iat": ahora,
        "exp": ahora + timedelta(minutes=minutos),
    }
    return jwt.encode(carga, ajustes.jwt_secret.get_secret_value(), algorithm=ALGORITMO)


_bearer = HTTPBearer(auto_error=False)

NO_AUTENTICADO = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Hay que iniciar sesión.",
    headers={"WWW-Authenticate": "Bearer"},
)


def _sujeto_del_token(credenciales: HTTPAuthorizationCredentials | None, rol: Rol) -> uuid.UUID:
    if credenciales is None:
        raise NO_AUTENTICADO
    try:
        carga = jwt.decode(
            credenciales.credentials,
            get_settings().jwt_secret.get_secret_value(),
            algorithms=[ALGORITMO],
            options={"require": ["exp", "sub"]},
        )
        sujeto = uuid.UUID(carga["sub"])
    except (jwt.PyJWTError, ValueError, KeyError) as error:
        raise NO_AUTENTICADO from error
    if carga.get("rol") != rol:
        # Un token válido de otro rol: autenticado, pero sin permiso para esta ruta.
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Ruta de otro rol.")
    return sujeto


Credenciales = Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)]
SesionBD = Annotated[Session, Depends(get_session)]


def apoderado_actual(credenciales: Credenciales, sesion: SesionBD) -> Apoderado:
    apoderado = sesion.get(Apoderado, _sujeto_del_token(credenciales, "apoderado"))
    if apoderado is None:
        raise NO_AUTENTICADO
    return apoderado


def estudiante_actual(credenciales: Credenciales, sesion: SesionBD) -> Estudiante:
    estudiante = sesion.get(Estudiante, _sujeto_del_token(credenciales, "estudiante"))
    if estudiante is None:
        raise NO_AUTENTICADO
    return estudiante


ApoderadoActual = Annotated[Apoderado, Depends(apoderado_actual)]
EstudianteActual = Annotated[Estudiante, Depends(estudiante_actual)]
