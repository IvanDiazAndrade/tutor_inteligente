"""Servir y resolver ejercicios: flujos F1, F2, F3 y RF-P7 (docs/diagramas_secuencia.md).

Reúne el banco (F1), el corrector (AD-2), el motor adaptativo y la gamificación. Los mensajes
del tutor son por ahora los locales (tutor/mensajes.py); el LLM se agrega en las tareas 55 y 59
sin cambiar este flujo.
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from tutor import mensajes
from tutor.config import get_settings
from tutor.dominio.corrector import corregir
from tutor.esquemas import (
    EjercicioParaEstudiante,
    ExplicacionGuiada,
    PistaTutor,
    RespuestaTutor,
)
from tutor.modelos import (
    DominioOA,
    Ejercicio,
    EjercicioServido,
    Estudiante,
    Intento,
    Sesion,
    Unidad,
)
from tutor.motor import ESTADO_INICIAL, EstadoMotor, registrar_intento


class NoEncontrado(Exception):
    pass


class SinEjercicios(Exception):
    """La celda unidad × nivel no tiene ejercicios activos (la repone F5)."""


class NoPermitido(Exception):
    """La acción no corresponde al estado del ejercicio (p. ej., ya resuelto)."""


def puntos_por(nivel: int, pistas: int) -> int:
    """Puntos provisorios (RF-G1): 10 por nivel, con el mismo descuento por pista que el índice
    (−15 % por pista, piso 40 %). La fórmula definitiva se fija con la gamificación (tarea 64)."""
    return round(10 * nivel * max(0.4, 1 - 0.15 * pistas))


# Servir (F1) -----------------------------------------------------------------------------


def _sesion_abierta(sesion: Session, estudiante: Estudiante) -> Sesion:
    abierta = sesion.scalar(
        select(Sesion)
        .where(Sesion.estudiante_id == estudiante.id, Sesion.fin.is_(None))
        .order_by(Sesion.inicio.desc())
    )
    if abierta is None:
        abierta = Sesion(estudiante_id=estudiante.id)
        sesion.add(abierta)
        sesion.flush()
    return abierta


def _dominio(sesion: Session, estudiante: Estudiante, unidad_id: str) -> DominioOA:
    dominio = sesion.get(DominioOA, (estudiante.id, unidad_id))
    if dominio is None:
        # Arranque en frío (modelo_estudiante.md §4): nivel 2, índice 0,5.
        dominio = DominioOA(
            estudiante_id=estudiante.id,
            unidad_id=unidad_id,
            indice=ESTADO_INICIAL.indice,
            nivel_actual=ESTADO_INICIAL.nivel,
            racha_correctas=0,
            intentos_en_unidad=0,
        )
        sesion.add(dominio)
        sesion.flush()
    return dominio


def _elegir(
    sesion: Session, estudiante_id: uuid.UUID, unidad_id: str, nivel: int, excluir=None
) -> Ejercicio | None:
    """Un ejercicio activo no visto de la celda; si ya vio todos, el visto hace más tiempo
    (modelo_estudiante.md §7). Nunca un gold."""
    ultimo_visto = (
        select(func.max(EjercicioServido.servido_en))
        .where(
            EjercicioServido.estudiante_id == estudiante_id,
            EjercicioServido.ejercicio_id == Ejercicio.id,
        )
        .scalar_subquery()
    )
    consulta = (
        select(Ejercicio)
        .where(
            Ejercicio.unidad_id == unidad_id,
            Ejercicio.nivel == nivel,
            Ejercicio.estado == "activo",
            Ejercicio.fuente != "gold",
        )
        .order_by(ultimo_visto.asc().nulls_first(), func.random())
        .limit(1)
    )
    if excluir is not None:
        consulta = consulta.where(Ejercicio.id != excluir)
    return sesion.scalar(consulta)


def _para_estudiante(servido: EjercicioServido, ejercicio: Ejercicio, unidad: Unidad):
    return EjercicioParaEstudiante(
        servido_id=servido.id,
        unidad_id=unidad.id,
        unidad_descripcion=unidad.descripcion_ciudadana,
        nivel=servido.nivel,
        enunciado=ejercicio.enunciado,
        representacion=ejercicio.representacion,
        formato_respuesta=ejercicio.formato_respuesta,
        pistas_restantes=get_settings().max_pistas - servido.pistas_usadas,
    )


def servir(sesion: Session, estudiante: Estudiante, unidad_id: str) -> EjercicioParaEstudiante:
    unidad = sesion.get(Unidad, unidad_id)
    if unidad is None or not unidad.activa or unidad.curso > estudiante.curso:
        raise NoEncontrado("Unidad no encontrada.")
    practica = _sesion_abierta(sesion, estudiante)
    # "Otro ejercicio" o volver a elegir unidad: lo que quedó en curso pasa a abandonado,
    # sin penalizar el índice (sin respuesta no hay evidencia; modelo_pedagogico.md §2).
    sesion.execute(
        update(EjercicioServido)
        .where(
            EjercicioServido.estudiante_id == estudiante.id,
            EjercicioServido.estado == "en_curso",
        )
        .values(estado="abandonado", terminado_en=datetime.now(UTC))
    )
    nivel = _dominio(sesion, estudiante, unidad_id).nivel_actual
    ejercicio = _elegir(sesion, estudiante.id, unidad_id, nivel)
    if ejercicio is None:
        raise SinEjercicios("Todavía no hay ejercicios para esta unidad.")
    servido = EjercicioServido(
        sesion_id=practica.id,
        estudiante_id=estudiante.id,
        ejercicio_id=ejercicio.id,
        nivel=nivel,
        pistas_usadas=0,
        fallos=0,
    )
    sesion.add(servido)
    sesion.commit()
    return _para_estudiante(servido, ejercicio, unidad)


# Responder (F2) --------------------------------------------------------------------------


def _servido_en_curso(
    sesion: Session, estudiante: Estudiante, servido_id: uuid.UUID
) -> EjercicioServido:
    servido = sesion.get(EjercicioServido, servido_id)
    if servido is None or servido.estudiante_id != estudiante.id:
        raise NoEncontrado("Ejercicio no encontrado.")
    if servido.estado != "en_curso":
        raise NoPermitido("Este ejercicio ya terminó.")
    return servido


def responder(
    sesion: Session,
    estudiante: Estudiante,
    servido_id: uuid.UUID,
    respuesta: str,
    tiempo_segundos: int,
) -> RespuestaTutor:
    ajustes = get_settings()
    servido = _servido_en_curso(sesion, estudiante, servido_id)
    ejercicio = sesion.get(Ejercicio, servido.ejercicio_id)
    resultado = corregir(respuesta, ejercicio)
    restantes = ajustes.max_pistas - servido.pistas_usadas

    if not resultado.cuenta_como_intento:
        return RespuestaTutor(
            resultado="formato_invalido",
            mensaje=resultado.mensaje,
            puntos=0,
            pistas_restantes=restantes,
            ofrece_resolver_juntos=servido.fallos >= ajustes.fallos_para_resolver_juntos,
            cambio_nivel=None,
            degradado=True,
        )

    ahora = datetime.now(UTC)
    correcta = resultado.estado == "correcta"
    puntos = puntos_por(servido.nivel, servido.pistas_usadas) if correcta else 0
    sesion.add(
        Intento(
            ejercicio_servido_id=servido.id,
            estudiante_id=estudiante.id,
            respuesta=respuesta,
            es_correcta=correcta,
            pistas_usadas=servido.pistas_usadas,
            patron_error=resultado.error_comun["causa"] if resultado.error_comun else None,
            tiempo_segundos=tiempo_segundos,
            puntos=puntos,
        )
    )

    # Motor adaptativo: índice, racha y nivel de la unidad (modelo_estudiante.md §2-3).
    dominio = _dominio(sesion, estudiante, ejercicio.unidad_id)
    estado, cambio = registrar_intento(
        EstadoMotor(
            dominio.indice,
            dominio.nivel_actual,
            dominio.racha_correctas,
            dominio.intentos_en_unidad,
        ),
        correcta,
        servido.pistas_usadas,
        ahora,
    )
    dominio.indice = estado.indice
    dominio.nivel_actual = estado.nivel
    dominio.racha_correctas = estado.racha
    dominio.intentos_en_unidad = estado.intentos
    dominio.fecha_ultimo_intento = ahora

    if correcta:
        servido.estado = "resuelto"
        servido.terminado_en = ahora
        estudiante.puntaje_total += puntos
        practica = sesion.get(Sesion, servido.sesion_id)
        practica.puntaje_obtenido += puntos
        mensaje = mensajes.refuerzo(estado.racha, cambio == "sube")
        if resultado.forma_distinta:
            mensaje += " " + mensajes.forma_canonica(ejercicio.respuesta_final)
        mensaje += f" Ganaste {puntos} puntos."
    else:
        servido.fallos += 1
        mensaje = mensajes.error_local(
            resultado.error_comun, ejercicio.solucion_referencia, ejercicio.respuesta_final
        )
    sesion.commit()
    return RespuestaTutor(
        resultado=resultado.estado,
        mensaje=mensaje,
        puntos=puntos,
        pistas_restantes=restantes,
        ofrece_resolver_juntos=(
            not correcta and servido.fallos >= ajustes.fallos_para_resolver_juntos
        ),
        cambio_nivel=cambio,
        degradado=True,
    )


# Pistas (F3) y "No entiendo" ---------------------------------------------------------------


def pedir_pista(sesion: Session, estudiante: Estudiante, servido_id: uuid.UUID) -> PistaTutor:
    ajustes = get_settings()
    servido = _servido_en_curso(sesion, estudiante, servido_id)
    if servido.pistas_usadas >= ajustes.max_pistas:
        raise NoPermitido("Ya usaste todas las pistas de este ejercicio.")
    ejercicio = sesion.get(Ejercicio, servido.ejercicio_id)
    servido.pistas_usadas += 1  # el descuento se aplica al responder (RF-G1, §1 del modelo)
    numero = servido.pistas_usadas
    texto = mensajes.sin_revelar(ejercicio.pistas[numero - 1], ejercicio.respuesta_final)
    sesion.commit()
    return PistaTutor(
        numero=numero,
        mensaje=f"Pista {numero}: {texto}",
        pistas_restantes=ajustes.max_pistas - numero,
    )


def no_entiendo(sesion: Session, estudiante: Estudiante, servido_id: uuid.UUID) -> str:
    """Re-explicación: no descuenta (pedir aclaración no es pedir ayuda extra)."""
    servido = _servido_en_curso(sesion, estudiante, servido_id)
    ejercicio = sesion.get(Ejercicio, servido.ejercicio_id)
    return mensajes.reexplicacion_local(ejercicio.pistas, ejercicio.respuesta_final)


# Resolvamos juntos (RF-P7) -----------------------------------------------------------------


def resolver_juntos(
    sesion: Session, estudiante: Estudiante, servido_id: uuid.UUID
) -> ExplicacionGuiada:
    """Tras N fallos: se narra la solución del ejercicio original (ahí sí puede verse su
    respuesta) y se sirve un análogo de la misma celda, que cuenta como intento normal. El
    original se cierra sin más penalización: los fallos ya movieron el índice."""
    ajustes = get_settings()
    servido = _servido_en_curso(sesion, estudiante, servido_id)
    if servido.fallos < ajustes.fallos_para_resolver_juntos:
        raise NoPermitido("Primero intenta resolverlo.")
    ejercicio = sesion.get(Ejercicio, servido.ejercicio_id)
    servido.estado = "explicado"
    servido.terminado_en = datetime.now(UTC)

    unidad = sesion.get(Unidad, ejercicio.unidad_id)
    nivel = _dominio(sesion, estudiante, unidad.id).nivel_actual
    analogo = _elegir(sesion, estudiante.id, unidad.id, nivel, excluir=ejercicio.id)
    para_estudiante = None
    if analogo is not None:
        nuevo = EjercicioServido(
            sesion_id=servido.sesion_id,
            estudiante_id=estudiante.id,
            ejercicio_id=analogo.id,
            nivel=nivel,
            pistas_usadas=0,
            fallos=0,
            analogo_de=servido.id,
        )
        sesion.add(nuevo)
        sesion.flush()
        para_estudiante = _para_estudiante(nuevo, analogo, unidad)
    sesion.commit()
    return ExplicacionGuiada(pasos=list(ejercicio.solucion_referencia), analogo=para_estudiante)
