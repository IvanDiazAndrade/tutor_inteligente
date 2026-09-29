"""Modelos ORM: una clase por tabla de docs/modelo_base_datos.md (tarea 48).

La fuente de verdad del esquema es la migración inicial (DDL literal del documento); estos
modelos lo reflejan para que la API trabaje con objetos. `alembic check` confirma que ambos
coinciden. Los CHECK se repiten aquí solo como documentación: los aplica la base de datos.
"""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import CITEXT, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from tutor.db import Base

UUID_PK = {"primary_key": True, "server_default": text("gen_random_uuid()")}
AHORA = {"server_default": func.now()}


# Cuentas ---------------------------------------------------------------------------------


class Apoderado(Base):
    __tablename__ = "apoderado"

    id: Mapped[uuid.UUID] = mapped_column(**UUID_PK)
    email: Mapped[str] = mapped_column(CITEXT, unique=True)
    password_hash: Mapped[str] = mapped_column(Text)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), **AHORA)

    estudiante: Mapped["Estudiante | None"] = relationship(back_populates="apoderado")


class Estudiante(Base):
    __tablename__ = "estudiante"
    __table_args__ = (
        CheckConstraint("curso BETWEEN 4 AND 6"),
        CheckConstraint("puntaje_total >= 0"),
    )

    id: Mapped[uuid.UUID] = mapped_column(**UUID_PK)
    # UNIQUE = un apoderado, un estudiante (RF-A1, por ratificar).
    apoderado_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("apoderado.id", ondelete="CASCADE"), unique=True
    )
    alias: Mapped[str] = mapped_column(String(30))  # sin datos identificatorios (RNF-S2)
    curso: Mapped[int] = mapped_column(SmallInteger)
    pin_hash: Mapped[str] = mapped_column(Text)
    pin_fallos: Mapped[int] = mapped_column(SmallInteger, server_default=text("0"))
    bloqueado_hasta: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    puntaje_total: Mapped[int] = mapped_column(Integer, server_default=text("0"))
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), **AHORA)

    apoderado: Mapped[Apoderado] = relationship(back_populates="estudiante")


# Catálogo curricular (datos, sin lógica: RNF-M2) -------------------------------------------


class Unidad(Base):
    __tablename__ = "unidad"
    __table_args__ = (
        CheckConstraint("curso BETWEEN 4 AND 6"),
        CheckConstraint("anillo IN (1, 2)"),
        UniqueConstraint("curso", "orden"),
    )

    id: Mapped[str] = mapped_column(Text, primary_key=True)  # oaCodigo, ej. '4B-OA9'
    oa_texto_oficial: Mapped[str] = mapped_column(Text)
    descripcion_ciudadana: Mapped[str] = mapped_column(Text)
    curso: Mapped[int] = mapped_column(SmallInteger)
    basal: Mapped[bool] = mapped_column(Boolean)
    anillo: Mapped[int] = mapped_column(SmallInteger)
    orden: Mapped[int] = mapped_column(SmallInteger)
    rango_numerico: Mapped[dict[str, Any]] = mapped_column(JSONB)
    activa: Mapped[bool] = mapped_column(Boolean, server_default=text("true"))


class Plantilla(Base):
    __tablename__ = "plantilla"

    id: Mapped[str] = mapped_column(Text, primary_key=True)  # ej. '5B-OA4-div-resto'
    unidad_id: Mapped[str] = mapped_column(ForeignKey("unidad.id"))
    version: Mapped[int] = mapped_column(Integer, server_default=text("1"))
    aprobada: Mapped[bool] = mapped_column(Boolean, server_default=text("false"))
    aprobada_por: Mapped[str | None] = mapped_column(Text)
    aprobada_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


# Banco de ejercicios ---------------------------------------------------------------------


