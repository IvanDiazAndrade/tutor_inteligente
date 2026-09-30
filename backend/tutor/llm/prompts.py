"""Plantillas de prompts versionadas fuera del código (RNF-M1; estrategia_llm.md §6).

Cada archivo de /prompts declara su versión en el comentario inicial ("version: retro-v1").
Esa versión se guarda en cada llamada (llamada_llm.version_prompt) para comparar la calidad
entre versiones durante la calibración (tarea 58).
"""

import re
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, StrictUndefined

_VERSION = re.compile(r"version:\s*([\w.-]+)")


@dataclass(frozen=True)
class PromptVersionado:
    texto: str
    version: str


class RepositorioPrompts:
    def __init__(self, carpeta: str | Path):
        self.carpeta = Path(carpeta)
        # StrictUndefined: una variable que falte es un error, no un hueco silencioso en el prompt.
        self._entorno = Environment(
            loader=FileSystemLoader(self.carpeta),
            undefined=StrictUndefined,
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=False,
            autoescape=False,
        )

    @cache  # noqa: B019 — un repositorio por proceso; las plantillas no cambian en caliente
    def version(self, nombre: str) -> str:
        cabecera = (self.carpeta / f"{nombre}.jinja").read_text(encoding="utf-8")[:400]
        encontrada = _VERSION.search(cabecera)
        if not encontrada:
            raise ValueError(f"La plantilla {nombre} no declara su versión.")
        return encontrada.group(1)

    def render(self, nombre: str, **variables: Any) -> PromptVersionado:
        texto = self._entorno.get_template(f"{nombre}.jinja").render(**variables).strip()
        return PromptVersionado(texto=texto, version=self.version(nombre))
