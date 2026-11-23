"""Gamificación (tarea 64; RF-G1–G4; CU-5, CU-6).

Puntos por ejercicio correcto ponderados por nivel y con descuento por pista; estrellas por
unidad según la banda del índice (no por cantidad de ejercicios: RF-G2); insignia al dominar una
unidad. Todo se compara solo con el propio estudiante (RF-G3, G4): no hay rankings, ni tablas,
ni temporizadores, y los mensajes hablan de esfuerzo y avance ("superaste tu marca").

Lo que se muestra se deriva por consulta (modelo_base_datos.md: estrellas, insignias y marcas
no se almacenan); solo el puntaje acumulado se guarda, en `estudiante.puntaje_total`.
"""

from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from tutor.config import get_settings
from tutor.esquemas import LogroUnidad, ProgresoEstudiante
from tutor.modelos import DominioOA, Estudiante, Intento, Unidad
from tutor.progreso import EstadoDominio, estrellas

PUNTOS_POR_NIVEL = 10
DESCUENTO_POR_PISTA = 0.15
PISO = 0.4


def puntos_por(nivel: int, pistas: int) -> int:
    """RF-G1: 10 por nivel de dificultad, con el mismo descuento por pista que el índice de
    dominio (−15 % por pista, piso 40 %): resolver con ayuda también suma (RF-P5).
    Nivel 1 sin pistas = 10; nivel 3 con 2 pistas = 21. Fórmula por ratificar con el equipo."""
    return round(PUNTOS_POR_NIVEL * nivel * max(PISO, 1 - DESCUENTO_POR_PISTA * pistas))


def mensaje(puntos_semana: int, mejor_semana_anterior: int, insignias: int) -> str:
    """Encuadre de esfuerzo y progreso personal (RF-G4): nunca contra otros."""
    if puntos_semana == 0:
        if mejor_semana_anterior:
            return "¡Una semana nueva! Cada ejercicio que resuelves suma puntos."
        return "Cada ejercicio que resuelves suma puntos. ¡Empieza cuando quieras!"
    if mejor_semana_anterior and puntos_semana > mejor_semana_anterior:
        return "¡Superaste tu marca! Es tu mejor semana hasta ahora."
    if mejor_semana_anterior:
        faltan = mejor_semana_anterior - puntos_semana + 1
        return f"Vas muy bien. Con {faltan} puntos más superas tu mejor semana."
    if insignias:
        return "¡Buen comienzo! Sigue practicando para ganar más estrellas."
    return "¡Buen comienzo! Sigue así para ganar tu primera insignia."


def progreso(
    sesion: Session, estudiante: Estudiante, ahora: datetime | None = None
) -> ProgresoEstudiante:
    """GET /estudiante/progreso (CU-6): puntos, marca semanal, estrellas e insignias."""
    ahora = ahora or datetime.now(UTC)
    zona = get_settings().zona_horaria
    # Semanas de lunes a domingo en hora de Chile, como el panel del apoderado.
    semana = func.date_trunc("week", func.timezone(zona, Intento.creado_en))
    por_semana = dict(
        sesion.execute(
            select(semana, func.sum(Intento.puntos))
            .where(Intento.estudiante_id == estudiante.id, Intento.es_correcta)
            .group_by(semana)
        ).all()
    )
    hoy = sesion.scalar(select(func.timezone(zona, ahora)))
    esta = hoy.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=hoy.weekday())
    puntos_semana = int(por_semana.pop(esta, 0) or 0)
    mejor_anterior = int(max((v for k, v in por_semana.items() if k < esta), default=0) or 0)
    resueltos = sesion.scalar(
        select(func.count())
        .select_from(Intento)
        .where(Intento.estudiante_id == estudiante.id, Intento.es_correcta)
    )

    filas = sesion.execute(
        select(Unidad, DominioOA)
        .join(DominioOA, DominioOA.unidad_id == Unidad.id)
        .where(
            DominioOA.estudiante_id == estudiante.id,
            DominioOA.intentos_en_unidad > 0,
            Unidad.activa,
        )
        .order_by(Unidad.curso.desc(), Unidad.orden)
    ).all()
    unidades = []
    for u, d in filas:
        n = estrellas(EstadoDominio(d.indice, d.fecha_ultimo_intento))
        unidades.append(
            LogroUnidad(
                id=u.id,
                curso=u.curso,
                descripcion=u.descripcion_ciudadana,
                estrellas=n,
                nivel=d.nivel_actual,
                insignia=n == 3,
            )
        )
    insignias = sum(u.insignia for u in unidades)
    return ProgresoEstudiante(
        alias=estudiante.alias,
        puntos_total=estudiante.puntaje_total,
        puntos_semana=puntos_semana,
        mejor_semana_anterior=mejor_anterior,
        ejercicios_resueltos=resueltos,
        insignias=insignias,
        mensaje=mensaje(puntos_semana, mejor_anterior, insignias),
        unidades=unidades,
    )