class Ejercicio(Base):
    __tablename__ = "ejercicio"
    __table_args__ = (
        CheckConstraint("nivel BETWEEN 1 AND 3"),
        CheckConstraint("fuente IN ('parametrica', 'llm', 'gold')"),
        CheckConstraint("uso_gold IN ('fewshot', 'validacion')"),
        CheckConstraint("estado IN ('borrador', 'verificado', 'activo', 'descartado', 'retirado')"),
        CheckConstraint("formato_respuesta IN ('numerico', 'fraccion', 'ordenar', 'comparar')"),
        CheckConstraint("veredicto_triaje IN ('ok', 'dudoso')"),
        CheckConstraint("(fuente = 'gold') = (uso_gold IS NOT NULL)"),
        CheckConstraint("fuente = 'gold' OR jsonb_array_length(pistas) = 3"),
        CheckConstraint("fuente <> 'parametrica' OR plantilla_id IS NOT NULL"),
        # F1: ejercicios servibles de una celda unidad×nivel (los gold nunca rotan).
        Index(
            "ix_ejercicio_celda_activa",
            "unidad_id",
            "nivel",
            postgresql_where=text("estado = 'activo' AND fuente <> 'gold'"),
        ),
        # Cola de la revisión humana: dudosos y sin triaje primero (expresión tal como la
        # normaliza PostgreSQL, para que `alembic check` no vea diferencias).
        Index(
            "ix_ejercicio_revision",
            text("(NOT veredicto_triaje IS DISTINCT FROM 'ok'::text)"),
            "creado_en",
            postgresql_where=text("estado = 'verificado'"),
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(**UUID_PK)
    unidad_id: Mapped[str] = mapped_column(ForeignKey("unidad.id"))
    nivel: Mapped[int] = mapped_column(SmallInteger)
    fuente: Mapped[str] = mapped_column(Text)
    uso_gold: Mapped[str | None] = mapped_column(Text)
    estado: Mapped[str] = mapped_column(Text, server_default=text("'borrador'"))
    enunciado: Mapped[str] = mapped_column(Text)
    representacion: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    formato_respuesta: Mapped[str] = mapped_column(Text)
    # respuesta_final y solucion_referencia nunca viajan al cliente (RF-D3, AD-1).
    respuesta_final: Mapped[str] = mapped_column(Text)
    regla_validacion: Mapped[dict[str, Any]] = mapped_column(JSONB, server_default=text("'{}'"))
    solucion_referencia: Mapped[list[str]] = mapped_column(JSONB)
    errores_comunes: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB, server_default=text("'[]'")
    )
    pistas: Mapped[list[str]] = mapped_column(JSONB, server_default=text("'[]'"))
    plantilla_id: Mapped[str | None] = mapped_column(ForeignKey("plantilla.id"))
    lote_generacion: Mapped[str | None] = mapped_column(Text)
    version_prompt: Mapped[str | None] = mapped_column(Text)
    veredicto_triaje: Mapped[str | None] = mapped_column(Text)
    motivo_descarte: Mapped[str | None] = mapped_column(Text)
    revisado_por: Mapped[str | None] = mapped_column(Text)
    revisado_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), **AHORA)


# Uso y desempeño -------------------------------------------------------------------------


class Sesion(Base):
    __tablename__ = "sesion"
    __table_args__ = (Index("ix_sesion_estudiante", "estudiante_id", "inicio"),)

    id: Mapped[uuid.UUID] = mapped_column(**UUID_PK)
    estudiante_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("estudiante.id", ondelete="CASCADE")
    )
    inicio: Mapped[datetime] = mapped_column(DateTime(timezone=True), **AHORA)
    fin: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    puntaje_obtenido: Mapped[int] = mapped_column(Integer, server_default=text("0"))


