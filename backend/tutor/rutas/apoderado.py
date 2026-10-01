"""Rutas del apoderado: perfil del estudiante (CU-9; RF-A1, A4, A5) y panel (CU-10)."""

from fastapi import APIRouter, HTTPException, status

from tutor import dashboard
from tutor.esquemas import EstudianteCambios, EstudianteNuevo, PanelApoderado, PerfilEstudiante
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
    estudiante = Estudiante(
        apoderado=apoderado, alias=datos.alias, curso=datos.curso, pin_hash=hashear(datos.pin)
    )
    sesion.add(estudiante)
    sesion.commit()
    return estudiante


@router.get("/estudiante", response_model=PerfilEstudiante)
def ver_estudiante(apoderado: ApoderadoActual) -> Estudiante:
    if apoderado.estudiante is None:
        raise SIN_PERFIL
    return apoderado.estudiante


@router.get("/dashboard", response_model=PanelApoderado)
def ver_dashboard(apoderado: ApoderadoActual, sesion: SesionBD) -> PanelApoderado:
    """Panel de progreso (CU-10, F4): agregación determinista, sin LLM."""
    if apoderado.estudiante is None:
        raise SIN_PERFIL
    return dashboard.panel(sesion, apoderado.estudiante)


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
    if cambios.pin is not None:
        estudiante.pin_hash = hashear(cambios.pin)
        estudiante.pin_fallos = 0
        estudiante.bloqueado_hasta = None
    sesion.commit()
    return estudiante
