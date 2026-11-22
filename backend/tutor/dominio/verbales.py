"""Ejercicios verbales generados por el LLM: reposición del banco (F5; modelo_dominio.md §8).

Para cada celda unidad × nivel con pocos problemas verbales: el LLM genera uno (capa 0), se
verifica la aritmética (capa 1, con doble resolución independiente en fracciones, RF-D6) y la
forma (capa 2), y el LLM de triaje lo marca ok o dudoso (capa 3). Lo que pasa queda
`verificado`, esperando al revisor humano (capa 4, tutor/dominio/revision.py); lo que no, queda
`descartado` con su motivo, para auditar el pipeline. El LLM nunca aprueba ni pone nada en
rotación por sí solo.

Sin clave, con el circuito abierto o sin presupuesto, el lote se pospone: el banco sigue
sirviendo lo que ya tiene (estrategia_llm.md §3).
"""

import json
import random
from dataclasses import dataclass, field
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from tutor.dominio.verificacion import respuesta_canonica, valor, verificar
from tutor.llm.adaptador import AdaptadorLLM, EjercicioLLM
from tutor.modelos import Ejercicio, Unidad

# Unidades con problemas verbales y cuántos se buscan por celda (modelo_dominio.md §4-5): las
# solo LLM llegan a 5 por nivel; las mixtas suman uno por nivel a lo paramétrico.
SOLO_LLM = ("4B-OA7", "5B-OA6", "5B-OA13", "6B-OA2", "6B-OA8")
MIXTAS = ("4B-OA3", "4B-OA5", "4B-OA6", "4B-OA9", "5B-OA3", "5B-OA4", "5B-OA9", "5B-OA12", "6B-OA6")
OBJETIVO = {**{u: 5 for u in SOLO_LLM}, **{u: 1 for u in MIXTAS}}
# Formato de la respuesta: fracción en las unidades de fracciones; las de "fracciones o
# decimales" alternan.
FORMATOS = {
    "4B-OA9": ("fraccion",),
    "5B-OA9": ("fraccion",),
    "6B-OA6": ("fraccion",),
    "5B-OA13": ("fraccion", "numerico"),
    "6B-OA8": ("fraccion", "numerico"),
}
# OA de fracciones: el problema se resuelve dos veces, de forma independiente (RF-D6).
FRACCIONES = {"4B-OA9", "5B-OA9", "5B-OA13", "6B-OA6", "6B-OA8"}
NIVELES = (1, 2, 3)
INTENTOS_POR_EJERCICIO = 3  # tope de llamadas por celda: acota el gasto si el LLM falla mucho
SIN_EJEMPLO = "(Todavía no hay un ejemplo resuelto para este objetivo: sigue las reglas.)"


@dataclass
class Resultado:
    verificados: int = 0
    descartados: int = 0
    motivos: list[str] = field(default_factory=list)
    pospuesto: bool = False


def verbales_en_celda(sesion: Session, unidad_id: str, nivel: int) -> int:
    """Problemas verbales en rotación o esperando revisión (no se generan de más)."""
    return sesion.scalar(
        select(func.count()).where(
            Ejercicio.unidad_id == unidad_id,
            Ejercicio.nivel == nivel,
            Ejercicio.fuente == "llm",
            Ejercicio.estado.in_(("verificado", "activo")),
        )
    )


def _ejemplo_gold(sesion: Session, unidad_id: str) -> str:
    gold = sesion.scalar(
        select(Ejercicio).where(
            Ejercicio.unidad_id == unidad_id,
            Ejercicio.fuente == "gold",
            Ejercicio.uso_gold == "fewshot",
        )
    )
    if gold is None:
        return SIN_EJEMPLO
    return json.dumps(
        {
            "enunciado": gold.enunciado,
            "respuesta_final": gold.respuesta_final,
            "solucion_referencia": gold.solucion_referencia,
            "pistas": gold.pistas,
        },
        ensure_ascii=False,
    )


def _variables(sesion: Session, unidad: Unidad, nivel: int, formato: str) -> dict:
    return {
        "curso": unidad.curso,
        "oaTextoOficial": unidad.oa_texto_oficial,
        "nivel": nivel,
        "maxPalabras": 60 if unidad.curso == 4 else 80,
        "formatoRespuesta": formato,
        "rangoNumerico": (
            json.dumps(unidad.rango_numerico, ensure_ascii=False)
            if unidad.rango_numerico
            else "sin restricción adicional"
        ),
        "ejemploGold": _ejemplo_gold(sesion, unidad.id),
    }


