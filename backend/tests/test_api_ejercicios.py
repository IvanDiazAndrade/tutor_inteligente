"""Flujo del ejercicio de punta a punta: F1, F2, F3 y resolvamos juntos."""

import uuid
from decimal import Decimal

from tests.conftest import UNIDAD
from tutor.modelos import (
    Apoderado,
    DominioOA,
    Ejercicio,
    EjercicioServido,
    Estudiante,
    Intento,
)
from tutor.seguridad import crear_token


def _servir(cliente, cabecera, unidad=UNIDAD):
    respuesta = cliente.post(f"/estudiante/unidades/{unidad}/ejercicio", headers=cabecera)
    assert respuesta.status_code == 201, respuesta.text
    return respuesta.json()


def _ejercicio(sesion, servido_id: str) -> Ejercicio:
    servido = sesion.get(EjercicioServido, uuid.UUID(servido_id))
    return sesion.get(Ejercicio, servido.ejercicio_id)


def _responder(cliente, cabecera, servido_id, respuesta):
    return cliente.post(
        f"/estudiante/servidos/{servido_id}/respuestas",
        json={"respuesta": respuesta, "tiempoSegundos": 20},
        headers=cabecera,
    )


def _incorrecta(sesion, servido_id: str) -> str:
    return str(int(_ejercicio(sesion, servido_id).respuesta_final) + 500)


def test_servir_no_envia_la_respuesta_ni_la_solucion(cliente, cabecera):
    """RF-D3 / AD-1: la solución de referencia nunca llega al cliente."""
    ejercicio = _servir(cliente, cabecera)

    assert ejercicio["nivel"] == 2  # arranque en frío (modelo_estudiante.md §4)
    assert ejercicio["pistasRestantes"] == 3
    assert ejercicio["formatoRespuesta"] == "numerico"
    assert ejercicio["unidadDescripcion"] == "Dividir con resto"
    prohibidos = {"respuestaFinal", "solucionReferencia", "erroresComunes", "pistas"}
    assert prohibidos.isdisjoint(ejercicio)


def test_unidades_sin_ejercicios_o_de_un_curso_superior(cliente, cabecera):
    sin_banco = cliente.post("/estudiante/unidades/5B-OA7/ejercicio", headers=cabecera)
    assert sin_banco.status_code == 404
    superior = cliente.post("/estudiante/unidades/6B-OA2/ejercicio", headers=cabecera)
    assert superior.status_code == 404


def test_respuesta_correcta_da_puntos_y_sube_el_indice(cliente, cabecera, sesion, estudiante):
    servido = _servir(cliente, cabecera)
    correcta = _ejercicio(sesion, servido["servidoId"]).respuesta_final

    respuesta = _responder(cliente, cabecera, servido["servidoId"], correcta).json()

    assert respuesta["resultado"] == "correcta"
    assert respuesta["puntos"] == 20 and "Ganaste 20 puntos" in respuesta["mensaje"]
    sesion.expire_all()
    assert sesion.get(Estudiante, estudiante.id).puntaje_total == 20
    dominio = sesion.get(DominioOA, (estudiante.id, UNIDAD))
    assert dominio.indice == Decimal("0.750") and dominio.intentos_en_unidad == 1
    # Ya resuelto: no acepta otra respuesta.
    assert _responder(cliente, cabecera, servido["servidoId"], correcta).status_code == 409


def test_los_espacios_alrededor_de_la_respuesta_se_ignoran(cliente, cabecera, sesion):
    servido = _servir(cliente, cabecera)
    correcta = _ejercicio(sesion, servido["servidoId"]).respuesta_final
    respuesta = _responder(cliente, cabecera, servido["servidoId"], f" {correcta} ").json()
    assert respuesta["resultado"] == "correcta"


def test_error_comun_explica_la_causa_sin_revelar(cliente, cabecera, sesion):
    servido = _servir(cliente, cabecera)
    ejercicio = _ejercicio(sesion, servido["servidoId"])
    error = ejercicio.errores_comunes[0]

    respuesta = _responder(cliente, cabecera, servido["servidoId"], error["respuesta"]).json()

    assert respuesta["resultado"] == "incorrecta"
    assert error["retroalimentacion"] in respuesta["mensaje"]
    assert ejercicio.respuesta_final not in respuesta["mensaje"].split()
    intento = sesion.query(Intento).one()
    assert intento.patron_error == error["causa"] and not intento.es_correcta


