"""Base de datos de pruebas.

Las pruebas usan una base aparte (tutor_test) que se recrea en cada ejecución con la migración
inicial, así nunca tocan los datos de desarrollo. Si PostgreSQL no está disponible, las pruebas
que la necesitan se saltan (docker compose up -d para levantarlo).
"""

import os
from collections.abc import Iterator

import psycopg
import pytest
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

URL_PRUEBAS = os.environ.get(
    "TEST_DATABASE_URL", "postgresql+psycopg://tutor:tutor@127.0.0.1:5432/tutor_test"
)
# Debe fijarse antes de importar tutor.*: la configuración se lee una sola vez.
os.environ["DATABASE_URL"] = URL_PRUEBAS


def _recrear_base() -> None:
    url = make_url(URL_PRUEBAS)
    with psycopg.connect(
        host=url.host,
        port=url.port,
        user=url.username,
        password=url.password,
        dbname="postgres",
        connect_timeout=3,
        autocommit=True,
    ) as conexion:
        conexion.execute(f'DROP DATABASE IF EXISTS "{url.database}" WITH (FORCE)')
        conexion.execute(f'CREATE DATABASE "{url.database}"')


@pytest.fixture(scope="session")
def motor():
    try:
        _recrear_base()
    except psycopg.OperationalError:
        pytest.skip("PostgreSQL no está disponible (docker compose up -d)")

    from alembic import command
    from alembic.config import Config

    command.upgrade(Config("alembic.ini"), "head")
    motor = create_engine(URL_PRUEBAS)
    yield motor
    motor.dispose()


@pytest.fixture
def sesion(motor) -> Iterator[Session]:
    """Sesión dentro de una transacción que se deshace al final: cada prueba parte limpia."""
    with motor.connect() as conexion:
        transaccion = conexion.begin()
        with Session(bind=conexion, join_transaction_mode="create_savepoint") as s:
            yield s
        transaccion.rollback()


@pytest.fixture
def cliente(sesion):
    """Cliente HTTP de la API que usa la sesión de prueba (sus cambios se deshacen al final)."""
    from fastapi.testclient import TestClient

    from tutor.db import get_session
    from tutor.main import app

    app.dependency_overrides[get_session] = lambda: sesion
    yield TestClient(app)
    app.dependency_overrides.clear()
