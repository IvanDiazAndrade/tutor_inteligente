"""Panel del apoderado (F4; CU-10; RF-DA1–DA7).

Agregación determinista sobre `intento` y `dominio_oa`, sin LLM (AD-6): los mismos datos dan
siempre el mismo panel. Solo métricas agregadas: ni respuestas ni mensajes del tutor (RF-DA7).
Los textos usan encuadre de avance y apoyo, nunca de alarma (RF-DA6).
"""

import math
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from tutor.config import get_settings
from tutor.esquemas import MedidorUnidad, PanelApoderado, ResumenSemana
from tutor.modelos import DominioOA, Ejercicio, EjercicioServido, Estudiante, Intento, Unidad
from tutor.progreso import EstadoDominio, banda, para_repasar, unidad_sugerida

# Ventana para detectar dificultad (RF-DA3): lo reciente, no todo el historial.
DIAS_DIFICULTAD = 28
MIN_RESPUESTAS_DIFICULTAD = 3  # con menos, una racha mala no es una tendencia
ERRORES_ALTOS = 0.5
PISTAS_ALTAS = 1.5  # pistas promedio por ejercicio
# El tiempo de un ejercicio se cuenta hasta su última respuesta, con tope: si el niño dejó la
# app abierta, no se infla el tiempo de práctica.
TOPE_SEGUNDOS_EJERCICIO = 10 * 60


@dataclass
class _Ejercicio:
    """Un ejercicio servido, visto desde sus respuestas."""

    unidad_id: str
    dia: date  # día local de la primera respuesta
    segundos: int = 0
    pistas: int = 0
    respuestas: list[tuple[date, bool]] = field(default_factory=list)


@dataclass
class _Dificultad:
    respuestas: int = 0
    errores: int = 0
    ejercicios: int = 0
    pistas: int = 0

    @property
    def tasa_error(self) -> float:
        return self.errores / self.respuestas if self.respuestas else 0.0

    @property
    def pistas_promedio(self) -> float:
        return self.pistas / self.ejercicios if self.ejercicios else 0.0

    @property
    def necesita_apoyo(self) -> bool:
        return self.respuestas >= MIN_RESPUESTAS_DIFICULTAD and (
            self.tasa_error >= ERRORES_ALTOS or self.pistas_promedio >= PISTAS_ALTAS
        )


def _minuscula(texto: str) -> str:
    return texto[:1].lower() + texto[1:]


def _ejercicios_recientes(
    sesion: Session, estudiante: Estudiante, desde: datetime
) -> dict[object, _Ejercicio]:
    zona = get_settings().zona_horaria
    filas = sesion.execute(
        select(
            Intento.ejercicio_servido_id,
            Ejercicio.unidad_id,
            func.timezone(zona, Intento.creado_en),
            Intento.es_correcta,
            Intento.tiempo_segundos,
            Intento.pistas_usadas,
        )
        .join(EjercicioServido, EjercicioServido.id == Intento.ejercicio_servido_id)
        .join(Ejercicio, Ejercicio.id == EjercicioServido.ejercicio_id)
        .where(Intento.estudiante_id == estudiante.id, Intento.creado_en >= desde)
        .order_by(Intento.creado_en)
    )
    ejercicios: dict[object, _Ejercicio] = {}
    for servido_id, unidad_id, local, correcta, segundos, pistas in filas:
        e = ejercicios.setdefault(servido_id, _Ejercicio(unidad_id, local.date()))
        e.respuestas.append((local.date(), correcta))
        # tiempo_segundos se mide desde que se mostró el ejercicio: vale el de la última.
        e.segundos = max(e.segundos, min(segundos, TOPE_SEGUNDOS_EJERCICIO))
        e.pistas = max(e.pistas, pistas)
    return ejercicios


def _resumen(ejercicios: list[_Ejercicio], lunes: date) -> ResumenSemana:
    domingo = lunes + timedelta(days=6)
    segundos = [0] * 7
    respuestas = correctas = trabajados = 0
    for e in ejercicios:
        if lunes <= e.dia <= domingo:
            trabajados += 1
            segundos[(e.dia - lunes).days] += e.segundos
        for dia, correcta in e.respuestas:
            if lunes <= dia <= domingo:
                respuestas += 1
                correctas += correcta
    return ResumenSemana(
        ejercicios=trabajados,
        respuestas=respuestas,
        correctas=correctas,
        # Hacia arriba: un día con práctica nunca aparece como 0 minutos.
        minutos_por_dia=[math.ceil(s / 60) for s in segundos],
    )


