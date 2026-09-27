"""Esquema inicial: tablas de docs/modelo_base_datos.md (tarea 41).

Revision ID: f95b07c98e4c
Revises:
Create Date: 2026-09-26 16:59

El SQL es copia literal del DDL de docs/modelo_base_datos.md §3. Si el modelo cambia,
se agrega una migración nueva; esta no se edita.
"""

from collections.abc import Sequence

from alembic import op

revision: str = "f95b07c98e4c"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

DDL = """
CREATE EXTENSION IF NOT EXISTS citext;

-- Cuentas ------------------------------------------------------------------

CREATE TABLE apoderado (
    id             uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    email          citext NOT NULL UNIQUE,
    password_hash  text   NOT NULL,                -- bcrypt (RNF-S1)
    creado_en      timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE estudiante (
    id               uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    apoderado_id     uuid NOT NULL UNIQUE           -- UNIQUE = 1 apoderado ↔ 1 estudiante (RF-A1, por ratificar)
                     REFERENCES apoderado(id) ON DELETE CASCADE,
    alias            varchar(30) NOT NULL,          -- sin datos identificatorios (RF-A5, RNF-S2)
    curso            smallint NOT NULL CHECK (curso BETWEEN 4 AND 6),
    pin_hash         text NOT NULL,
    pin_fallos       smallint NOT NULL DEFAULT 0,
    bloqueado_hasta  timestamptz,
    puntaje_total    integer NOT NULL DEFAULT 0 CHECK (puntaje_total >= 0),
    creado_en        timestamptz NOT NULL DEFAULT now()
);

-- Catálogo curricular (datos, sin lógica: RNF-M2) ----------------------------

CREATE TABLE unidad (
    id                     text PRIMARY KEY,        -- oaCodigo, ej. '4B-OA9'
    oa_texto_oficial       text NOT NULL,
    descripcion_ciudadana  text NOT NULL,
    curso                  smallint NOT NULL CHECK (curso BETWEEN 4 AND 6),
    basal                  boolean NOT NULL,
    anillo                 smallint NOT NULL CHECK (anillo IN (1, 2)),
    orden                  smallint NOT NULL,
    rango_numerico         jsonb NOT NULL,
    activa                 boolean NOT NULL DEFAULT true,
    UNIQUE (curso, orden)
);

CREATE TABLE plantilla (
    id            text PRIMARY KEY,                 -- ej. '5B-OA4-div-resto'
    unidad_id     text NOT NULL REFERENCES unidad(id),
    version       integer NOT NULL DEFAULT 1,
    aprobada      boolean NOT NULL DEFAULT false,
    aprobada_por  text,
    aprobada_en   timestamptz
);

-- Banco de ejercicios ------------------------------------------------------------

CREATE TABLE ejercicio (
    id                   uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    unidad_id            text NOT NULL REFERENCES unidad(id),
    nivel                smallint NOT NULL CHECK (nivel BETWEEN 1 AND 3),
    fuente               text NOT NULL CHECK (fuente IN ('parametrica', 'llm', 'gold')),
    uso_gold             text CHECK (uso_gold IN ('fewshot', 'validacion')),
    estado               text NOT NULL DEFAULT 'borrador'
                         CHECK (estado IN ('borrador', 'verificado', 'activo', 'descartado', 'retirado')),
    enunciado            text NOT NULL,
    representacion       jsonb,                     -- {tipo, parametros}; el cliente dibuja el SVG
    formato_respuesta    text NOT NULL CHECK (formato_respuesta IN ('numerico', 'fraccion', 'ordenar', 'comparar')),
    respuesta_final      text NOT NULL,             -- nunca viaja al cliente (RF-D3, AD-1)
    regla_validacion     jsonb NOT NULL DEFAULT '{}',
    solucion_referencia  jsonb NOT NULL,            -- arreglo de pasos; nunca viaja al cliente
    errores_comunes      jsonb NOT NULL DEFAULT '[]',
    pistas               jsonb NOT NULL DEFAULT '[]',
                                                    -- 3 pistas en todo ejercicio servible; los gold no las necesitan
    plantilla_id         text REFERENCES plantilla(id),
    lote_generacion      text,
    version_prompt       text,
    veredicto_triaje     text CHECK (veredicto_triaje IN ('ok', 'dudoso')),
    motivo_descarte      text,
    revisado_por         text,
    revisado_en          timestamptz,
    creado_en            timestamptz NOT NULL DEFAULT now(),
    CHECK ((fuente = 'gold') = (uso_gold IS NOT NULL)),
    CHECK (fuente = 'gold' OR jsonb_array_length(pistas) = 3),
    CHECK (fuente <> 'parametrica' OR plantilla_id IS NOT NULL)
);

-- F1: ejercicios servibles de una celda unidad×nivel (los gold nunca rotan)
CREATE INDEX ix_ejercicio_celda_activa ON ejercicio (unidad_id, nivel)
    WHERE estado = 'activo' AND fuente <> 'gold';
-- Cola de la revisión humana: dudosos y sin triaje primero (false < true)
CREATE INDEX ix_ejercicio_revision ON ejercicio ((veredicto_triaje IS NOT DISTINCT FROM 'ok'), creado_en)
    WHERE estado = 'verificado';

-- Uso y desempeño ----------------------------------------------------------------

CREATE TABLE sesion (
    id                uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    estudiante_id     uuid NOT NULL REFERENCES estudiante(id) ON DELETE CASCADE,
    inicio            timestamptz NOT NULL DEFAULT now(),
    fin               timestamptz,
    puntaje_obtenido  integer NOT NULL DEFAULT 0
);
CREATE INDEX ix_sesion_estudiante ON sesion (estudiante_id, inicio);

CREATE TABLE ejercicio_servido (
    id             uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    sesion_id      uuid NOT NULL REFERENCES sesion(id) ON DELETE CASCADE,
    estudiante_id  uuid NOT NULL REFERENCES estudiante(id) ON DELETE CASCADE,
    ejercicio_id   uuid NOT NULL REFERENCES ejercicio(id),
    nivel          smallint NOT NULL CHECK (nivel BETWEEN 1 AND 3),   -- nivel con que se sirvió
    estado         text NOT NULL DEFAULT 'en_curso'
                   CHECK (estado IN ('en_curso', 'resuelto', 'abandonado', 'explicado')),
    pistas_usadas  smallint NOT NULL DEFAULT 0 CHECK (pistas_usadas BETWEEN 0 AND 3),
    fallos         smallint NOT NULL DEFAULT 0,
    analogo_de     uuid REFERENCES ejercicio_servido(id),              -- RF-P7
    servido_en     timestamptz NOT NULL DEFAULT now(),
    terminado_en   timestamptz
);
-- "no visto" en F1 y re-servir el más antiguo cuando la celda se agota
CREATE INDEX ix_servido_estudiante_ejercicio ON ejercicio_servido (estudiante_id, ejercicio_id, servido_en);

CREATE TABLE intento (
    id                    bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    ejercicio_servido_id  uuid NOT NULL REFERENCES ejercicio_servido(id) ON DELETE CASCADE,
    estudiante_id         uuid NOT NULL REFERENCES estudiante(id) ON DELETE CASCADE,  -- desnormalizado para el dashboard
    respuesta             text NOT NULL,
    es_correcta           boolean NOT NULL,
    pistas_usadas         smallint NOT NULL CHECK (pistas_usadas BETWEEN 0 AND 3),
    patron_error          text,                    -- causa del error común detectado, si hubo
    tiempo_segundos       integer NOT NULL CHECK (tiempo_segundos >= 0),
    puntos                integer NOT NULL DEFAULT 0,
    creado_en             timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX ix_intento_estudiante_fecha ON intento (estudiante_id, creado_en);

CREATE TABLE dominio_oa (
    estudiante_id         uuid NOT NULL REFERENCES estudiante(id) ON DELETE CASCADE,
    unidad_id             text NOT NULL REFERENCES unidad(id),
    indice                numeric(4,3) NOT NULL DEFAULT 0.5 CHECK (indice BETWEEN 0 AND 1),
    nivel_actual          smallint NOT NULL DEFAULT 2 CHECK (nivel_actual BETWEEN 1 AND 3),
    racha_correctas       smallint NOT NULL DEFAULT 0,
    intentos_en_unidad    integer NOT NULL DEFAULT 0,
    fecha_ultimo_intento  timestamptz,
    PRIMARY KEY (estudiante_id, unidad_id)
);

-- Operación del LLM --------------------------------------------------------------

CREATE TABLE llamada_llm (
    id              bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sesion_id       uuid REFERENCES sesion(id) ON DELETE SET NULL,   -- NULL en generación y triaje
    operacion       text NOT NULL CHECK (operacion IN ('generarEjercicio', 'triajeEjercicio',
                    'generarRetroalimentacion', 'generarPista', 'narrarExplicacionGuiada')),
    modelo          text NOT NULL,                  -- snapshot exacto
    version_prompt  text NOT NULL,
    tokens_entrada  integer NOT NULL DEFAULT 0,
    tokens_salida   integer NOT NULL DEFAULT 0,
    costo_usd       numeric(10,6) NOT NULL DEFAULT 0,
    latencia_ms     integer,
    resultado       text NOT NULL CHECK (resultado IN ('ok', 'timeout', 'error', 'filtrado', 'degradado', 'tope')),
    creado_en       timestamptz NOT NULL DEFAULT now()
);
-- Costo del mes en curso (alerta 80 %, corte 100 %)
CREATE INDEX ix_llamada_fecha ON llamada_llm (creado_en);

CREATE TABLE evento_filtro (
    id                    bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    ejercicio_servido_id  uuid REFERENCES ejercicio_servido(id) ON DELETE SET NULL,
    operacion             text NOT NULL,
    texto_bloqueado       text NOT NULL,           -- datos sintéticos en TT1/TT2 (RNF-S4)
    creado_en             timestamptz NOT NULL DEFAULT now()
);
"""

# Orden inverso de dependencias (claves foráneas).
TABLAS = [
    "evento_filtro",
    "llamada_llm",
    "dominio_oa",
    "intento",
    "ejercicio_servido",
    "sesion",
    "ejercicio",
    "plantilla",
    "unidad",
    "estudiante",
    "apoderado",
]


def upgrade() -> None:
    op.execute(DDL)


def downgrade() -> None:
    for tabla in TABLAS:
        op.execute(f"DROP TABLE IF EXISTS {tabla}")
