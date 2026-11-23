"""Varios estudiantes por cuenta (RF-A1, actualización 23-nov-2026).

Revision ID: 8d4f2a6c1e37
Revises: 3b7e1c9d2a54
Create Date: 2026-11-23 12:00

Un apoderado puede tener hasta 3 estudiantes (por ejemplo, hermanos). Se quita el UNIQUE de
estudiante.apoderado_id, que imponía uno solo; el máximo lo controla la API
(Settings.max_estudiantes). Queda un índice para buscar los estudiantes de una cuenta.
"""

from collections.abc import Sequence

from alembic import op

revision: str = "8d4f2a6c1e37"
down_revision: str | None = "3b7e1c9d2a54"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TABLE estudiante DROP CONSTRAINT estudiante_apoderado_id_key")
    op.execute("CREATE INDEX ix_estudiante_apoderado_id ON estudiante (apoderado_id)")


def downgrade() -> None:
    # Falla si alguna cuenta ya tiene más de un estudiante: hay que resolverlo a mano antes.
    op.execute("DROP INDEX ix_estudiante_apoderado_id")
    op.execute(
        "ALTER TABLE estudiante ADD CONSTRAINT estudiante_apoderado_id_key UNIQUE (apoderado_id)"
    )
