"""Registro e ingreso (CU-1, CU-9; RF-A1–A3, RNF-S1).

El apoderado inicia sesión una vez por dispositivo con correo y contraseña. La respuesta trae,
además del token del panel, un token de dispositivo de larga duración que solo sirve para:

- entrar como el estudiante, sin PIN (el niño toca su perfil), y
- abrir el panel del apoderado con su PIN de 4 números.

Así el niño no necesita PIN y el apoderado no escribe su contraseña cada vez (RF-A3).
"""

from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from tutor.config import get_settings
from tutor.esquemas import (
    ApoderadoCreado,
    IngresoApoderado,
    IngresoConDispositivo,
    PinPanel,
    RegistroApoderado,
    Token,
)
from tutor.modelos import Apoderado
from tutor.seguridad import ApoderadoDelDispositivo, SesionBD, crear_token, hashear, verificar

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
    apoderado = Apoderado(
        email=datos.email, password_hash=hashear(datos.contrasena), pin_hash=hashear(datos.pin)
    )
    sesion.add(apoderado)
    sesion.commit()
    return apoderado


@router.post("/apoderado/login", response_model=IngresoConDispositivo)
def ingresar_apoderado(datos: IngresoApoderado, sesion: SesionBD) -> IngresoConDispositivo:
    apoderado = sesion.scalar(select(Apoderado).where(Apoderado.email == datos.email))
    valido = verificar(datos.contrasena, apoderado.password_hash if apoderado else _HASH_RELLENO)
    if apoderado is None or not valido:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Correo o contraseña incorrectos.")
    return IngresoConDispositivo(
        token=crear_token(apoderado.id, "apoderado"),
        rol="apoderado",
        token_dispositivo=crear_token(apoderado.id, "dispositivo"),
    )


@router.post("/dispositivo/estudiante", response_model=Token)
def entrar_como_estudiante(apoderado: ApoderadoDelDispositivo) -> Token:
    """El estudiante toca su perfil en un dispositivo vinculado y entra sin PIN (RF-A3)."""
    if apoderado.estudiante is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Todavía no hay un perfil de estudiante.")
    return Token(token=crear_token(apoderado.estudiante.id, "estudiante"), rol="estudiante")


@router.post("/dispositivo/apoderado", response_model=Token)
def abrir_panel(datos: PinPanel, apoderado: ApoderadoDelDispositivo, sesion: SesionBD) -> Token:
    """PIN del panel. Tras varios PIN incorrectos el panel se bloquea unos minutos: un PIN de
    4 dígitos sin bloqueo se adivina en poco tiempo (modelo_base_datos.md §1)."""
    panel = Token(token=crear_token(apoderado.id, "apoderado"), rol="apoderado")
    if apoderado.pin_hash is None:
        return panel  # cuenta anterior al cambio, sin PIN fijado (ver la migración)

    ajustes = get_settings()
    ahora = datetime.now(UTC)
    if apoderado.bloqueado_hasta and apoderado.bloqueado_hasta > ahora:
        raise HTTPException(status.HTTP_423_LOCKED, PIN_BLOQUEADO)

    if verificar(datos.pin, apoderado.pin_hash):
        apoderado.pin_fallos = 0
        apoderado.bloqueado_hasta = None
        sesion.commit()
        return panel

    apoderado.pin_fallos += 1
    if apoderado.pin_fallos >= ajustes.pin_max_fallos:
        apoderado.pin_fallos = 0
        apoderado.bloqueado_hasta = ahora + timedelta(minutes=ajustes.pin_minutos_bloqueo)
        sesion.commit()
        raise HTTPException(status.HTTP_423_LOCKED, PIN_BLOQUEADO)
    sesion.commit()
    raise HTTPException(status.HTTP_401_UNAUTHORIZED, PIN_INCORRECTO)
