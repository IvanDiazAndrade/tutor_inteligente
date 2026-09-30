"""Adaptador LLM y su integración con el flujo del ejercicio (tarea 55).

Todo con ProveedorSimulado: la CI nunca gasta tokens ni necesita clave. Se prueba lo que
estrategia_llm.md promete: alias fuera del prompt, filtros antes de mostrar, reintentos,
circuit breaker, tope mensual y degradación a mensajes locales.
"""

from decimal import Decimal

import pytest

from tests.test_api_ejercicios import _ejercicio, _incorrecta, _responder, _servir
from tutor.config import get_settings
from tutor.llm.adaptador import AdaptadorLLM, ContextoError, PasosNarrados, get_adaptador
from tutor.llm.proveedores import ErrorPermanente, ErrorTransitorio, ProveedorSimulado
from tutor.main import app
from tutor.modelos import EventoFiltro, LlamadaLLM


class Reloj:
    def __init__(self):
        self.ahora = 0.0

    def __call__(self) -> float:
        return self.ahora


def _adaptador(proveedor, reloj=None, esperas=None, **ajustes) -> AdaptadorLLM:
    return AdaptadorLLM(
        proveedor,
        get_settings().model_copy(update=ajustes),
        reloj=reloj or Reloj(),
        esperar=(esperas.append if esperas is not None else lambda _: None),
    )


@pytest.fixture
def con_llm(cliente):
    """Conecta un ProveedorSimulado a la API; devuelve una función que lo instala."""

    def instalar(*respuestas, funcion=None, **ajustes) -> ProveedorSimulado:
        proveedor = ProveedorSimulado(list(respuestas), funcion)
        adaptador = _adaptador(proveedor, **ajustes)
        app.dependency_overrides[get_adaptador] = lambda: adaptador
        return proveedor

    return instalar


def _llamadas(sesion) -> list[LlamadaLLM]:
    sesion.expire_all()
    return sesion.query(LlamadaLLM).order_by(LlamadaLLM.id).all()


CTX = ContextoError(
    curso=5,
    enunciado="Reparte 37 láminas en grupos de 6.",
    solucion=["37 : 6 = 6, resto 1"],
    banda="Practicando",
    respuesta_estudiante="7",
    fallos=1,
)


# Sin clave ----------------------------------------------------------------------------------


def test_sin_clave_el_tutor_responde_local_y_no_registra_llamadas(cliente, cabecera, sesion):
    servido = _servir(cliente, cabecera)
    incorrecta = _incorrecta(sesion, servido["servidoId"])
    respuesta = _responder(cliente, cabecera, servido["servidoId"], incorrecta).json()

    assert respuesta["degradado"] is True
    assert respuesta["mensaje"].startswith("Todavía no es.")
    assert _llamadas(sesion) == []


# Integración con el flujo ---------------------------------------------------------------


def test_retroalimentacion_del_llm_personalizada_sin_enviar_el_alias(
    cliente, cabecera, sesion, con_llm
):
    proveedor = con_llm("¡Casi, {nombre}! Revisa cuántas veces cabe el divisor.")
    servido = _servir(cliente, cabecera)
    incorrecta = _incorrecta(sesion, servido["servidoId"])

    respuesta = _responder(cliente, cabecera, servido["servidoId"], incorrecta).json()

    assert respuesta["mensaje"] == "¡Casi, Vale! Revisa cuántas veces cabe el divisor."
    assert respuesta["degradado"] is False
    enviado = proveedor.solicitudes[0]
    assert "Vale" not in enviado.instrucciones + enviado.entrada  # RNF-S3
    assert incorrecta in enviado.entrada
    [llamada] = _llamadas(sesion)
    assert llamada.operacion == "generarRetroalimentacion" and llamada.resultado == "ok"
    assert llamada.version_prompt == "retro-v1" and llamada.costo_usd > 0
    assert llamada.sesion_id is not None


def test_la_respuesta_correcta_no_llama_al_llm(cliente, cabecera, sesion, con_llm):
    proveedor = con_llm()
    servido = _servir(cliente, cabecera)
    correcta = _ejercicio(sesion, servido["servidoId"]).respuesta_final

    respuesta = _responder(cliente, cabecera, servido["servidoId"], correcta).json()

    assert respuesta["resultado"] == "correcta" and respuesta["degradado"] is False
    assert proveedor.solicitudes == []


