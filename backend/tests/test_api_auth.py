"""Registro, ingreso y perfil del estudiante (CU-1, CU-9)."""

APODERADO = {"email": "apoderado@ejemplo.cl", "contrasena": "clave-segura-1"}


def _cabecera(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _apoderado_con_token(cliente) -> str:
    assert cliente.post("/auth/apoderado/registro", json=APODERADO).status_code == 201
    respuesta = cliente.post("/auth/apoderado/login", json=APODERADO)
    assert respuesta.status_code == 200
    return respuesta.json()["token"]


def _crear_estudiante(cliente, token: str, pin: str = "1234") -> str:
    respuesta = cliente.post(
        "/apoderado/estudiante",
        json={"alias": "Vale", "curso": 5, "pin": pin},
        headers=_cabecera(token),
    )
    assert respuesta.status_code == 201
    return respuesta.json()["id"]


def _login_estudiante(cliente, estudiante_id: str, pin: str):
    return cliente.post("/auth/estudiante/login", json={"estudianteId": estudiante_id, "pin": pin})


def test_registro_rechaza_correo_repetido_sin_importar_mayusculas(cliente):
    assert cliente.post("/auth/apoderado/registro", json=APODERADO).status_code == 201

    otra = {**APODERADO, "email": "APODERADO@ejemplo.cl"}
    assert cliente.post("/auth/apoderado/registro", json=otra).status_code == 409


def test_registro_valida_correo_y_largo_de_contrasena(cliente):
    corta = {"email": "a@ejemplo.cl", "contrasena": "1234567"}
    assert cliente.post("/auth/apoderado/registro", json=corta).status_code == 422
    sin_arroba = {"email": "no-es-correo", "contrasena": "clave-segura-1"}
    assert cliente.post("/auth/apoderado/registro", json=sin_arroba).status_code == 422


def test_login_apoderado_con_contrasena_incorrecta(cliente):
    _apoderado_con_token(cliente)
    malo = {**APODERADO, "contrasena": "otra-clave-99"}
    assert cliente.post("/auth/apoderado/login", json=malo).status_code == 401


def test_la_contrasena_no_se_guarda_en_claro(cliente, sesion):
    from sqlalchemy import select

    from tutor.modelos import Apoderado

    _apoderado_con_token(cliente)
    guardado = sesion.scalar(select(Apoderado)).password_hash
    assert APODERADO["contrasena"] not in guardado
    assert guardado.startswith("$2")  # formato bcrypt


def test_flujo_apoderado_crea_perfil_y_el_estudiante_entra_con_pin(cliente):
    token = _apoderado_con_token(cliente)
    estudiante_id = _crear_estudiante(cliente, token)

    perfil = cliente.get("/apoderado/estudiante", headers=_cabecera(token)).json()
    assert perfil == {"id": estudiante_id, "alias": "Vale", "curso": 5}

    respuesta = _login_estudiante(cliente, estudiante_id, "1234")
    assert respuesta.status_code == 200
    assert respuesta.json()["rol"] == "estudiante"


def test_un_apoderado_no_puede_crear_un_segundo_estudiante(cliente):
    token = _apoderado_con_token(cliente)
    _crear_estudiante(cliente, token)

    otro = {"alias": "Tomás", "curso": 4, "pin": "4321"}
    respuesta = cliente.post("/apoderado/estudiante", json=otro, headers=_cabecera(token))
    assert respuesta.status_code == 409


def test_pin_debe_tener_4_digitos(cliente):
    token = _apoderado_con_token(cliente)
    respuesta = cliente.post(
        "/apoderado/estudiante",
        json={"alias": "Vale", "curso": 5, "pin": "12a4"},
        headers=_cabecera(token),
    )
    assert respuesta.status_code == 422


def test_cinco_pin_incorrectos_bloquean_el_perfil(cliente):
    estudiante_id = _crear_estudiante(cliente, _apoderado_con_token(cliente))

    for _ in range(4):
        assert _login_estudiante(cliente, estudiante_id, "0000").status_code == 401
    assert _login_estudiante(cliente, estudiante_id, "0000").status_code == 423
    # Durante el bloqueo ni siquiera el PIN correcto entra.
    assert _login_estudiante(cliente, estudiante_id, "1234").status_code == 423


def test_el_apoderado_cambia_curso_y_pin(cliente):
    token = _apoderado_con_token(cliente)
    estudiante_id = _crear_estudiante(cliente, token)

    respuesta = cliente.patch(
        "/apoderado/estudiante", json={"curso": 6, "pin": "9876"}, headers=_cabecera(token)
    )
    assert respuesta.json()["curso"] == 6
    assert _login_estudiante(cliente, estudiante_id, "1234").status_code == 401
    assert _login_estudiante(cliente, estudiante_id, "9876").status_code == 200


def test_cada_rol_solo_entra_a_sus_rutas(cliente):
    token_apoderado = _apoderado_con_token(cliente)
    estudiante_id = _crear_estudiante(cliente, token_apoderado)
    token_estudiante = _login_estudiante(cliente, estudiante_id, "1234").json()["token"]

    assert cliente.get("/apoderado/estudiante").status_code == 401
    assert cliente.get("/apoderado/estudiante", headers=_cabecera("no-es-token")).status_code == 401
    ruta_apoderado = cliente.get("/apoderado/estudiante", headers=_cabecera(token_estudiante))
    assert ruta_apoderado.status_code == 403
    ruta_estudiante = cliente.get("/estudiante/unidades", headers=_cabecera(token_apoderado))
    assert ruta_estudiante.status_code == 403