def _fila(ej: EjercicioLLM, unidad: Unidad, nivel: int, lote: str, version: str) -> Ejercicio:
    return Ejercicio(
        unidad_id=unidad.id,
        nivel=nivel,
        fuente="llm",
        estado="borrador",
        enunciado=ej.enunciado.strip(),
        formato_respuesta=ej.formato_respuesta,
        respuesta_final=ej.respuesta_final,
        regla_validacion={"aceptaEquivalentes": True},
        solucion_referencia=list(ej.solucion_referencia),
        errores_comunes=[e.model_dump() for e in ej.errores_comunes],
        pistas=list(ej.pistas),
        lote_generacion=lote,
        version_prompt=version,
    )


def _repetido(sesion: Session, unidad_id: str, enunciado: str) -> bool:
    return (
        sesion.scalar(
            select(func.count()).where(
                Ejercicio.unidad_id == unidad_id,
                Ejercicio.enunciado == enunciado,
                Ejercicio.estado.in_(("verificado", "activo", "retirado")),
            )
        )
        > 0
    )


def generar_uno(
    sesion: Session,
    adaptador: AdaptadorLLM,
    unidad: Unidad,
    nivel: int,
    azar: random.Random,
    lote: str,
) -> Ejercicio | None:
    """Capas 0 a 3 para un problema. None si el LLM no respondió (el lote se pospone)."""
    formato = azar.choice(FORMATOS.get(unidad.id, ("numerico",)))
    variables = _variables(sesion, unidad, nivel, formato)
    ej = adaptador.generar_ejercicio(sesion, variables)
    if ej is None:
        return None
    version = adaptador.prompts.version("gen-ejercicio")
    fila = _fila(ej, unidad, nivel, lote, version)
    sesion.add(fila)

    motivo = verificar(ej, unidad.curso, unidad.rango_numerico or {})
    if motivo is None and _repetido(sesion, unidad.id, fila.enunciado):
        motivo = "repite un enunciado que ya está en el banco"
    if motivo is None and unidad.id in FRACCIONES:
        segunda = adaptador.resolver(sesion, unidad.curso, ej.enunciado, ej.formato_respuesta)
        if segunda is None:
            motivo = "no se pudo hacer la segunda resolución independiente"
        else:
            try:
                iguales = valor(segunda.respuesta_final) == valor(ej.respuesta_final)
            except ValueError:
                iguales = False
            if not iguales:
                motivo = (
                    f"la segunda resolución da {segunda.respuesta_final} y no {ej.respuesta_final}"
                )
    if motivo:
        fila.estado, fila.motivo_descarte = "descartado", motivo
        return fila

    fila.respuesta_final = respuesta_canonica(ej.respuesta_final, ej.formato_respuesta)
    triaje = adaptador.triaje(sesion, unidad.curso, ej.model_dump_json())
    fila.veredicto_triaje = triaje.veredicto if triaje else None  # sin triaje: revisión normal
    fila.estado = "verificado"
    return fila


def reponer_verbales(
    sesion: Session,
    adaptador: AdaptadorLLM,
    azar: random.Random | None = None,
    unidades: list[str] | None = None,
) -> Resultado:
    """Completa las celdas con pocos problemas verbales. Sin LLM disponible, no hace nada."""
    resultado = Resultado()
    if not adaptador.habilitado:
        resultado.pospuesto = True
        return resultado
    azar = azar or random.Random()
    lote = f"llm-{datetime.now(UTC):%Y%m%d-%H%M}"
    for unidad_id in unidades or list(OBJETIVO):
        unidad = sesion.get(Unidad, unidad_id)
        if unidad is None or not unidad.activa:
            continue
        for nivel in NIVELES:
            faltan = OBJETIVO.get(unidad_id, 1) - verbales_en_celda(sesion, unidad_id, nivel)
            for _ in range(max(faltan, 0) * INTENTOS_POR_EJERCICIO):
                if faltan <= 0:
                    break
                fila = generar_uno(sesion, adaptador, unidad, nivel, azar, lote)
                if fila is None:
                    resultado.pospuesto = True
                    sesion.commit()  # deja registradas las llamadas fallidas
                    return resultado
                if fila.estado == "verificado":
                    resultado.verificados += 1
                    faltan -= 1
                else:
                    resultado.descartados += 1
                    resultado.motivos.append(f"{unidad_id} N{nivel}: {fila.motivo_descarte}")
                sesion.commit()
    return resultado