def test_formato_invalido_no_cuenta_como_intento(cliente, cabecera, sesion):
    servido = _servir(cliente, cabecera)
    respuesta = _responder(cliente, cabecera, servido["servidoId"], "cuarenta").json()
    assert respuesta["resultado"] == "formato_invalido"
    assert sesion.query(Intento).count() == 0


def test_primer_fallo_en_frio_baja_de_nivel(cliente, cabecera, sesion, estudiante):
    servido = _servir(cliente, cabecera)
    incorrecta = _incorrecta(sesion, servido["servidoId"])
    respuesta = _responder(cliente, cabecera, servido["servidoId"], incorrecta).json()
    assert respuesta["cambioNivel"] == "baja"
    sesion.expire_all()
    assert sesion.get(DominioOA, (estudiante.id, UNIDAD)).nivel_actual == 1


def test_tres_pistas_y_luego_no_hay_mas_con_descuento_de_puntos(cliente, cabecera, sesion):
    servido = _servir(cliente, cabecera)
    ruta = f"/estudiante/servidos/{servido['servidoId']}/pistas"
    numeros = [cliente.post(ruta, headers=cabecera).json() for _ in range(2)]
    assert [p["numero"] for p in numeros] == [1, 2]
    assert numeros[1]["pistasRestantes"] == 1
    assert numeros[0]["mensaje"].startswith("Pista 1:")

    correcta = _ejercicio(sesion, servido["servidoId"]).respuesta_final
    respuesta = _responder(cliente, cabecera, servido["servidoId"], correcta).json()
    assert respuesta["puntos"] == 14  # 20 × 0,70 con dos pistas


def test_no_hay_cuarta_pista(cliente, cabecera):
    servido = _servir(cliente, cabecera)
    ruta = f"/estudiante/servidos/{servido['servidoId']}/pistas"
    for _ in range(3):
        assert cliente.post(ruta, headers=cabecera).status_code == 200
    assert cliente.post(ruta, headers=cabecera).status_code == 409


def test_resolver_juntos_tras_tres_fallos_entrega_pasos_y_un_analogo(cliente, cabecera, sesion):
    servido = _servir(cliente, cabecera)
    servido_id = servido["servidoId"]
    ruta = f"/estudiante/servidos/{servido_id}/resolver-juntos"
    assert cliente.post(ruta, headers=cabecera).status_code == 409  # aún no

    incorrecta = _incorrecta(sesion, servido_id)
    for intento in range(3):
        respuesta = _responder(cliente, cabecera, servido_id, incorrecta).json()
        assert respuesta["ofreceResolverJuntos"] == (intento == 2)

    guiada = cliente.post(ruta, headers=cabecera).json()
    original = _ejercicio(sesion, servido_id)
    assert guiada["pasos"] == original.solucion_referencia
    assert guiada["analogo"]["servidoId"] != servido_id
    assert _ejercicio(sesion, guiada["analogo"]["servidoId"]).id != original.id
    sesion.expire_all()
    assert sesion.get(EjercicioServido, uuid.UUID(servido_id)).estado == "explicado"


def test_otro_ejercicio_abandona_el_anterior_sin_penalizar(cliente, cabecera, sesion, estudiante):
    primero = _servir(cliente, cabecera)
    segundo = _servir(cliente, cabecera)

    assert primero["servidoId"] != segundo["servidoId"]
    sesion.expire_all()
    assert sesion.get(EjercicioServido, uuid.UUID(primero["servidoId"])).estado == "abandonado"
    assert sesion.get(DominioOA, (estudiante.id, UNIDAD)).intentos_en_unidad == 0


def test_no_entiendo_no_descuenta_pistas(cliente, cabecera):
    servido = _servir(cliente, cabecera)
    ruta = f"/estudiante/servidos/{servido['servidoId']}/no-entiendo"
    mensaje = cliente.post(ruta, headers=cabecera).json()["mensaje"]
    assert mensaje.startswith("Vamos más despacio.")
    pista = cliente.post(f"/estudiante/servidos/{servido['servidoId']}/pistas", headers=cabecera)
    assert pista.json()["numero"] == 1


def test_no_puede_responder_el_ejercicio_de_otro(cliente, cabecera, sesion):
    servido = _servir(cliente, cabecera)
    otro = Estudiante(
        apoderado=Apoderado(email="otro@ejemplo.cl", password_hash="x"),
        alias="Tomás",
        curso=5,
        pin_hash="x",
    )
    sesion.add(otro)
    sesion.commit()
    ajena = {"Authorization": f"Bearer {crear_token(otro.id, 'estudiante')}"}
    assert _responder(cliente, ajena, servido["servidoId"], "1").status_code == 404
