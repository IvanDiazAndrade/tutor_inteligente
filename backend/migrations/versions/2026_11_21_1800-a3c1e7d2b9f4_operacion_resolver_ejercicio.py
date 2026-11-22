"""Operación resolverEjercicio en llamada_llm (doble pasada de fracciones, RF-D6).

Revision ID: a3c1e7d2b9f4
Revises: f95b07c98e4c
Create Date: 2026-11-21 18:00

El pipeline de ejercicios verbales resuelve de nuevo, en una llamada independiente, los
problemas de fracciones (modelo_dominio.md §8, capa 1). Esa llamada se registra con su costo
como cualquier otra, así que la restricción de operaciones admite el nombre nuevo.
"""

from collections.abc import Sequence

from alembic import op

revision: str = "a3c1e7d2b9f4"
down_revision: str | None = "f95b07c98e4c"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

ANTES = (
    "'generarEjercicio', 'triajeEjercicio', "
    "'generarRetroalimentacion', 'generarPista', 'narrarExplicacionGuiada'"
)
AHORA = ANTES + ", 'resolverEjercicio'"


def _restriccion(operaciones: str) -> None:
    op.execute("ALTER TABLE llamada_llm DROP CONSTRAINT llamada_llm_operacion_check")
    op.execute(
        "ALTER TABLE llamada_llm ADD CONSTRAINT llamada_llm_operacion_check "
        f"CHECK (operacion IN ({operaciones}))"
    )


def upgrade() -> None:
    _restriccion(AHORA)


def downgrade() -> None:
    op.execute("DELETE FROM llamada_llm WHERE operacion = 'resolverEjercicio'")
    _restriccion(ANTES)
