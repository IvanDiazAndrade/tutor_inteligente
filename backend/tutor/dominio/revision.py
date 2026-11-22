"""Revisión humana de los problemas verbales: capa 4 del pipeline (CU-14; modelo_dominio.md §8).

Herramienta de línea de comandos del revisor (casos_de_uso.md §4: sin pantallas de
administración en la app). Nada generado por el LLM llega a los estudiantes sin pasar por aquí.

    python -m tutor.dominio.revision generar                 # repone las celdas (necesita la clave)
    python -m tutor.dominio.revision pendientes              # dudosos y sin triaje primero
    python -m tutor.dominio.revision mostrar <id>            # el ejercicio completo
    python -m tutor.dominio.revision aprobar <id> --revisor "Nombre"
    python -m tutor.dominio.revision descartar <id> --revisor "Nombre" --motivo "..."
    python -m tutor.dominio.revision descartados             # para auditar las capas 1 y 2

El <id> puede ser el UUID completo o sus primeros caracteres (los que muestra "pendientes").
"""

import argparse
import sys
from datetime import UTC, datetime

from sqlalchemy import String, case, cast, select
from sqlalchemy.orm import Session

from tutor.modelos import Ejercicio


class NoEncontrado(Exception):
    pass


def pendientes(sesion: Session) -> list[Ejercicio]:
    """Los verificados que esperan revisión: primero los dudosos y los que no tuvieron triaje."""
    return list(
        sesion.scalars(
            select(Ejercicio)
            .where(Ejercicio.estado == "verificado")
            .order_by(case((Ejercicio.veredicto_triaje == "ok", 1), else_=0), Ejercicio.creado_en)
        )
    )


def buscar(sesion: Session, prefijo: str) -> Ejercicio:
    encontrados = sesion.scalars(
        select(Ejercicio).where(cast(Ejercicio.id, String).startswith(prefijo.lower()))
    ).all()
    if len(encontrados) != 1:
        raise NoEncontrado(
            f"{'Ningún' if not encontrados else 'Más de un'} ejercicio empieza con «{prefijo}»."
        )
    return encontrados[0]


def aprobar(sesion: Session, ejercicio: Ejercicio, revisor: str) -> None:
    if ejercicio.estado != "verificado":
        raise ValueError(f"Solo se aprueban ejercicios verificados (este está {ejercicio.estado}).")
    ejercicio.estado = "activo"
    ejercicio.revisado_por, ejercicio.revisado_en = revisor, datetime.now(UTC)
    sesion.commit()


def descartar(sesion: Session, ejercicio: Ejercicio, revisor: str, motivo: str) -> None:
    if ejercicio.estado not in ("verificado", "activo"):
        raise ValueError(f"Este ejercicio ya está {ejercicio.estado}.")
    # Uno activo que ya se sirvió se retira (conserva el historial); uno verificado, se descarta.
    ejercicio.estado = "retirado" if ejercicio.estado == "activo" else "descartado"
    ejercicio.motivo_descarte = f"revisión: {motivo}"
    ejercicio.revisado_por, ejercicio.revisado_en = revisor, datetime.now(UTC)
    sesion.commit()


def ficha(e: Ejercicio) -> str:
    """El ejercicio completo, como lo revisa una persona."""
    lineas = [
        f"{e.id}  ·  {e.unidad_id} nivel {e.nivel}  ·  {e.estado}"
        + (f"  ·  triaje: {e.veredicto_triaje}" if e.veredicto_triaje else "  ·  sin triaje"),
        "",
        f"ENUNCIADO: {e.enunciado}",
        f"RESPUESTA: {e.respuesta_final}  ({e.formato_respuesta})",
        "SOLUCIÓN:",
        *[f"  {i}. {paso}" for i, paso in enumerate(e.solucion_referencia, 1)],
        "PISTAS:",
        *[f"  {i}. {pista}" for i, pista in enumerate(e.pistas, 1)],
        "ERRORES COMUNES:",
        *[
            f"  · {err['respuesta']}: {err['causa']} → {err['retroalimentacion']}"
            for err in e.errores_comunes
        ],
    ]
    if e.motivo_descarte:
        lineas.append(f"MOTIVO DEL DESCARTE: {e.motivo_descarte}")
    return "\n".join(lineas)


