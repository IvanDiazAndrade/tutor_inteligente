"""Servir y resolver ejercicios: flujos F1, F2, F3 y RF-P7 (docs/diagramas_secuencia.md).

Reúne el banco (F1), el corrector (AD-2), el motor adaptativo y la gamificación. El LLM solo
redacta: la corrección, los puntos y el índice ya están decididos antes de llamarlo. Todo texto
del LLM pasa por los filtros deterministas (§6 de modelo_pedagogico.md) antes de personalizarse
con el alias; si falta la clave, falla o se filtra, se usa el mensaje local (F6).
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
from tutor.llm.adaptador import AdaptadorLLM, ContextoEjercicio, ContextoError, ContextoPista
from tutor.modelos import (
    DominioOA,
    Ejercicio,
    EjercicioServido,
    Estudiante,
    EventoFiltro,
    Intento,
    Sesion,
    Unidad,
)
from tutor.motor import ESTADO_INICIAL, EstadoMotor, registrar_intento
from tutor.progreso import banda


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


# LLM: contexto y filtros --------------------------------------------------------------------


def _contexto(sesion: Session, estudiante: Estudiante, ejercicio: Ejercicio) -> dict:
    """Solo contenido matemático y variables pedagógicas: nada que identifique al niño."""
    dominio = _dominio(sesion, estudiante, ejercicio.unidad_id)
    return dict(
        curso=sesion.get(Unidad, ejercicio.unidad_id).curso,
        enunciado=ejercicio.enunciado,
        solucion=list(ejercicio.solucion_referencia),
        banda=banda(dominio.indice),
        racha=dominio.racha_correctas,
    )


def _filtro(sesion: Session, servido: EjercicioServido, operacion: str, rechaza):
    """Filtro para el adaptador: lo rechazado se registra (evento_filtro) y no se muestra."""

    def aceptable(texto: str) -> bool:
        if rechaza(texto):
            sesion.add(
                EventoFiltro(
                    ejercicio_servido_id=servido.id, operacion=operacion, texto_bloqueado=texto
                )
            )
            return False
        return True

    return aceptable


def _habilitado(adaptador: AdaptadorLLM | None) -> bool:
    return adaptador is not None and adaptador.habilitado


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
    adaptador: AdaptadorLLM | None = None,
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
            degradado=not _habilitado(adaptador),
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
        # El refuerzo es siempre local: la ruta correcta no gasta tokens (§3).
        degradado = not _habilitado(adaptador)
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
        mensaje = None
        if _habilitado(adaptador):
            ctx = ContextoError(
                **_contexto(sesion, estudiante, ejercicio),
                # Solo llega aquí una respuesta que el corrector leyó como número o fracción.
                respuesta_estudiante=respuesta.strip(),
                causa=resultado.error_comun["causa"] if resultado.error_comun else None,
                pistas_vistas=servido.pistas_usadas,
                fallos=servido.fallos,
            )
            aceptable = _filtro(
                sesion,
                servido,
                "generarRetroalimentacion",
                lambda t: mensajes.revela(t, ejercicio.respuesta_final),
            )
            mensaje = adaptador.retroalimentacion(sesion, ctx, servido.sesion_id, aceptable)
        degradado = mensaje is None
        if mensaje is None:
            mensaje = mensajes.error_local(
                resultado.error_comun, ejercicio.solucion_referencia, ejercicio.respuesta_final
            )
        mensaje = mensajes.personalizar(mensaje, estudiante.alias)
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
        degradado=degradado,
    )


# Pistas (F3) y "No entiendo" ---------------------------------------------------------------


def _pista_llm(
    sesion: Session,
    estudiante: Estudiante,
    servido: EjercicioServido,
    ejercicio: Ejercicio,
    adaptador: AdaptadorLLM | None,
    numero: int,
    simplificar: bool,
) -> str | None:
    """Reformula la pista `numero` del banco. Sin números nuevos (no adelanta pasos) y sin
    revelar la respuesta; si no pasa, None y se usa la pista del banco."""
    if not _habilitado(adaptador):
        return None
    vistas = ejercicio.pistas[:numero]
    ctx = ContextoPista(
        **_contexto(sesion, estudiante, ejercicio),
        pista=ejercicio.pistas[numero - 1],
        numero=numero,
        pistas_anteriores=list(vistas[:-1]),
        simplificar=simplificar,
    )
    permitido = " ".join([ejercicio.enunciado, *vistas])
    aceptable = _filtro(
        sesion,
        servido,
        "generarPista",
        lambda t: (
            mensajes.revela(t, ejercicio.respuesta_final) or mensajes.numeros_nuevos(t, permitido)
        ),
    )
    return adaptador.pista(sesion, ctx, servido.sesion_id, aceptable)


def pedir_pista(
    sesion: Session,
    estudiante: Estudiante,
    servido_id: uuid.UUID,
    adaptador: AdaptadorLLM | None = None,
) -> PistaTutor:
    ajustes = get_settings()
    servido = _servido_en_curso(sesion, estudiante, servido_id)
    if servido.pistas_usadas >= ajustes.max_pistas:
        raise NoPermitido("Ya usaste todas las pistas de este ejercicio.")
    ejercicio = sesion.get(Ejercicio, servido.ejercicio_id)
    servido.pistas_usadas += 1  # el descuento se aplica al responder (RF-G1, §1 del modelo)
    numero = servido.pistas_usadas
    texto = _pista_llm(sesion, estudiante, servido, ejercicio, adaptador, numero, False)
    if texto is None:
        texto = mensajes.sin_revelar(ejercicio.pistas[numero - 1], ejercicio.respuesta_final)
    texto = mensajes.personalizar(texto, estudiante.alias)
    sesion.commit()
    return PistaTutor(
        numero=numero,
        mensaje=f"Pista {numero}: {texto}",
        pistas_restantes=ajustes.max_pistas - numero,
    )


def no_entiendo(
    sesion: Session,
    estudiante: Estudiante,
    servido_id: uuid.UUID,
    adaptador: AdaptadorLLM | None = None,
) -> str:
    """Re-explicación: no descuenta (pedir aclaración no es pedir ayuda extra). Explica más
    simple la última pista vista (o la estrategia, si aún no pidió pistas), sin avanzar."""
    servido = _servido_en_curso(sesion, estudiante, servido_id)
    ejercicio = sesion.get(Ejercicio, servido.ejercicio_id)
    numero = max(servido.pistas_usadas, 1)
    texto = _pista_llm(sesion, estudiante, servido, ejercicio, adaptador, numero, True)
    if texto is None:
        texto = mensajes.reexplicacion_local(ejercicio.pistas, ejercicio.respuesta_final)
    sesion.commit()  # registros de llamada_llm y evento_filtro
    return mensajes.personalizar(texto, estudiante.alias)


# Resolvamos juntos (RF-P7) -----------------------------------------------------------------


def resolver_juntos(
    sesion: Session,
    estudiante: Estudiante,
    servido_id: uuid.UUID,
    adaptador: AdaptadorLLM | None = None,
) -> ExplicacionGuiada:
    """Tras N fallos: se narra la solución del ejercicio original (ahí sí puede verse su
    respuesta) y se sirve un análogo de la misma celda, que cuenta como intento normal. El
    original se cierra sin más penalización: los fallos ya movieron el índice."""
    ajustes = get_settings()
    servido = _servido_en_curso(sesion, estudiante, servido_id)
    if servido.fallos < ajustes.fallos_para_resolver_juntos:
        raise NoPermitido("Primero intenta resolverlo.")
    ejercicio = sesion.get(Ejercicio, servido.ejercicio_id)
    pasos = None
    if _habilitado(adaptador):
        # La narración puede mostrar la respuesta, pero no inventar ni cambiar números.
        permitido = " ".join([ejercicio.enunciado, *ejercicio.solucion_referencia])
        aceptable = _filtro(
            sesion,
            servido,
            "narrarExplicacionGuiada",
            lambda t: mensajes.numeros_nuevos(t, permitido),
        )
        ctx = ContextoEjercicio(**_contexto(sesion, estudiante, ejercicio))
        pasos = adaptador.explicacion_guiada(sesion, ctx, servido.sesion_id, aceptable)
    if pasos is None:
        pasos = list(ejercicio.solucion_referencia)
    pasos = [mensajes.personalizar(paso, estudiante.alias) for paso in pasos]
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
    return ExplicacionGuiada(pasos=pasos, analogo=para_estudiante)
