"""Gestión de la cuenta por el apoderado: perfiles de estudiante y PIN del panel
(CU-9; RF-A1, A3, A4, A5)."""

import uuid

from fastapi import APIRouter, HTTPException, status

from tutor.config import get_settings
from tutor.esquemas import EstudianteCambios, EstudianteNuevo, PerfilEstudiante, PinPanel
from tutor.modelos import Apoderado, Estudiante
from tutor.seguridad import ApoderadoActual, SesionBD, hashear

router = APIRouter(prefix="/apoderado", tags=["apoderado"])


def estudiante_de(apoderado: Apoderado, estudiante_id: uuid.UUID) -> Estudiante:
    """Un estudiante de la cuenta; si no es de ella, 404 (no se distingue de uno inexistente)."""
    for estudiante in apoderado.estudiantes:
        if estudiante.id == estudiante_id:
            return estudiante
    raise HTTPException(status.HTTP_404_NOT_FOUND, "Ese perfil no es de esta cuenta.")


@router.get("/estudiantes", response_model=list[PerfilEstudiante])
def ver_estudiantes(apoderado: ApoderadoActual) -> list[Estudiante]:
    """Los perfiles de la cuenta, en el orden en que se crearon."""
    return apoderado.estudiantes


@router.post("/estudiantes", status_code=status.HTTP_201_CREATED, response_model=PerfilEstudiante)
def crear_estudiante(
    datos: EstudianteNuevo, apoderado: ApoderadoActual, sesion: SesionBD
) -> Estudiante:
    maximo = get_settings().max_estudiantes
    if len(apoderado.estudiantes) >= maximo:
        raise HTTPException(
            status.HTTP_409_CONFLICT, f"Una cuenta puede tener hasta {maximo} estudiantes."
        )
    estudiante = Estudiante(apoderado=apoderado, alias=datos.alias, curso=datos.curso)
    sesion.add(estudiante)
    sesion.commit()
    return estudiante


@router.patch("/estudiantes/{estudiante_id}", response_model=PerfilEstudiante)
def editar_estudiante(
    estudiante_id: uuid.UUID,
    cambios: EstudianteCambios,
    apoderado: ApoderadoActual,
    sesion: SesionBD,
) -> Estudiante:
    estudiante = estudiante_de(apoderado, estudiante_id)
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