def _linea(e: Ejercicio) -> str:
    triaje = e.veredicto_triaje or "sin triaje"
    return f"{str(e.id)[:8]}  {e.unidad_id:<8} N{e.nivel}  {triaje:<10}  {e.enunciado[:70]}"


def main(argumentos: list[str] | None = None) -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    analizador = argparse.ArgumentParser(prog="python -m tutor.dominio.revision")
    ordenes = analizador.add_subparsers(dest="orden", required=True)
    ordenes.add_parser("generar", help="genera y verifica problemas verbales (necesita la clave)")
    ordenes.add_parser("pendientes", help="lista los verificados que esperan revisión")
    ordenes.add_parser("descartados", help="lista los descartados por el pipeline o el revisor")
    mostrar = ordenes.add_parser("mostrar", help="muestra un ejercicio completo")
    mostrar.add_argument("id")
    aprobar_ = ordenes.add_parser("aprobar", help="pasa un verificado a activo")
    aprobar_.add_argument("id")
    aprobar_.add_argument("--revisor", required=True)
    descartar_ = ordenes.add_parser("descartar", help="descarta un verificado o retira un activo")
    descartar_.add_argument("id")
    descartar_.add_argument("--revisor", required=True)
    descartar_.add_argument("--motivo", required=True)
    args = analizador.parse_args(argumentos)

    from tutor.db import SessionLocal  # aquí y no arriba: las pruebas usan su propia sesión

    with SessionLocal() as sesion:
        try:
            _ejecutar(sesion, args)
        except (NoEncontrado, ValueError) as error:
            print(error)
            sys.exit(1)


def _ejecutar(sesion: Session, args: argparse.Namespace) -> None:
    if args.orden == "generar":
        from tutor.dominio.verbales import reponer_verbales
        from tutor.llm.adaptador import get_adaptador

        resultado = reponer_verbales(sesion, get_adaptador())
        if resultado.pospuesto and not (resultado.verificados or resultado.descartados):
            print(
                "El LLM no está disponible (sin clave, sin presupuesto o con fallas): "
                "no se generó nada. El banco sigue sirviendo lo que tiene."
            )
            return
        print(f"Verificados (esperan revisión): {resultado.verificados}.")
        print(f"Descartados por el pipeline: {resultado.descartados}.")
        for motivo in resultado.motivos:
            print(f"  · {motivo}")
        if resultado.pospuesto:
            print("El LLM dejó de responder: el resto del lote queda para la próxima vez.")
    elif args.orden == "pendientes":
        lista = pendientes(sesion)
        print(f"{len(lista)} ejercicios esperan revisión.")
        for e in lista:
            print(_linea(e))
    elif args.orden == "descartados":
        for e in sesion.scalars(
            select(Ejercicio)
            .where(Ejercicio.fuente == "llm", Ejercicio.estado.in_(("descartado", "retirado")))
            .order_by(Ejercicio.creado_en.desc())
        ):
            print(f"{_linea(e)}\n      motivo: {e.motivo_descarte}")
    elif args.orden == "mostrar":
        print(ficha(buscar(sesion, args.id)))
    elif args.orden == "aprobar":
        ejercicio = buscar(sesion, args.id)
        aprobar(sesion, ejercicio, args.revisor)
        print(f"Aprobado: {str(ejercicio.id)[:8]} ya está en rotación.")
    else:
        ejercicio = buscar(sesion, args.id)
        descartar(sesion, ejercicio, args.revisor, args.motivo)
        print(
            f"{'Retirado' if ejercicio.estado == 'retirado' else 'Descartado'}: "
            f"{str(ejercicio.id)[:8]}."
        )


if __name__ == "__main__":
    main()
