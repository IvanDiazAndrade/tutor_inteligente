"""Punto de entrada de la API REST."""

from fastapi import FastAPI

from tutor import __version__

app = FastAPI(title="Tutor Inteligente", version=__version__)


@app.get("/salud")
def salud() -> dict[str, str]:
    """Confirma que la API está arriba. No consulta la base de datos ni el LLM."""
    return {"estado": "ok", "version": __version__}
