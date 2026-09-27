from fastapi.testclient import TestClient

from tutor.main import app

cliente = TestClient(app)


def test_salud_responde_ok():
    respuesta = cliente.get("/salud")

    assert respuesta.status_code == 200
    assert respuesta.json()["estado"] == "ok"
    # La API responde aunque la base de datos no esté disponible (p. ej. en CI).
    assert respuesta.json()["base_datos"] in {"ok", "sin conexión"}