class EjercicioServido(Base):
    __tablename__ = "ejercicio_servido"
    __table_args__ = (
        CheckConstraint("nivel BETWEEN 1 AND 3"),
        CheckConstraint("estado IN ('en_curso', 'resuelto', 'abandonado', 'explicado')"),
        CheckConstraint("pistas_usadas BETWEEN 0 AND 3"),
        # "No visto" en F1 y re-servir el más antiguo cuando la celda se agota.
        Index("ix_servido_estudiante_ejercicio", "estudiante_id", "ejercicio_id", "servido_en"),
    )

    id: Mapped[uuid.UUID] = mapped_column(**UUID_PK)
    sesion_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sesion.id", ondelete="CASCADE"))
    estudiante_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("estudiante.id", ondelete="CASCADE")
    )
    ejercicio_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ejercicio.id"))
    nivel: Mapped[int] = mapped_column(SmallInteger)  # nivel con que se sirvió
    estado: Mapped[str] = mapped_column(Text, server_default=text("'en_curso'"))
    pistas_usadas: Mapped[int] = mapped_column(SmallInteger, server_default=text("0"))
    fallos: Mapped[int] = mapped_column(SmallInteger, server_default=text("0"))
    analogo_de: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("ejercicio_servido.id")
    )  # RF-P7
    servido_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), **AHORA)
    terminado_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Intento(Base):
    __tablename__ = "intento"
    __table_args__ = (
        CheckConstraint("pistas_usadas BETWEEN 0 AND 3"),
        CheckConstraint("tiempo_segundos >= 0"),
        Index("ix_intento_estudiante_fecha", "estudiante_id", "creado_en"),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    ejercicio_servido_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("ejercicio_servido.id", ondelete="CASCADE")
    )
    # Desnormalizado para las agregaciones del dashboard.
    estudiante_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("estudiante.id", ondelete="CASCADE")
    )
    respuesta: Mapped[str] = mapped_column(Text)
    es_correcta: Mapped[bool] = mapped_column(Boolean)
    pistas_usadas: Mapped[int] = mapped_column(SmallInteger)
    patron_error: Mapped[str | None] = mapped_column(Text)
    tiempo_segundos: Mapped[int] = mapped_column(Integer)
    puntos: Mapped[int] = mapped_column(Integer, server_default=text("0"))
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), **AHORA)


class DominioOA(Base):
    __tablename__ = "dominio_oa"
    __table_args__ = (
        CheckConstraint("indice BETWEEN 0 AND 1"),
        CheckConstraint("nivel_actual BETWEEN 1 AND 3"),
    )

    estudiante_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("estudiante.id", ondelete="CASCADE"), primary_key=True
    )
    unidad_id: Mapped[str] = mapped_column(ForeignKey("unidad.id"), primary_key=True)
    indice: Mapped[Decimal] = mapped_column(Numeric(4, 3), server_default=text("0.5"))
    nivel_actual: Mapped[int] = mapped_column(SmallInteger, server_default=text("2"))
    racha_correctas: Mapped[int] = mapped_column(SmallInteger, server_default=text("0"))
    intentos_en_unidad: Mapped[int] = mapped_column(Integer, server_default=text("0"))
    fecha_ultimo_intento: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


# Operación del LLM -----------------------------------------------------------------------


class LlamadaLLM(Base):
    __tablename__ = "llamada_llm"
    __table_args__ = (
        CheckConstraint(
            "operacion IN ('generarEjercicio', 'triajeEjercicio', "
            "'generarRetroalimentacion', 'generarPista', 'narrarExplicacionGuiada')"
        ),
        CheckConstraint("resultado IN ('ok', 'timeout', 'error', 'filtrado', 'degradado', 'tope')"),
        # Costo del mes en curso (alerta 80 %, corte 100 %).
        Index("ix_llamada_fecha", "creado_en"),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    sesion_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("sesion.id", ondelete="SET NULL")
    )  # NULL en generación y triaje
    operacion: Mapped[str] = mapped_column(Text)
    modelo: Mapped[str] = mapped_column(Text)  # snapshot exacto
    version_prompt: Mapped[str] = mapped_column(Text)
    tokens_entrada: Mapped[int] = mapped_column(Integer, server_default=text("0"))
    tokens_salida: Mapped[int] = mapped_column(Integer, server_default=text("0"))
    costo_usd: Mapped[Decimal] = mapped_column(Numeric(10, 6), server_default=text("0"))
    latencia_ms: Mapped[int | None] = mapped_column(Integer)
    resultado: Mapped[str] = mapped_column(Text)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), **AHORA)


class EventoFiltro(Base):
    __tablename__ = "evento_filtro"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    ejercicio_servido_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("ejercicio_servido.id", ondelete="SET NULL")
    )
    operacion: Mapped[str] = mapped_column(Text)
    texto_bloqueado: Mapped[str] = mapped_column(Text)  # datos sintéticos (RNF-S4)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), **AHORA)
