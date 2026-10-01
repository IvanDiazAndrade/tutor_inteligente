"""Panel del apoderado (F4; RF-DA1–DA7): agregación determinista sobre intentos y dominio."""

from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from tests.conftest import UNIDAD
from tests.test_api_ejercicios import _ejercicio, _incorrecta, _responder, _servir
from tutor.dashboard import panel
from tutor.modelos import (
    Apoderado,
    DominioOA,
    Ejercicio,
    EjercicioServido,
    Intento,
    Sesion,
)
from tutor.seguridad import crear_token

# Miércoles 30-sep-2026, 12:00 en Chile (UTC−3 en horario de verano).
AHORA = datetime(2026, 9, 30, 15, 0, tzinfo=UTC)


@pytest.fixture
def cabecera_apoderado(estudiante) -> dict[str, str]:
    return {"Authorization": f"Bearer {crear_token(estudiante.apoderado_id, 'apoderado')}"}


def _ejercicio_respondido(sesion, estudiante, respuestas, unidad=UNIDAD, pistas=0):
    """Un ejercicio servido con sus respuestas: [(creado_en, correcta, tiempo_segundos)]."""
    ejercicio = sesion.query(Ejercicio).filter_by(unidad_id=unidad).first()
    practica = Sesion(estudiante_id=estudiante.id)
    sesion.add(practica)
    sesion.flush()
    servido = EjercicioServido(
        sesion_id=practica.id, estudiante_id=estudiante.id, ejercicio_id=ejercicio.id, nivel=2
    )
    sesion.add(servido)
    sesion.flush()
    for creado_en, correcta, segundos in respuestas:
        sesion.add(
            Intento(
                ejercicio_servido_id=servido.id,
                estudiante_id=estudiante.id,
                respuesta="1",
                es_correcta=correcta,
                pistas_usadas=pistas,
                tiempo_segundos=segundos,
                creado_en=creado_en,
            )
        )
    sesion.flush()


def _dominio(sesion, estudiante, indice, fecha, unidad=UNIDAD):
    sesion.add(
        DominioOA(
            estudiante_id=estudiante.id,
            unidad_id=unidad,
            indice=Decimal(indice),
            nivel_actual=2,
            racha_correctas=0,
            intentos_en_unidad=5,
            fecha_ultimo_intento=fecha,
        )
    )
    sesion.flush()


def test_sin_perfil_de_estudiante_responde_404(cliente, sesion):
    apoderado = Apoderado(email="solo@ejemplo.cl", password_hash="x")
    sesion.add(apoderado)
    sesion.commit()
    cabecera = {"Authorization": f"Bearer {crear_token(apoderado.id, 'apoderado')}"}
    assert cliente.get("/apoderado/dashboard", headers=cabecera).status_code == 404


def test_el_estudiante_no_puede_ver_el_panel(cliente, cabecera):
    assert cliente.get("/apoderado/dashboard", headers=cabecera).status_code == 403


def test_sin_practica_el_panel_sugiere_empezar(cliente, cabecera_apoderado):
    datos = cliente.get("/apoderado/dashboard", headers=cabecera_apoderado).json()

    assert datos["alias"] == "Vale" and datos["curso"] == 5
    assert datos["estaSemana"] == {
        "ejercicios": 0,
        "respuestas": 0,
        "correctas": 0,
        "minutosPorDia": [0] * 7,
    }
    assert datos["medidores"] == []
    assert datos["sugerencia"].startswith("Esta semana pueden empezar con ")


def test_la_practica_real_aparece_en_el_panel(cliente, cabecera, cabecera_apoderado, sesion):
    primero = _servir(cliente, cabecera)
    correcta = _ejercicio(sesion, primero["servidoId"]).respuesta_final
    _responder(cliente, cabecera, primero["servidoId"], correcta)
    segundo = _servir(cliente, cabecera)
    _responder(cliente, cabecera, segundo["servidoId"], _incorrecta(sesion, segundo["servidoId"]))

    datos = cliente.get("/apoderado/dashboard", headers=cabecera_apoderado).json()

    semana = datos["estaSemana"]
    assert (semana["ejercicios"], semana["respuestas"], semana["correctas"]) == (2, 2, 1)
    assert sum(semana["minutosPorDia"]) == 1  # 2 × 20 s en el día, redondeado hacia arriba
    [medidor] = datos["medidores"]
    assert medidor["unidadId"] == UNIDAD
    assert medidor["descripcion"] == "Dividir con resto"
    assert medidor["banda"] in {"Empezando", "Practicando", "Dominado"}
    # Solo métricas agregadas: nada de respuestas ni mensajes del tutor (RF-DA7).
    assert "respuesta" not in str(datos).lower().replace("respuestas", "")


