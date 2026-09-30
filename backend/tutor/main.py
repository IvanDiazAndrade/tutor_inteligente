"""Punto de entrada de la API REST."""

from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from tutor import __version__
from tutor.db import engine
from tutor.rutas import apoderado, auth, ejercicios, estudiante

app = FastAPI(title="Tutor Inteligente", version=__version__)
app.include_router(auth.router)
app.include_router(apoderado.router)
app.include_router(estudiante.router)
app.include_router(ejercicios.router)


@app.get("/salud")
def salud() -> dict[str, str]:
    """Confirma que la API está arriba e informa si alcanza la base de datos. No usa el LLM."""
    try:
        with engine.connect() as conexion:
            conexion.execute(text("SELECT 1"))
        base_datos = "ok"
    except SQLAlchemyError:
        base_datos = "sin conexión"
    return {"estado": "ok", "version": __version__, "base_datos": base_datos}
