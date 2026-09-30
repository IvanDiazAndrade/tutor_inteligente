"""Banco de ejercicios: plantillas paramétricas registradas, aprobadas y reposición de celdas.

Uso (herramienta de línea de comandos del revisor, casos_de_uso.md §4):
    python -m tutor.dominio.banco registrar
    python -m tutor.dominio.banco aprobar 5B-OA4-div-resto --revisor "Nombre"
    python -m tutor.dominio.banco reponer

Una plantilla se aprueba una sola vez (modelo_dominio.md §8): desde ahí todo lo que genera
entra al banco como `activo`, sin revisión por ejercicio, porque es correcto por construcción.
Los ejercicios verbales del LLM (F5) se agregan con su pipeline en una tarea posterior.
"""

import argparse
import random
import sys
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from tutor.db import SessionLocal
from tutor.dominio.plantillas import PLANTILLAS, EjercicioGenerado
from tutor.modelos import Ejercicio, Plantilla

STOCK_OBJETIVO = 5  # ejercicios activos por celda unidad × nivel (modelo_dominio.md §5)
NIVELES = (1, 2, 3)
INTENTOS_POR_EJERCICIO = 20  # para evitar enunciados repetidos dentro de una celda


def registrar_plantillas(sesion: Session) -> int:
    """Crea o actualiza las filas de `plantilla`. No toca la aprobación de las existentes,
    salvo que cambie la versión: una plantilla modificada debe aprobarse de nuevo."""
    for p in PLANTILLAS.values():
        sentencia = insert(Plantilla).values(id=p.id, unidad_id=p.unidad_id, version=p.version)
        sesion.execute(
            sentencia.on_conflict_do_update(
                index_elements=[Plantilla.id],
                set_={
                    "unidad_id": sentencia.excluded.unidad_id,
                    "version": sentencia.excluded.version,
                    "aprobada": Plantilla.aprobada
                    & (Plantilla.version == sentencia.excluded.version),
                },
            )
        )
    sesion.commit()
    return len(PLANTILLAS)


def aprobar_plantilla(sesion: Session, plantilla_id: str, revisor: str) -> None:
    plantilla = sesion.get(Plantilla, plantilla_id)
    if plantilla is None:
        raise ValueError(f"No existe la plantilla {plantilla_id}; ejecuta primero 'registrar'.")
    plantilla.aprobada = True
    plantilla.aprobada_por = revisor
    plantilla.aprobada_en = datetime.now(UTC)
    sesion.commit()


def _a_fila(e: EjercicioGenerado, lote: str) -> Ejercicio:
    return Ejercicio(
        unidad_id=e.unidad_id,
        nivel=e.nivel,
        fuente="parametrica",
        estado="activo",
        enunciado=e.enunciado,
        representacion=e.representacion,
        formato_respuesta=e.formato_respuesta,
        respuesta_final=e.respuesta_final,
        regla_validacion=e.regla_validacion,
        solucion_referencia=e.solucion_referencia,
        errores_comunes=e.errores_comunes,
        pistas=e.pistas,
        plantilla_id=e.plantilla_id,
        lote_generacion=lote,
    )


def reponer_parametricos(
    sesion: Session, azar: random.Random | None = None, objetivo: int = STOCK_OBJETIVO
) -> dict[tuple[str, int], int]:
    """Completa cada celda unidad × nivel de las plantillas aprobadas hasta `objetivo`
    ejercicios activos. Devuelve cuántos se agregaron por celda."""
    azar = azar or random.Random()
    lote = f"param-{datetime.now(UTC):%Y%m%d}"
    aprobadas = sesion.scalars(select(Plantilla).where(Plantilla.aprobada)).all()
    agregados: dict[tuple[str, int], int] = {}
    for fila in aprobadas:
        plantilla = PLANTILLAS.get(fila.id)
        if plantilla is None:
            continue  # registrada en la base pero ya no existe en el código
        for nivel in NIVELES:
            activos = sesion.scalars(
                select(Ejercicio.enunciado).where(
                    Ejercicio.unidad_id == fila.unidad_id,
                    Ejercicio.nivel == nivel,
                    Ejercicio.estado == "activo",
                    Ejercicio.fuente != "gold",
                )
            ).all()
            enunciados = set(activos)
            faltan = objetivo - len(activos)
            nuevos = 0
            for _ in range(max(faltan, 0) * INTENTOS_POR_EJERCICIO):
                if nuevos == faltan:
                    break
                e = plantilla.instanciar(nivel, azar)
                if e.enunciado in enunciados:
                    continue
                enunciados.add(e.enunciado)
                sesion.add(_a_fila(e, lote))
                nuevos += 1
            if nuevos:
                agregados[(fila.unidad_id, nivel)] = nuevos
    sesion.commit()
    return agregados


def stock_por_celda(sesion: Session) -> dict[tuple[str, int], int]:
    filas = sesion.execute(
        select(Ejercicio.unidad_id, Ejercicio.nivel, func.count())
        .where(Ejercicio.estado == "activo", Ejercicio.fuente != "gold")
        .group_by(Ejercicio.unidad_id, Ejercicio.nivel)
    ).all()
    return {(u, n): c for u, n, c in filas}


def main(argumentos: list[str] | None = None) -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    analizador = argparse.ArgumentParser(prog="python -m tutor.dominio.banco")
    ordenes = analizador.add_subparsers(dest="orden", required=True)
    ordenes.add_parser("registrar", help="registra las plantillas del código en la base")
    aprobar = ordenes.add_parser("aprobar", help="aprueba una plantilla (revisión única)")
    aprobar.add_argument("plantilla")
    aprobar.add_argument("--revisor", required=True)
    ordenes.add_parser("reponer", help="completa las celdas de las plantillas aprobadas")
    args = analizador.parse_args(argumentos)

    with SessionLocal() as sesion:
        if args.orden == "registrar":
            print(f"Plantillas registradas: {registrar_plantillas(sesion)}.")
        elif args.orden == "aprobar":
            aprobar_plantilla(sesion, args.plantilla, args.revisor)
            print(f"Plantilla {args.plantilla} aprobada por {args.revisor}.")
        else:
            agregados = reponer_parametricos(sesion)
            print(f"Ejercicios agregados: {sum(agregados.values())}.")
            for (unidad, nivel), cantidad in sorted(stock_por_celda(sesion).items()):
                print(f"  {unidad} nivel {nivel}: {cantidad} activos")


if __name__ == "__main__":
    main()
