"""Planificador de la reposición del banco (F5; CU-7; diagrama_despliegue.md §3).

APScheduler corre dentro del proceso de la API y, cada REPOSICION_MINUTOS, completa las celdas
con stock bajo: primero lo paramétrico (sin costo) y después los problemas verbales (con el
LLM, si está disponible). Un candado de PostgreSQL (pg_try_advisory_lock) asegura que un solo
proceso repone a la vez, aunque algún día haya más de una instancia.

Con REPOSICION_MINUTOS = 0 (por defecto) no se programa nada: en desarrollo y en las pruebas
la reposición se hace a mano (python -m tutor.dominio.banco reponer / revision generar).
"""

import logging

from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import text

from tutor.config import get_settings
from tutor.db import SessionLocal, engine
from tutor.dominio.banco import reponer_parametricos
from tutor.dominio.verbales import reponer_verbales
from tutor.llm.adaptador import AdaptadorLLM, get_adaptador

log = logging.getLogger("tutor.planificador")
CANDADO = 57_000_001  # identificador del advisory lock de la reposición


def ciclo(adaptador: AdaptadorLLM | None = None) -> bool:
    """Una pasada de reposición. False si otro proceso ya la está haciendo."""
    # El candado vive en una conexión propia durante toda la pasada: la sesión de trabajo hace
    # commit varias veces y devolvería su conexión al pool, soltando un candado de sesión.
    with engine.connect() as candado:
        if not candado.scalar(text("SELECT pg_try_advisory_lock(:k)"), {"k": CANDADO}):
            log.info("Otra reposición está en curso: se omite esta pasada.")
            return False
        try:
            with SessionLocal() as sesion:
                agregados = reponer_parametricos(sesion)
                verbales = reponer_verbales(sesion, adaptador or get_adaptador())
            log.info(
                "Reposición: %s paramétricos, %s verbales verificados, %s descartados%s.",
                sum(agregados.values()),
                verbales.verificados,
                verbales.descartados,
                " (lote verbal pospuesto)" if verbales.pospuesto else "",
            )
            return True
        finally:
            candado.execute(text("SELECT pg_advisory_unlock(:k)"), {"k": CANDADO})
            candado.commit()


def iniciar() -> BackgroundScheduler | None:
    minutos = get_settings().reposicion_minutos
    if minutos <= 0:
        return None
    planificador = BackgroundScheduler(timezone="UTC")
    # max_instances=1 y coalesce: si una pasada se atrasa, no se acumulan pasadas pendientes.
    planificador.add_job(ciclo, "interval", minutes=minutos, max_instances=1, coalesce=True)
    planificador.start()
    log.info("Reposición del banco programada cada %s minutos.", minutos)
    return planificador
