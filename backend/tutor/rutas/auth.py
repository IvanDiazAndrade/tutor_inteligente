"""Registro e ingreso (CU-1, CU-9; RF-A1–A3, RNF-S1)."""

from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from tutor.config import get_settings
from tutor.esquemas import (
    ApoderadoCreado,
    IngresoApoderado,
    IngresoEstudiante,
    RegistroApoderado,
    Token,
)
from tutor.modelos import Apoderado, Estudiante
from tutor.seguridad import SesionBD, crear_token, hashear, verificar

router = APIRouter(prefix="/auth", tags=["autenticación"])

PIN_INCORRECTO = "Ese PIN no es. Prueba otra vez."
PIN_BLOQUEADO = "Espera un momento e intenta otra vez."

# Hash de relleno: si el correo no existe se verifica igual, para que el tiempo de respuesta
# no revele qué correos están registrados.
_HASH_RELLENO = hashear("relleno-para-igualar-tiempos")


@router.post(
    "/apoderado/registro", status_code=status.HTTP_201_CREATED, response_model=ApoderadoCreado
)
def registrar_apoderado(datos: RegistroApoderado, sesion: SesionBD) -> Apoderado:
    if sesion.scalar(select(Apoderado).where(Apoderado.email == datos.email)):
        raise HTTPException(status.HTTP_409_CONFLICT, "Ese correo ya tiene una cuenta.")
    apoderado = Apoderado(email=datos.email, password_hash=hashear(datos.contrasena))
    sesion.add(apoderado)
    sesion.commit()
    return apoderado


@router.post("/apoderado/login", response_model=Token)
def ingresar_apoderado(datos: IngresoApoderado, sesion: SesionBD) -> Token:
    apoderado = sesion.scalar(select(Apoderado).where(Apoderado.email == datos.email))
    valido = verificar(datos.contrasena, apoderado.password_hash if apoderado else _HASH_RELLENO)
    if apoderado is None or not valido:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Correo o contraseña incorrectos.")
    return Token(token=crear_token(apoderado.id, "apoderado"), rol="apoderado")


@router.post("/estudiante/login", response_model=Token)
def ingresar_estudiante(datos: IngresoEstudiante, sesion: SesionBD) -> Token:
    """Perfil + PIN (RF-A3). Tras varios PIN incorrectos el perfil se bloquea unos minutos:
    un PIN de 4 dígitos sin bloqueo se adivina en poco tiempo (modelo_base_datos.md §1)."""
    ajustes = get_settings()
    ahora = datetime.now(UTC)
    estudiante = sesion.get(Estudiante, datos.estudiante_id)
    if estudiante is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, PIN_INCORRECTO)
    if estudiante.bloqueado_hasta and estudiante.bloqueado_hasta > ahora:
        raise HTTPException(status.HTTP_423_LOCKED, PIN_BLOQUEADO)

    if verificar(datos.pin, estudiante.pin_hash):
        estudiante.pin_fallos = 0
        estudiante.bloqueado_hasta = None
        sesion.commit()
        return Token(token=crear_token(estudiante.id, "estudiante"), rol="estudiante")

    estudiante.pin_fallos += 1
    if estudiante.pin_fallos >= ajustes.pin_max_fallos:
        estudiante.pin_fallos = 0
        estudiante.bloqueado_hasta = ahora + timedelta(minutes=ajustes.pin_minutos_bloqueo)
        sesion.commit()
        raise HTTPException(status.HTTP_423_LOCKED, PIN_BLOQUEADO)
    sesion.commit()
    raise HTTPException(status.HTTP_401_UNAUTHORIZED, PIN_INCORRECTO)
