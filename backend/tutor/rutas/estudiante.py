"""Rutas del estudiante: unidades con su progreso y sesiones de práctica (CU-2)."""

import uuid
from datetime import UTC, datetime
from typing import Literal

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from tutor.esquemas import SesionPractica, UnidadEstudiante
from tutor.modelos import DominioOA, Sesion, Unidad
from tutor.progreso import EstadoDominio, estrellas, para_repasar, unidad_sugerida
from tutor.seguridad import EstudianteActual, SesionBD

router = APIRouter(prefix="/estudiante", tags=["estudiante"])


@router.get("/unidades", response_model=list[UnidadEstudiante])
def listar_unidades(estudiante: EstudianteActual, sesion: SesionBD) -> list[UnidadEstudiante]:
    """Unidades de su curso y de los anteriores, nunca de los superiores (modelo_estudiante.md
    §5), con estrellas, etiqueta y la unidad sugerida ya calculadas."""
    ahora = datetime.now(UTC)
    unidades = sesion.scalars(
        select(Unidad)
        .where(Unidad.activa, Unidad.curso <= estudiante.curso)
        .order_by(Unidad.curso, Unidad.orden)
    ).all()
    dominios = {
        d.unidad_id: EstadoDominio(d.indice, d.fecha_ultimo_intento)
        for d in sesion.scalars(select(DominioOA).where(DominioOA.estudiante_id == estudiante.id))
    }
    sugerida = unidad_sugerida(unidades, dominios, ahora, estudiante.curso)
    primera_nueva = next(
        (u for u in unidades if u.curso == estudiante.curso and u.id not in dominios), None
    )

    def etiqueta(u: Unidad) -> Literal["dominada", "repasar", "nueva"] | None:
        d = dominios.get(u.id)
        if para_repasar(d, ahora):
            return "repasar"
        if estrellas(d) == 3:
            return "dominada"
        if primera_nueva is not None and u.id == primera_nueva.id:
            return "nueva"
        return None

    return [
        UnidadEstudiante(
            id=u.id,
            curso=u.curso,
            descripcion=u.descripcion_ciudadana,
            estrellas=estrellas(dominios.get(u.id)),
            etiqueta=etiqueta(u),
            sugerida=sugerida is not None and u.id == sugerida.id,
        )
        for u in unidades
    ]


@router.post("/sesiones", status_code=status.HTTP_201_CREATED, response_model=SesionPractica)
def abrir_sesion(estudiante: EstudianteActual, sesion: SesionBD) -> Sesion:
    nueva = Sesion(estudiante_id=estudiante.id)
    sesion.add(nueva)
    sesion.commit()
    sesion.refresh(nueva)
    return nueva


@router.post("/sesiones/{sesion_id}/cierre", response_model=SesionPractica)
def cerrar_sesion(sesion_id: uuid.UUID, estudiante: EstudianteActual, sesion: SesionBD) -> Sesion:
    practica = sesion.get(Sesion, sesion_id)
    if practica is None or practica.estudiante_id != estudiante.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Sesión no encontrada.")
    if practica.fin is None:
        practica.fin = datetime.now(UTC)
        sesion.commit()
    return practica