def test_si_el_llm_revela_la_respuesta_se_filtra_y_se_usa_el_mensaje_local(
    cliente, cabecera, sesion, con_llm
):
    servido = _servir(cliente, cabecera)
    ejercicio = _ejercicio(sesion, servido["servidoId"])
    con_llm(f"Te faltó poco: el resultado es {ejercicio.respuesta_final}.")

    incorrecta = _incorrecta(sesion, servido["servidoId"])
    respuesta = _responder(cliente, cabecera, servido["servidoId"], incorrecta).json()

    assert respuesta["mensaje"].startswith("Todavía no es.")
    assert respuesta["degradado"] is True
    [llamada] = _llamadas(sesion)
    assert llamada.resultado == "filtrado"
    evento = sesion.query(EventoFiltro).one()
    assert evento.operacion == "generarRetroalimentacion"
    assert ejercicio.respuesta_final in evento.texto_bloqueado


def test_pista_reformulada_y_pista_con_numeros_nuevos(cliente, cabecera, sesion, con_llm):
    con_llm("{nombre}, piensa en armar grupos iguales.", "Prueba con 98765 grupos.")
    servido = _servir(cliente, cabecera)
    ruta = f"/estudiante/servidos/{servido['servidoId']}/pistas"
    ejercicio = _ejercicio(sesion, servido["servidoId"])

    primera = cliente.post(ruta, headers=cabecera).json()
    segunda = cliente.post(ruta, headers=cabecera).json()

    assert primera["mensaje"] == "Pista 1: Vale, piensa en armar grupos iguales."
    # La segunda inventó un número: se entrega la pista verificada del banco.
    assert segunda["mensaje"] == f"Pista 2: {ejercicio.pistas[1]}"
    assert [ll.resultado for ll in _llamadas(sesion)] == ["ok", "filtrado"]
    assert sesion.query(EventoFiltro).one().operacion == "generarPista"


def test_no_entiendo_pide_una_explicacion_mas_simple(cliente, cabecera, con_llm):
    proveedor = con_llm("Imagina que repartes dulces entre amigos, {nombre}.")
    servido = _servir(cliente, cabecera)

    ruta = f"/estudiante/servidos/{servido['servidoId']}/no-entiendo"
    mensaje = cliente.post(ruta, headers=cabecera).json()["mensaje"]

    assert mensaje == "Imagina que repartes dulces entre amigos, Vale."
    assert "palabras más simples" in proveedor.solicitudes[0].entrada


def test_resolver_juntos_con_pasos_narrados(cliente, cabecera, sesion, con_llm):
    servido = _servir(cliente, cabecera)
    servido_id = servido["servidoId"]
    original = _ejercicio(sesion, servido_id)
    incorrecta = _incorrecta(sesion, servido_id)
    for _ in range(3):
        _responder(cliente, cabecera, servido_id, incorrecta)
    narrados = [f"Miremos este paso juntos, {{nombre}}. {p}" for p in original.solucion_referencia]
    con_llm(PasosNarrados(pasos=narrados))

    guiada = cliente.post(f"/estudiante/servidos/{servido_id}/resolver-juntos", headers=cabecera)

    assert guiada.json()["pasos"] == [p.replace("{nombre}", "Vale") for p in narrados]


def test_resolver_juntos_descarta_una_narracion_con_otra_cantidad_de_pasos(
    cliente, cabecera, sesion, con_llm
):
    servido = _servir(cliente, cabecera)
    servido_id = servido["servidoId"]
    original = _ejercicio(sesion, servido_id)
    incorrecta = _incorrecta(sesion, servido_id)
    for _ in range(3):
        _responder(cliente, cabecera, servido_id, incorrecta)
    con_llm(PasosNarrados(pasos=["Un solo paso."]))

    guiada = cliente.post(f"/estudiante/servidos/{servido_id}/resolver-juntos", headers=cabecera)

    assert guiada.json()["pasos"] == original.solucion_referencia
    assert _llamadas(sesion)[-1].resultado == "filtrado"


