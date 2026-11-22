"""Reposición de problemas verbales y revisión humana (F5, CU-7, CU-14).

Todo con ProveedorSimulado: la CI nunca gasta tokens. Se prueba que nada generado por el LLM
entra en rotación sin pasar las capas 1-2 y la revisión humana, y que sin LLM no pasa nada.
"""

import argparse
import itertools
import random

import pytest

from tests.test_llm import _adaptador
from tutor.catalogo import RUTA_POR_DEFECTO, cargar_catalogo, leer_catalogo
from tutor.dominio import revision
from tutor.dominio.verbales import OBJETIVO, reponer_verbales
from tutor.llm.adaptador import (
    AdaptadorLLM,
    EjercicioLLM,
    ErrorComunLLM,
    SolucionLLM,
    VeredictoTriaje,
)
from tutor.llm.proveedores import ErrorPermanente, ProveedorSimulado
from tutor.modelos import Ejercicio, LlamadaLLM


@pytest.fixture
def catalogo(sesion):
    cargar_catalogo(sesion, leer_catalogo(RUTA_POR_DEFECTO))
    sesion.commit()


def _miles(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def problema_dinero(n: int, paso_mal: bool = False) -> EjercicioLLM:
    """Un problema distinto por cada n: el cuaderno cuesta $1.000 + 10n."""
    cuaderno, lapiz, billete = 1000 + 10 * n, 350, 2000
    gasto = cuaderno + lapiz
    escrito = gasto + (100 if paso_mal else 0)
    vuelto = billete - escrito
    return EjercicioLLM(
        enunciado=(
            f"Sofía compra un cuaderno de ${_miles(cuaderno)} y un lápiz de ${lapiz}. "
            f"Paga con ${_miles(billete)}. ¿Cuánto dinero recibe de vuelto?"
        ),
        formato_respuesta="numerico",
        respuesta_final=f"${vuelto}",
        solucion_referencia=[
            f"Se suma lo que gasta: {_miles(cuaderno)} + {lapiz} = {_miles(escrito)}.",
            f"Se resta del billete: {_miles(billete)} − {_miles(escrito)} = {vuelto}.",
            f"Recibe ${vuelto} de vuelto.",
        ],
        errores_comunes=[
            ErrorComunLLM(
                respuesta=_miles(gasto),
                causa="respondió lo que gastó",
                retroalimentacion="Eso es lo que gastó; la pregunta es el vuelto.",
            )
        ],
        pistas=[
            "Primero averigua cuánto gasta.",
            "Suma el cuaderno y el lápiz.",
            "Ahora resta el gasto del billete.",
        ],
    )


def problema_fracciones(n: int) -> EjercicioLLM:
    a = n % 3 + 1  # 1/8, 2/8 o 3/8 más 4/8
    return EjercicioLLM(
        enunciado=f"Ana comió {a}/8 de una torta y Luis 4/8 (vez {n}). ¿Cuánto comieron juntos?",
        formato_respuesta="fraccion",
        respuesta_final=f"{a + 4}/8",
        solucion_referencia=[f"{a}/8 + 4/8 = {a + 4}/8.", f"Comieron {a + 4}/8."],
        errores_comunes=[
            ErrorComunLLM(
                respuesta=f"{a + 4}/16",
                causa="sumó los denominadores",
                retroalimentacion="Con igual denominador se suman solo los numeradores.",
            )
        ],
        pistas=[
            "Fíjate en los denominadores.",
            "Son iguales: se mantienen.",
            "Ahora suma los numeradores.",
        ],
    )


def simulador(generar=problema_dinero, triaje="ok", segunda=None, fallar_desde=None):
    """Responde según lo que se pide: ejercicio, triaje o segunda resolución."""
    contador = itertools.count(1)

    def responder(solicitud):
        if solicitud.esquema is EjercicioLLM:
            n = next(contador)
            if fallar_desde and n >= fallar_desde:
                raise ErrorPermanente("la API rechazó la solicitud")
            return generar(n)
        if solicitud.esquema is VeredictoTriaje:
            if isinstance(triaje, Exception):
                raise triaje
            return VeredictoTriaje(veredicto=triaje, razones=[])
        assert solicitud.esquema is SolucionLLM
        respuesta = segunda or "5/8"
        return SolucionLLM(pasos=["..."], respuesta_final=respuesta)

    return ProveedorSimulado(funcion=responder)


def _llm(sesion, estado=None) -> list[Ejercicio]:
    sesion.expire_all()
    consulta = sesion.query(Ejercicio).filter(Ejercicio.fuente == "llm")
    if estado:
        consulta = consulta.filter(Ejercicio.estado == estado)
    return consulta.all()


# Reposición (capas 0-3) ---------------------------------------------------------------


def test_sin_clave_el_lote_se_pospone_y_no_se_genera_nada(sesion, catalogo):
    resultado = reponer_verbales(sesion, AdaptadorLLM(None))
    assert resultado.pospuesto and not _llm(sesion)


def test_genera_hasta_completar_cada_celda_y_queda_esperando_revision(sesion, catalogo):
    adaptador = _adaptador(simulador())
    resultado = reponer_verbales(sesion, adaptador, random.Random(1), ["4B-OA7"])
    assert resultado.verificados == 3 * OBJETIVO["4B-OA7"] and resultado.descartados == 0
    verificados = _llm(sesion, "verificado")
    assert len(verificados) == 15 and not _llm(sesion, "activo")  # nada en rotación sin revisor
    e = verificados[0]
    assert e.veredicto_triaje == "ok" and e.version_prompt == "gen-v1"
    assert "$" not in e.respuesta_final and "." not in e.respuesta_final  # forma canónica
    llamadas = {ll.operacion for ll in sesion.query(LlamadaLLM)}
    assert llamadas == {"generarEjercicio", "triajeEjercicio"}
    # La celda ya está completa: una segunda pasada no genera ni gasta.
    assert reponer_verbales(sesion, adaptador, unidades=["4B-OA7"]).verificados == 0


def test_un_paso_mal_calculado_se_descarta_con_su_motivo(sesion, catalogo):
    adaptador = _adaptador(simulador(lambda n: problema_dinero(n, paso_mal=(n == 1))))
    resultado = reponer_verbales(sesion, adaptador, random.Random(1), ["4B-OA7"])
    assert resultado.descartados == 1 and resultado.verificados == 15
    [descartado] = _llm(sesion, "descartado")
    assert "paso aritmético incorrecto" in descartado.motivo_descarte


def test_un_enunciado_repetido_se_descarta(sesion, catalogo):
    adaptador = _adaptador(simulador(lambda n: problema_dinero(1)))
    resultado = reponer_verbales(sesion, adaptador, random.Random(1), ["4B-OA3"])
    assert resultado.verificados == 1  # el primero; los demás repiten el enunciado
    assert all("repite" in m for m in resultado.motivos) and resultado.descartados >= 2


def test_fracciones_se_resuelven_dos_veces_y_se_descarta_si_no_coinciden(sesion, catalogo):
    adaptador = _adaptador(simulador(problema_fracciones, segunda="1/2"))
    resultado = reponer_verbales(sesion, adaptador, random.Random(1), ["4B-OA9"])
    assert resultado.verificados == 0 and resultado.descartados > 0
    assert all("segunda resolución" in m for m in resultado.motivos)
    operaciones = {ll.operacion for ll in sesion.query(LlamadaLLM)}
    assert "resolverEjercicio" in operaciones


def test_fracciones_que_coinciden_quedan_verificadas(sesion, catalogo):
    # problema_fracciones(n): a = n % 3 + 1. Con la segunda resolución calculada igual.
    def coincide(n):
        return problema_fracciones(n)

    proveedor = simulador(coincide)
    respuestas = iter(f"{n % 3 + 1 + 4}/8" for n in itertools.count(1))
    original = proveedor._funcion

    def con_segunda(solicitud):
        if solicitud.esquema is SolucionLLM:
            return SolucionLLM(pasos=["..."], respuesta_final=next(respuestas))
        return original(solicitud)

    proveedor._funcion = con_segunda
    resultado = reponer_verbales(sesion, _adaptador(proveedor), random.Random(1), ["4B-OA9"])
    assert resultado.verificados == 3 and resultado.descartados == 0


def test_sin_triaje_el_ejercicio_igual_queda_para_revision(sesion, catalogo):
    adaptador = _adaptador(simulador(triaje=ErrorPermanente("sin triaje")))
    reponer_verbales(sesion, adaptador, random.Random(1), ["4B-OA3"])
    assert {e.veredicto_triaje for e in _llm(sesion, "verificado")} == {None}


def test_si_el_llm_deja_de_responder_el_lote_se_pospone(sesion, catalogo):
    adaptador = _adaptador(simulador(fallar_desde=3))
    resultado = reponer_verbales(sesion, adaptador, random.Random(1), ["4B-OA7"])
    assert resultado.pospuesto and resultado.verificados == 2


# Revisión humana (capa 4) --------------------------------------------------------------


@pytest.fixture
def pendientes(sesion, catalogo):
    adaptador = _adaptador(simulador(triaje="ok"))
    reponer_verbales(sesion, adaptador, random.Random(1), ["4B-OA3"])
    adaptador = _adaptador(simulador(lambda n: problema_dinero(n + 50), triaje="dudoso"))
    reponer_verbales(sesion, adaptador, random.Random(1), ["4B-OA5"])
    return revision.pendientes(sesion)


def test_los_dudosos_se_revisan_primero(pendientes):
    assert [e.veredicto_triaje for e in pendientes] == ["dudoso"] * 3 + ["ok"] * 3


def test_aprobar_pone_en_rotacion_y_registra_al_revisor(sesion, pendientes):
    e = pendientes[0]
    revision.aprobar(sesion, revision.buscar(sesion, str(e.id)[:8]), "Benjamín")
    assert e.estado == "activo" and e.revisado_por == "Benjamín" and e.revisado_en
    with pytest.raises(ValueError):
        revision.aprobar(sesion, e, "Benjamín")  # ya no está verificado


def test_descartar_un_activo_lo_retira_sin_borrarlo(sesion, pendientes):
    e = pendientes[0]
    revision.aprobar(sesion, e, "Benjamín")
    revision.descartar(sesion, e, "Iván", "el contexto no se entiende")
    assert e.estado == "retirado" and e.motivo_descarte == "revisión: el contexto no se entiende"


def test_la_ficha_muestra_todo_lo_que_hay_que_revisar(pendientes):
    texto = revision.ficha(pendientes[0])
    for parte in ("ENUNCIADO", "RESPUESTA", "SOLUCIÓN", "PISTAS", "ERRORES COMUNES", "dudoso"):
        assert parte in texto


def test_la_linea_de_comandos_lista_los_pendientes(sesion, pendientes, capsys):
    revision._ejecutar(sesion, argparse.Namespace(orden="pendientes"))
    salida = capsys.readouterr().out
    assert "6 ejercicios esperan revisión." in salida and "4B-OA5" in salida


# Planificador (reposición automática) ---------------------------------------------------


def test_sin_minutos_configurados_no_se_programa_nada():
    from tutor import planificador

    assert planificador.iniciar() is None  # REPOSICION_MINUTOS = 0 por defecto


def test_si_otra_reposicion_tiene_el_candado_se_omite_la_pasada(motor):
    from sqlalchemy import text

    from tutor import planificador

    with motor.connect() as otra:
        otra.execute(text("SELECT pg_advisory_lock(:k)"), {"k": planificador.CANDADO})
        try:
            assert planificador.ciclo(AdaptadorLLM(None)) is False
        finally:
            otra.execute(text("SELECT pg_advisory_unlock(:k)"), {"k": planificador.CANDADO})
