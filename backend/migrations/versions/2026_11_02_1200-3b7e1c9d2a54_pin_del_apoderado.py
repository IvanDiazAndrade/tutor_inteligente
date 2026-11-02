"""PIN del panel del apoderado (RF-A3, actualización 2-nov-2026).

Revision ID: 3b7e1c9d2a54
Revises: f95b07c98e4c
Create Date: 2026-11-02 12:00

El PIN deja de ser del estudiante y pasa al apoderado: en un dispositivo vinculado el niño entra
tocando su perfil, y el PIN protege el panel. Las cuentas existentes conservan su PIN: se copia
el del estudiante al apoderado. Las que no tienen estudiante quedan con pin_hash NULL hasta que
el apoderado lo fije.
"""

from collections.abc import Sequence

from alembic import op

revision: str = "3b7e1c9d2a54"
down_revision: str | None = "f95b07c98e4c"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE apoderado
            ADD COLUMN pin_hash         text,
            ADD COLUMN pin_fallos       smallint NOT NULL DEFAULT 0,
            ADD COLUMN bloqueado_hasta  timestamptz;

        UPDATE apoderado a SET pin_hash = e.pin_hash
        FROM estudiante e WHERE e.apoderado_id = a.id;

        ALTER TABLE estudiante
            DROP COLUMN pin_hash,
            DROP COLUMN pin_fallos,
            DROP COLUMN bloqueado_hasta;
        """
    )


def downgrade() -> None:
    # Un estudiante sin apoderado con PIN no puede quedar con pin_hash NULL: se usa un hash que
    # no corresponde a ningún PIN, y el apoderado tendrá que fijarlo de nuevo.
    op.execute(
        """
        ALTER TABLE estudiante
            ADD COLUMN pin_hash         text,
            ADD COLUMN pin_fallos       smallint NOT NULL DEFAULT 0,
            ADD COLUMN bloqueado_hasta  timestamptz;

        UPDATE estudiante e SET pin_hash = COALESCE(a.pin_hash, '!sin-pin')
        FROM apoderado a WHERE e.apoderado_id = a.id;

        ALTER TABLE estudiante ALTER COLUMN pin_hash SET NOT NULL;

        ALTER TABLE apoderado
            DROP COLUMN pin_hash,
            DROP COLUMN pin_fallos,
            DROP COLUMN bloqueado_hasta;
        """
    )