def test_semanas_de_lunes_a_domingo_en_hora_de_chile(sesion, estudiante):
    # 28-sep 02:00 UTC es domingo 27 a las 23:00 en Chile: cuenta para la semana pasada.
    _ejercicio_respondido(sesion, estudiante, [(datetime(2026, 9, 28, 2, tzinfo=UTC), True, 60)])
    _ejercicio_respondido(sesion, estudiante, [(datetime(2026, 9, 28, 12, tzinfo=UTC), True, 120)])

    datos = panel(sesion, estudiante, AHORA)

    assert datos.semana_pasada.minutos_por_dia == [0, 0, 0, 0, 0, 0, 1]
    assert datos.esta_semana.minutos_por_dia == [2, 0, 0, 0, 0, 0, 0]


def test_el_tiempo_de_un_ejercicio_es_el_de_su_ultima_respuesta_con_tope(sesion, estudiante):
    lunes = datetime(2026, 9, 28, 14, tzinfo=UTC)
    # El tiempo se mide desde que se mostró el ejercicio: 30 s y luego 90 s son 90 s, no 120.
    _ejercicio_respondido(
        sesion, estudiante, [(lunes, False, 30), (lunes + timedelta(seconds=60), True, 90)]
    )
    # Una app olvidada abierta no infla la práctica: tope de 10 minutos por ejercicio.
    _ejercicio_respondido(sesion, estudiante, [(lunes, True, 5000)])

    semana = panel(sesion, estudiante, AHORA).esta_semana

    assert semana.minutos_por_dia[0] == 2 + 10
    assert (semana.ejercicios, semana.respuestas, semana.correctas) == (2, 3, 2)


def test_unidad_con_muchas_pistas_necesita_apoyo(sesion, estudiante):
    _dominio(sesion, estudiante, "0.5", AHORA - timedelta(days=1))
    ayer = AHORA - timedelta(days=1)
    for _ in range(3):
        _ejercicio_respondido(sesion, estudiante, [(ayer, True, 60)], pistas=2)

    [medidor] = panel(sesion, estudiante, AHORA).medidores

    assert medidor.necesita_apoyo
    assert medidor.comentario == "Le está costando un poco: usa hartas pistas aquí."


def test_pocas_respuestas_no_bastan_para_marcar_dificultad(sesion, estudiante):
    _dominio(sesion, estudiante, "0.5", AHORA - timedelta(days=1))
    _ejercicio_respondido(sesion, estudiante, [(AHORA - timedelta(days=1), False, 60)])

    [medidor] = panel(sesion, estudiante, AHORA).medidores

    assert not medidor.necesita_apoyo
    assert medidor.comentario == "Va avanzando parejo, con práctica regular."


def test_unidad_sin_practica_reciente_se_sugiere_repasar(sesion, estudiante):
    _dominio(sesion, estudiante, "0.6", AHORA - timedelta(days=30))

    datos = panel(sesion, estudiante, AHORA)

    assert datos.medidores[0].comentario == "Hace más de 3 semanas que no practica este tema."
    assert datos.sugerencia == "Esta semana conviene repasar dividir con resto."


def test_unidad_dominada(sesion, estudiante):
    _dominio(sesion, estudiante, "0.9", AHORA - timedelta(days=2))

    [medidor] = panel(sesion, estudiante, AHORA).medidores

    assert medidor.banda == "Dominado" and medidor.indice == pytest.approx(0.9)
    assert medidor.comentario == "Lo maneja muy bien, ya casi no necesita pistas."