# Resiliencia y costo (estrategia_llm.md §5) ---------------------------------------------


def test_reintenta_los_errores_transitorios_con_espera(sesion):
    esperas = []
    proveedor = ProveedorSimulado([ErrorTransitorio("timeout"), ErrorTransitorio("503"), "Bien."])
    adaptador = _adaptador(proveedor, esperas=esperas, llm_reintentos=2)

    assert adaptador.retroalimentacion(sesion, CTX) == "Bien."
    assert esperas == [0.5, 2.0]
    assert [ll.resultado for ll in _llamadas(sesion)] == ["ok"]


def test_agotados_los_reintentos_devuelve_none_y_registra_el_timeout(sesion):
    proveedor = ProveedorSimulado([ErrorTransitorio("Request timeout")] * 3)
    adaptador = _adaptador(proveedor, llm_reintentos=2)

    assert adaptador.retroalimentacion(sesion, CTX) is None
    assert len(proveedor.solicitudes) == 3
    assert [ll.resultado for ll in _llamadas(sesion)] == ["timeout"]


def test_un_error_permanente_no_se_reintenta(sesion):
    proveedor = ProveedorSimulado([ErrorPermanente("clave inválida"), "no se usa"])
    adaptador = _adaptador(proveedor)

    assert adaptador.retroalimentacion(sesion, CTX) is None
    assert len(proveedor.solicitudes) == 1


def test_circuit_breaker_corta_y_luego_reintenta(sesion):
    reloj = Reloj()
    proveedor = ProveedorSimulado([ErrorPermanente("x"), ErrorPermanente("x"), "Volví."])
    adaptador = _adaptador(proveedor, reloj, llm_fallos_para_corte=2, llm_segundos_de_corte=60)

    adaptador.retroalimentacion(sesion, CTX)
    adaptador.retroalimentacion(sesion, CTX)
    assert adaptador.retroalimentacion(sesion, CTX) is None  # abierto: ni siquiera llama
    assert len(proveedor.solicitudes) == 2

    reloj.ahora = 61
    assert adaptador.retroalimentacion(sesion, CTX) == "Volví."
    assert [ll.resultado for ll in _llamadas(sesion)] == ["error", "error", "degradado", "ok"]


def test_al_llegar_al_tope_mensual_no_llama(sesion):
    sesion.add(
        LlamadaLLM(
            operacion="generarPista",
            modelo="m",
            version_prompt="v",
            resultado="ok",
            costo_usd=Decimal("5"),
        )
    )
    sesion.flush()
    proveedor = ProveedorSimulado(["no se usa"])
    adaptador = _adaptador(proveedor, llm_tope_usd=Decimal("5"))

    assert adaptador.retroalimentacion(sesion, CTX) is None
    assert proveedor.solicitudes == []
    assert _llamadas(sesion)[-1].resultado == "tope"


def test_costo_segun_precios_configurados(sesion):
    adaptador = _adaptador(
        ProveedorSimulado(),
        llm_precio_entrada_usd_mtok=Decimal("0.20"),
        llm_precio_salida_usd_mtok=Decimal("1.25"),
    )
    assert adaptador._costo(1_000_000, 1_000_000) == Decimal("1.45")


def test_sin_temperatura_si_el_modelo_no_la_acepta(sesion):
    proveedor = ProveedorSimulado(["Bien."])
    _adaptador(proveedor, llm_usar_temperatura=False).retroalimentacion(sesion, CTX)
    assert proveedor.solicitudes[0].temperatura is None


def test_todas_las_plantillas_se_renderizan():
    """StrictUndefined: si una plantilla pide una variable que el código no entrega, falla aquí
    y no en producción."""
    from dataclasses import asdict

    from tutor.llm.adaptador import ContextoEjercicio, ContextoPista

    prompts = _adaptador(None).prompts
    base = asdict(ContextoEjercicio(5, "E", ["a", "b"], "Empezando"))
    prompts.render("retroalimentacion", **asdict(CTX))
    for simplificar in (False, True):
        prompts.render("pista", **asdict(ContextoPista(**base, pista="p", simplificar=simplificar)))
    prompts.render("explicacion-guiada", **base)
    prompts.render("tutor-sistema")
