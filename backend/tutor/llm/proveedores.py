"""Proveedores de LLM detrás de una interfaz propia (AD-4, RNF-M3).

El adaptador solo conoce `ProveedorLLM`: cambiar de OpenAI a otro proveedor (p. ej. Gemini
Flash-Lite, estrategia_llm.md §2) es escribir otra clase con el mismo método `completar`.
`ProveedorSimulado` responde sin red: lo usan las pruebas y la CI, que nunca gastan tokens.
"""

from collections import deque
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Protocol

from pydantic import BaseModel


@dataclass(frozen=True)
class Solicitud:
    modelo: str
    instrucciones: str  # system prompt
    entrada: str  # prompt de la operación
    temperatura: float | None
    max_tokens: int
    timeout: float
    esquema: type[BaseModel] | None = None  # structured output


@dataclass(frozen=True)
class RespuestaLLM:
    texto: str
    datos: BaseModel | None
    tokens_entrada: int
    tokens_salida: int


class ErrorTransitorio(Exception):
    """Timeout, límite de tasa (429) o error del servidor (5xx): vale la pena reintentar."""


class ErrorPermanente(Exception):
    """Clave inválida, solicitud mal formada, salida que no cumple el esquema: no se reintenta."""


class ProveedorLLM(Protocol):
    nombre: str

    def completar(self, solicitud: Solicitud) -> RespuestaLLM: ...


class ProveedorOpenAI:
    """OpenAI con la Responses API. `store=False`: OpenAI no guarda la conversación."""

    nombre = "openai"

    def __init__(self, api_key: str):
        import openai  # importación diferida: sin clave no se necesita

        self._openai = openai
        # Los reintentos los maneja el adaptador (política propia, estrategia_llm.md §5).
        self._cliente = openai.OpenAI(api_key=api_key, max_retries=0)

    def completar(self, solicitud: Solicitud) -> RespuestaLLM:
        o = self._openai
        parametros: dict[str, Any] = {
            "model": solicitud.modelo,
            "instructions": solicitud.instrucciones,
            "input": solicitud.entrada,
            "max_output_tokens": solicitud.max_tokens,
            "store": False,
            "timeout": solicitud.timeout,
        }
        if solicitud.temperatura is not None:
            parametros["temperature"] = solicitud.temperatura
        try:
            if solicitud.esquema is not None:
                respuesta = self._cliente.responses.parse(
                    text_format=solicitud.esquema, **parametros
                )
                datos = respuesta.output_parsed
                if datos is None:
                    raise ErrorPermanente("La salida no cumple el esquema.")
            else:
                respuesta = self._cliente.responses.create(**parametros)
                datos = None
        except (
            o.APITimeoutError,
            o.APIConnectionError,
            o.RateLimitError,
            o.InternalServerError,
        ) as e:
            raise ErrorTransitorio(str(e)) from e
        except o.OpenAIError as e:
            raise ErrorPermanente(str(e)) from e
        uso = respuesta.usage
        return RespuestaLLM(
            texto=respuesta.output_text or "",
            datos=datos,
            tokens_entrada=uso.input_tokens if uso else 0,
            tokens_salida=uso.output_tokens if uso else 0,
        )


class ProveedorSimulado:
    """Devuelve respuestas preparadas en orden, o las calcula con una función.

    Cada elemento puede ser un texto, un modelo Pydantic (salida estructurada) o una
    excepción, que se lanza en vez de responder (para simular fallas).
    """

    nombre = "simulado"

    def __init__(
        self,
        respuestas: list[str | BaseModel | Exception] | None = None,
        funcion: Callable[[Solicitud], str | BaseModel] | None = None,
    ):
        self._cola = deque(respuestas or [])
        self._funcion = funcion
        self.solicitudes: list[Solicitud] = []

    def completar(self, solicitud: Solicitud) -> RespuestaLLM:
        self.solicitudes.append(solicitud)
        if self._cola:
            salida = self._cola.popleft()
        elif self._funcion:
            salida = self._funcion(solicitud)
        else:
            raise ErrorTransitorio("El simulador no tiene más respuestas preparadas.")
        if isinstance(salida, Exception):
            raise salida
        datos = salida if isinstance(salida, BaseModel) else None
        texto = salida.model_dump_json() if datos else str(salida)
        return RespuestaLLM(
            texto=texto,
            datos=datos,
            tokens_entrada=len(solicitud.instrucciones + solicitud.entrada) // 4,
            tokens_salida=len(texto) // 4,
        )
