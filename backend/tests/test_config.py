"""Configuración para Render (tarea de despliegue): la URL de la base se adapta al driver."""

import pytest

from tutor.config import Settings


@pytest.mark.parametrize(
    "url",
    [
        "postgres://u:c@host:5432/tutor",
        "postgresql://u:c@host:5432/tutor",
        "postgresql+psycopg://u:c@host:5432/tutor",
    ],
)
def test_la_url_de_render_usa_psycopg(url):
    assert Settings(database_url=url).database_url == "postgresql+psycopg://u:c@host:5432/tutor"
