"""Registro, ingreso, dispositivo vinculado y perfiles de estudiante (CU-1, CU-9; RF-A1–A3)."""

import uuid

APODERADO = {"email": "apoderado@ejemplo.cl", "contrasena": "clave-segura-1", "pin": "1234"}
LOGIN = {"email": APODERADO["email"], "contrasena": APODERADO["contrasena"]}


def _cabecera(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _registrar_e_ingresar(cliente) -> dict:
    """Registra al apoderado e inicia sesión: devuelve el token del panel y el del dispositivo."""
    assert cliente.post("/auth/apoderado/registro", json=APODERADO).status_code == 201
    respuesta = cliente.post("/auth/apoderado/login", json=LOGIN)
    assert respuesta.status_code == 200
    return respuesta.json()


def _crear_estudiante(cliente, token: str, alias: str = "Vale", curso: int = 5) -> str:
    respuesta = cliente.post(
        "/apoderado/estudiantes", json={"alias": alias, "curso": curso}, headers=_cabecera(token)
    )
    assert respuesta.status_code == 201
    return respuesta.json()["id"]


def _entrar(cliente, token_dispositivo: str, estudiante_id: str):
    return cliente.post(
        "/auth/dispositivo/estudiante",
        json={"estudianteId": estudiante_id},
        headers=_cabecera(token_dispositivo),
    )


def _abrir_panel(cliente, token_dispositivo: str, pin: str):
    return cliente.post(
        "/auth/dispositivo/apoderado", json={"pin": pin}, headers=_cabecera(token_dispositivo)
    )


def test_registro_rechaza_correo_repetido_sin_importar_mayusculas(cliente):
    assert cliente.post("/auth/apoderado/registro", json=APODERADO).status_code == 201

    otra = {**APODERADO, "email": "APODERADO@ejemplo.cl"}
    assert cliente.post("/auth/apoderado/registro", json=otra).status_code == 409


def test_registro_valida_correo_contrasena_y_pin(cliente):
    corta = {**APODERADO, "email": "a@ejemplo.cl", "contrasena": "1234567"}
    assert cliente.post("/auth/apoderado/registro", json=corta).status_code == 422
    sin_arroba = {**APODERADO, "email": "no-es-correo"}
    assert cliente.post("/auth/apoderado/registro", json=sin_arroba).status_code == 422
    pin_malo = {**APODERADO, "email": "b@ejemplo.cl", "pin": "12a4"}
    assert cliente.post("/auth/apoderado/registro", json=pin_malo).status_code == 422
    sin_pin = {"email": "c@ejemplo.cl", "contrasena": "clave-segura-1"}
    assert cliente.post("/auth/apoderado/registro", json=sin_pin).status_code == 422


def test_login_apoderado_con_contrasena_incorrecta(cliente):
    _registrar_e_ingresar(cliente)
    malo = {**LOGIN, "contrasena": "otra-clave-99"}
    assert cliente.post("/auth/apoderado/login", json=malo).status_code == 401


def test_contrasena_y_pin_no_se_guardan_en_claro(cliente, sesion):
    from sqlalchemy import select

    from tutor.modelos import Apoderado

    _registrar_e_ingresar(cliente)
    apoderado = sesion.scalar(select(Apoderado))
    assert APODERADO["contrasena"] not in apoderado.password_hash
    assert apoderado.password_hash.startswith("$2")  # formato bcrypt
    assert apoderado.pin_hash.startswith("$2")


def test_el_estudiante_entra_sin_pin_desde_un_dispositivo_vinculado(cliente):
    tokens = _registrar_e_ingresar(cliente)
    estudiante_id = _crear_estudiante(cliente, tokens["token"])

    perfiles = cliente.get("/apoderado/estudiantes", headers=_cabecera(tokens["token"])).json()
    assert perfiles == [{"id": estudiante_id, "alias": "Vale", "curso": 5, "puntajeTotal": 0}]

    respuesta = _entrar(cliente, tokens["tokenDispositivo"], estudiante_id)
    assert respuesta.status_code == 200
    assert respuesta.json()["rol"] == "estudiante"
    token_estudiante = respuesta.json()["token"]
    assert (
        cliente.get("/estudiante/unidades", headers=_cabecera(token_estudiante)).status_code == 200
    )


def test_sin_perfil_creado_no_se_puede_entrar_como_estudiante(cliente):
    tokens = _registrar_e_ingresar(cliente)
    respuesta = _entrar(cliente, tokens["tokenDispositivo"], str(uuid.uuid4()))
    assert respuesta.status_code == 404


def test_hasta_tres_estudiantes_por_cuenta_y_cada_uno_entra_con_su_perfil(cliente):
    tokens = _registrar_e_ingresar(cliente)
    ids = [
        _crear_estudiante(cliente, tokens["token"], alias, curso)
        for alias, curso in [("Vale", 5), ("Tomás", 4), ("Sofi", 6)]
    ]

    cuarto = {"alias": "Mati", "curso": 4}
    respuesta = cliente.post(
        "/apoderado/estudiantes", json=cuarto, headers=_cabecera(tokens["token"])
    )
    assert respuesta.status_code == 409
    assert "3" in respuesta.json()["detail"]

    perfiles = cliente.get("/apoderado/estudiantes", headers=_cabecera(tokens["token"])).json()
    assert [p["alias"] for p in perfiles] == ["Vale", "Tomás", "Sofi"]  # en orden de creación
    for estudiante_id, curso in zip(ids, [5, 4, 6], strict=True):
        token = _entrar(cliente, tokens["tokenDispositivo"], estudiante_id).json()["token"]
        perfil = cliente.get("/estudiante/perfil", headers=_cabecera(token)).json()
        assert (perfil["id"], perfil["curso"]) == (estudiante_id, curso)


def test_el_telefono_solo_lista_los_perfiles_de_su_cuenta(cliente):
    ajena = _registrar_e_ingresar(cliente)
    _crear_estudiante(cliente, ajena["token"], "Sofi", 4)
    otra = {**APODERADO, "email": "otra@ejemplo.cl"}
    assert cliente.post("/auth/apoderado/registro", json=otra).status_code == 201
    propia = cliente.post(
        "/auth/apoderado/login", json={"email": otra["email"], "contrasena": otra["contrasena"]}
    ).json()
    _crear_estudiante(cliente, propia["token"], "Pedro", 5)

    perfiles = cliente.get(
        "/auth/dispositivo/estudiantes", headers=_cabecera(propia["tokenDispositivo"])
    ).json()
    assert [p["alias"] for p in perfiles] == ["Pedro"]
    # Solo con el token del dispositivo: el del panel o el del estudiante no sirven.
    panel = cliente.get("/auth/dispositivo/estudiantes", headers=_cabecera(propia["token"]))
    assert panel.status_code == 403


def test_un_telefono_no_entra_a_perfiles_de_otra_cuenta(cliente):
    ajena = _registrar_e_ingresar(cliente)
    estudiante_ajeno = _crear_estudiante(cliente, ajena["token"])
    otra = {**APODERADO, "email": "otra@ejemplo.cl"}
    assert cliente.post("/auth/apoderado/registro", json=otra).status_code == 201
    propia = cliente.post(
        "/auth/apoderado/login", json={"email": otra["email"], "contrasena": otra["contrasena"]}
    ).json()

    assert _entrar(cliente, propia["tokenDispositivo"], estudiante_ajeno).status_code == 404
    cambio = cliente.patch(
        f"/apoderado/estudiantes/{estudiante_ajeno}",
        json={"curso": 6},
        headers=_cabecera(propia["token"]),
    )
    assert cambio.status_code == 404


def test_el_panel_se_abre_con_el_pin_del_apoderado(cliente):
    tokens = _registrar_e_ingresar(cliente)
    _crear_estudiante(cliente, tokens["token"])

    assert _abrir_panel(cliente, tokens["tokenDispositivo"], "0000").status_code == 401
    respuesta = _abrir_panel(cliente, tokens["tokenDispositivo"], "1234")
    assert respuesta.status_code == 200
    assert respuesta.json()["rol"] == "apoderado"
    panel = _cabecera(respuesta.json()["token"])
    assert cliente.get("/apoderado/estudiantes", headers=panel).status_code == 200


def test_cinco_pin_incorrectos_bloquean_el_panel(cliente):
    dispositivo = _registrar_e_ingresar(cliente)["tokenDispositivo"]

    for _ in range(4):
        assert _abrir_panel(cliente, dispositivo, "0000").status_code == 401
    assert _abrir_panel(cliente, dispositivo, "0000").status_code == 423
    # Durante el bloqueo ni siquiera el PIN correcto entra.
    assert _abrir_panel(cliente, dispositivo, "1234").status_code == 423


def test_el_apoderado_cambia_el_pin_desde_el_panel(cliente):
    tokens = _registrar_e_ingresar(cliente)

    respuesta = cliente.put(
        "/apoderado/pin", json={"pin": "9876"}, headers=_cabecera(tokens["token"])
    )
    assert respuesta.status_code == 204
    assert _abrir_panel(cliente, tokens["tokenDispositivo"], "1234").status_code == 401
    assert _abrir_panel(cliente, tokens["tokenDispositivo"], "9876").status_code == 200


def test_cuenta_sin_pin_fijado_abre_el_panel_sin_pin(cliente, sesion):
    """Cuentas anteriores al cambio, sin estudiante (la migración las deja con pin_hash NULL)."""
    from tutor.modelos import Apoderado
    from tutor.seguridad import crear_token

    apoderado = Apoderado(email="antigua@ejemplo.cl", password_hash="x")
    sesion.add(apoderado)
    sesion.commit()
    dispositivo = crear_token(apoderado.id, "dispositivo")
    assert _abrir_panel(cliente, dispositivo, "0000").status_code == 200


def test_el_apoderado_cambia_el_curso(cliente):
    token = _registrar_e_ingresar(cliente)["token"]
    estudiante_id = _crear_estudiante(cliente, token)

    respuesta = cliente.patch(
        f"/apoderado/estudiantes/{estudiante_id}", json={"curso": 6}, headers=_cabecera(token)
    )
    assert respuesta.json()["curso"] == 6


def test_cada_token_solo_entra_a_sus_rutas(cliente):
    tokens = _registrar_e_ingresar(cliente)
    estudiante_id = _crear_estudiante(cliente, tokens["token"])
    panel, dispositivo = tokens["token"], tokens["tokenDispositivo"]
    estudiante = _entrar(cliente, dispositivo, estudiante_id).json()["token"]

    assert cliente.get("/apoderado/estudiantes").status_code == 401
    assert (
        cliente.get("/apoderado/estudiantes", headers=_cabecera("no-es-token")).status_code == 401
    )
    assert cliente.get("/apoderado/estudiantes", headers=_cabecera(estudiante)).status_code == 403
    assert cliente.get("/estudiante/unidades", headers=_cabecera(panel)).status_code == 403
    # El token del dispositivo no abre el panel ni las rutas del estudiante por sí solo.
    assert cliente.get("/apoderado/estudiantes", headers=_cabecera(dispositivo)).status_code == 403
    assert cliente.get("/estudiante/unidades", headers=_cabecera(dispositivo)).status_code == 403
    # Y los tokens del panel o del estudiante no sirven como token de dispositivo.
    assert _abrir_panel(cliente, panel, "1234").status_code == 403
    assert _abrir_panel(cliente, estudiante, "1234").status_code == 403


def test_la_migracion_traspasa_el_pin_del_estudiante_al_apoderado(motor):
    """Baja a la revisión inicial con una cuenta con PIN y vuelve a subir: el PIN se conserva."""
    from alembic import command
    from alembic.config import Config
    from sqlalchemy import text

    from tutor.seguridad import hashear, verificar

    config = Config("alembic.ini")
    command.downgrade(config, "f95b07c98e4c")
    try:
        with motor.begin() as c:
            apoderado_id = c.execute(
                text(
                    "INSERT INTO apoderado (email, password_hash)"
                    " VALUES ('m@ejemplo.cl', 'x') RETURNING id"
                )
            ).scalar()
            c.execute(
                text(
                    "INSERT INTO estudiante (apoderado_id, alias, curso, pin_hash)"
                    " VALUES (:a, 'Vale', 5, :p)"
                ),
                {"a": apoderado_id, "p": hashear("4321")},
            )
        command.upgrade(config, "head")
        with motor.begin() as c:
            guardado = c.execute(
                text("SELECT pin_hash FROM apoderado WHERE id = :a"), {"a": apoderado_id}
            ).scalar()
            assert verificar("4321", guardado)
            c.execute(text("DELETE FROM apoderado WHERE id = :a"), {"a": apoderado_id})
    finally:
        command.upgrade(config, "head")
