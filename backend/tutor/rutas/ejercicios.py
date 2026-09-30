"""Rutas del ejercicio: servir, responder, pistas, no entiendo y resolvamos juntos
(docs/diagramas_secuencia.md §1 y §3-6)."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from tutor import ejercicios
from tutor.esquemas import (
    EjercicioParaEstudiante,
    ExplicacionGuiada,
    PistaTutor,
    RespuestaEstudiante,
    RespuestaTutor,
)
from tutor.llm.adaptador import AdaptadorLLM, get_adaptador
from tutor.seguridad import EstudianteActual, SesionBD

# Sin OPENAI_API_KEY el adaptador existe pero sin proveedor: todo responde en modo local.
LLM = Annotated[AdaptadorLLM, Depends(get_adaptador)]

router = APIRouter(prefix="/estudiante", tags=["ejercicios"])


def _http(error: Exception) -> HTTPException:
    codigo = {
        ejercicios.NoEncontrado: status.HTTP_404_NOT_FOUND,
        ejercicios.SinEjercicios: status.HTTP_404_NOT_FOUND,
        ejercicios.NoPermitido: status.HTTP_409_CONFLICT,
    }[type(error)]
    return HTTPException(codigo, str(error))


ERRORES = (ejercicios.NoEncontrado, ejercicios.SinEjercicios, ejercicios.NoPermitido)


class Mensaje(BaseModel):
    mensaje: str


@router.post(
    "/unidades/{unidad_id}/ejercicio",
    status_code=status.HTTP_201_CREATED,
    response_model=EjercicioParaEstudiante,
)
def servir(unidad_id: str, estudiante: EstudianteActual, sesion: SesionBD):
    try:
        return ejercicios.servir(sesion, estudiante, unidad_id)
    except ERRORES as error:
        raise _http(error) from error


@router.post("/servidos/{servido_id}/respuestas", response_model=RespuestaTutor)
def responder(
    servido_id: uuid.UUID,
    datos: RespuestaEstudiante,
    estudiante: EstudianteActual,
    sesion: SesionBD,
    llm: LLM,
):
    try:
        return ejercicios.responder(
            sesion, estudiante, servido_id, datos.respuesta, datos.tiempo_segundos, llm
        )
    except ERRORES as error:
        raise _http(error) from error


@router.post("/servidos/{servido_id}/pistas", response_model=PistaTutor)
def pedir_pista(servido_id: uuid.UUID, estudiante: EstudianteActual, sesion: SesionBD, llm: LLM):
    try:
        return ejercicios.pedir_pista(sesion, estudiante, servido_id, llm)
    except ERRORES as error:
        raise _http(error) from error


@router.post("/servidos/{servido_id}/no-entiendo", response_model=Mensaje)
def no_entiendo(servido_id: uuid.UUID, estudiante: EstudianteActual, sesion: SesionBD, llm: LLM):
    try:
        return Mensaje(mensaje=ejercicios.no_entiendo(sesion, estudiante, servido_id, llm))
    except ERRORES as error:
        raise _http(error) from error


@router.post("/servidos/{servido_id}/resolver-juntos", response_model=ExplicacionGuiada)
def resolver_juntos(
    servido_id: uuid.UUID, estudiante: EstudianteActual, sesion: SesionBD, llm: LLM
):
    try:
        return ejercicios.resolver_juntos(sesion, estudiante, servido_id, llm)
    except ERRORES as error:
        raise _http(error) from error
