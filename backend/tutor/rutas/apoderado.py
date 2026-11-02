"""Gestión de la cuenta por el apoderado: perfil del estudiante y PIN del panel
(CU-9; RF-A1, A3, A4, A5)."""

from fastapi import APIRouter, HTTPException, status

from tutor.esquemas import EstudianteCambios, EstudianteNuevo, PerfilEstudiante, PinPanel
from tutor.modelos import Estudiante
from tutor.seguridad import ApoderadoActual, SesionBD, hashear

router = APIRouter(prefix="/apoderado", tags=["apoderado"])

SIN_PERFIL = HTTPException(status.HTTP_404_NOT_FOUND, "Todavía no hay un perfil de estudiante.")


@router.post("/estudiante", status_code=status.HTTP_201_CREATED, response_model=PerfilEstudiante)
def crear_estudiante(
    datos: EstudianteNuevo, apoderado: ApoderadoActual, sesion: SesionBD
) -> Estudiante:
    if apoderado.estudiante is not None:
        # Un apoderado, un estudiante (RF-A1, por ratificar con el equipo).
        raise HTTPException(status.HTTP_409_CONFLICT, "La cuenta ya tiene un estudiante.")
    estudiante = Estudiante(apoderado=apoderado, alias=datos.alias, curso=datos.curso)
    sesion.add(estudiante)
    sesion.commit()
    return estudiante


@router.get("/estudiante", response_model=PerfilEstudiante)
def ver_estudiante(apoderado: ApoderadoActual) -> Estudiante:
    if apoderado.estudiante is None:
        raise SIN_PERFIL
    return apoderado.estudiante


@router.patch("/estudiante", response_model=PerfilEstudiante)
def editar_estudiante(
    cambios: EstudianteCambios, apoderado: ApoderadoActual, sesion: SesionBD
) -> Estudiante:
    estudiante = apoderado.estudiante
    if estudiante is None:
        raise SIN_PERFIL
    if cambios.alias is not None:
        estudiante.alias = cambios.alias
    if cambios.curso is not None:
        # El historial (intentos, dominio por OA) se conserva al cambiar de curso (RF-A4).
        estudiante.curso = cambios.curso
    sesion.commit()
    return estudiante


@router.put("/pin", status_code=status.HTTP_204_NO_CONTENT)
def cambiar_pin(datos: PinPanel, apoderado: ApoderadoActual, sesion: SesionBD) -> None:
    """Fija o cambia el PIN del panel (RF-A3). Exige estar en el panel: ya se pidió el PIN
    actual (o la contraseña) para llegar aquí."""
    apoderado.pin_hash = hashear(datos.pin)
    apoderado.pin_fallos = 0
    apoderado.bloqueado_hasta = None
    sesion.commit()