def _comentario(estado: EstadoDominio, dificultad: _Dificultad, ahora: datetime) -> str:
    """Una frase por unidad, por reglas (RF-DA5), en tono de avance (RF-DA6)."""
    b = banda(estado.indice)
    if b == "Dominado":
        return "Lo maneja muy bien, ya casi no necesita pistas."
    if dificultad.necesita_apoyo:
        if dificultad.pistas_promedio >= PISTAS_ALTAS:
            return "Le está costando un poco: usa hartas pistas aquí."
        return "Le está costando un poco: practicar con calma le ayudará."
    if para_repasar(estado, ahora):
        return "Hace más de 3 semanas que no practica este tema."
    if b == "Practicando":
        return "Va avanzando parejo, con práctica regular."
    return "Recién está partiendo con este tema, es normal ir lento."


def _sugerencia(unidad: Unidad, estado: EstadoDominio | None, ahora: datetime) -> str:
    tema = _minuscula(unidad.descripcion_ciudadana)
    if estado is None:
        return f"Esta semana pueden empezar con {tema}."
    if para_repasar(estado, ahora):
        return f"Esta semana conviene repasar {tema}."
    return f"Esta semana conviene practicar {tema}."


def panel(sesion: Session, estudiante: Estudiante, ahora: datetime | None = None) -> PanelApoderado:
    ahora = ahora or datetime.now(UTC)
    zona = get_settings().zona_horaria
    hoy = sesion.scalar(select(func.timezone(zona, ahora))).date()
    lunes = hoy - timedelta(days=hoy.weekday())

    recientes = _ejercicios_recientes(sesion, estudiante, ahora - timedelta(days=DIAS_DIFICULTAD))
    ejercicios = list(recientes.values())

    desde_dificultad = hoy - timedelta(days=DIAS_DIFICULTAD)
    dificultad: dict[str, _Dificultad] = defaultdict(_Dificultad)
    for e in ejercicios:
        d = dificultad[e.unidad_id]
        en_ventana = [c for dia, c in e.respuestas if dia >= desde_dificultad]
        if en_ventana:
            d.ejercicios += 1
            d.pistas += e.pistas
            d.respuestas += len(en_ventana)
            d.errores += sum(not c for c in en_ventana)

    unidades = sesion.scalars(
        select(Unidad)
        .where(Unidad.activa, Unidad.curso <= estudiante.curso)
        .order_by(Unidad.curso, Unidad.orden)
    ).all()
    dominios = {
        d.unidad_id: d
        for d in sesion.scalars(
            select(DominioOA).where(
                DominioOA.estudiante_id == estudiante.id, DominioOA.intentos_en_unidad > 0
            )
        )
    }
    estados = {u: EstadoDominio(d.indice, d.fecha_ultimo_intento) for u, d in dominios.items()}

    # Medidores: unidades iniciadas, primero las del curso actual (RF-DA2).
    iniciadas = sorted((u for u in unidades if u.id in estados), key=lambda u: (-u.curso, u.orden))
    medidores = [
        MedidorUnidad(
            unidad_id=u.id,
            descripcion=u.descripcion_ciudadana,
            indice=float(estados[u.id].indice),
            banda=banda(estados[u.id].indice),
            comentario=_comentario(estados[u.id], dificultad[u.id], ahora),
            necesita_apoyo=dificultad[u.id].necesita_apoyo,
        )
        for u in iniciadas
    ]

    sugerida = unidad_sugerida(unidades, estados, ahora, estudiante.curso)
    return PanelApoderado(
        alias=estudiante.alias,
        curso=estudiante.curso,
        esta_semana=_resumen(ejercicios, lunes),
        semana_pasada=_resumen(ejercicios, lunes - timedelta(days=7)),
        medidores=medidores,
        sugerencia=_sugerencia(sugerida, estados.get(sugerida.id), ahora) if sugerida else None,
    )
