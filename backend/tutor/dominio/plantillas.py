"""Generador paramétrico (AD-9; modelo_dominio.md §4).

Cada plantilla sortea sus parámetros dentro del rango del OA y construye el ejercicio completo
con el esquema de §2: enunciado, respuesta final, solución paso a paso, errores comunes (como
fórmulas de los parámetros), tres pistas y representación pictórica opcional. El resultado es
correcto por construcción: la respuesta sale de los parámetros, nunca al revés. Los niveles
cambian los parámetros, no la plantilla.

Por ahora están las dos plantillas que el diseño especifica en detalle (§4.1 y §4.2); las
fichas del resto de las unidades se agregan aquí siguiendo el mismo patrón.
"""

import random
import re
from dataclasses import dataclass, field
from typing import Any, Protocol

from tutor.dominio.corrector import fraccion


@dataclass(frozen=True)
class EjercicioGenerado:
    unidad_id: str
    plantilla_id: str
    nivel: int
    enunciado: str
    formato_respuesta: str
    respuesta_final: str
    solucion_referencia: list[str]
    errores_comunes: list[dict[str, str]]
    pistas: list[str]
    regla_validacion: dict[str, Any] = field(default_factory=lambda: {"aceptaEquivalentes": True})
    representacion: dict[str, Any] | None = None


class Plantilla(Protocol):
    id: str
    unidad_id: str
    version: int

    def instanciar(self, nivel: int, azar: random.Random) -> EjercicioGenerado: ...


def _errores(respuesta: str, candidatos: list[tuple[str, str, str]]) -> list[dict[str, str]]:
    """Descarta errores que valen lo mismo que la respuesta o que otro error (p. ej. 2/4 y 1/2):
    un patrón ambiguo no sirve para diagnosticar la causa."""
    vistos = {fraccion(respuesta)}
    errores = []
    for valor, causa, retro in candidatos:
        if fraccion(valor) not in vistos:
            vistos.add(fraccion(valor))
            errores.append({"respuesta": valor, "causa": causa, "retroalimentacion": retro})
    return errores


def menciona(texto: str, respuesta: str) -> bool:
    """¿El texto contiene la respuesta como número o fracción suelto (no dentro de otro)?"""
    return re.search(rf"(?<![\d/]){re.escape(respuesta)}(?![\d/])", texto) is not None


def _sin_revelar(pista: str, respuesta: str, alternativa: str) -> str:
    """Si por casualidad la pista nombra la respuesta (p. ej. 99 : 9 -> "divide 11 : 9"),
    se usa una versión sin números. El filtro del tutor lo revisa de nuevo al servirla."""
    return alternativa if menciona(pista, respuesta) else pista


# 5B-OA4: división de 3 dígitos por 1 dígito, con resto (§4.1) ---------------------------


class DivisionConResto:
    id = "5B-OA4-div-resto"
    unidad_id = "5B-OA4"
    version = 1

    def instanciar(self, nivel: int, azar: random.Random) -> EjercicioGenerado:
        # N1: resto 0 y divisor 2-5 · N2: resto > 0 · N3: resto > 0 y se pregunta cociente o resto.
        divisor = azar.randint(2, 5) if nivel == 1 else azar.randint(2, 9)
        resto = 0 if nivel == 1 else azar.randint(1, divisor - 1)
        # El dividendo se construye desde el cociente y el resto (correcto por construcción).
        cociente = azar.randint(-(-(100 - resto) // divisor), (999 - resto) // divisor)
        dividendo = cociente * divisor + resto
        pide_resto = nivel == 3 and azar.random() < 0.5

        pregunta = "¿Cuál es el resto?" if pide_resto else "¿Cuál es el cociente?"
        respuesta = str(resto if pide_resto else cociente)
        pasos, ultimo_parcial = _pasos_division(dividendo, divisor)
        solucion = [*pasos, f"El cociente es {cociente} y el resto es {resto}."]

        if pide_resto:
            errores = _errores(
                respuesta,
                [
                    (
                        str(cociente),
                        "confundió cociente con resto",
                        "Ese número es cuántas veces cabe el divisor. "
                        "La pregunta pide lo que sobra.",
                    ),
                    (
                        "0",
                        "pensó que la división era exacta",
                        "Revisa el último paso: después de repartir, ¿sobró algo?",
                    ),
                ],
            )
            pista_final = _sin_revelar(
                f"El cociente es {cociente}. Multiplica {cociente} × {divisor} "
                "y réstalo al dividendo.",
                respuesta,
                "Multiplica el cociente por el divisor y réstalo al dividendo.",
            )
        else:
            errores = _errores(
                respuesta,
                [
                    (
                        str(cociente + 1),
                        "siguió dividiendo de más",
                        "Revisa el último paso: el resto tiene que ser menor que el divisor.",
                    ),
                    (
                        str(resto),
                        "confundió cociente con resto",
                        "Ese número es lo que sobra. "
                        "La pregunta pide cuántas veces cabe el divisor.",
                    ),
                ],
            )
            # A un paso del final (§4.3 del modelo pedagógico): todas las cifras menos la última.
            pista_final = _sin_revelar(
                f"El cociente empieza con {str(cociente)[:-1]}. "
                f"Ahora divide {ultimo_parcial} : {divisor}.",
                respuesta,
                "Ya tienes casi todo el cociente: te falta dividir la última parte.",
            )

        return EjercicioGenerado(
            unidad_id=self.unidad_id,
            plantilla_id=self.id,
            nivel=nivel,
            enunciado=f"Calcula {dividendo} : {divisor}. {pregunta}",
            formato_respuesta="numerico",
            respuesta_final=respuesta,
            solucion_referencia=solucion,
            errores_comunes=errores,
            pistas=[
                "Dividir es repartir en partes iguales. "
                "Empieza por las primeras cifras del dividendo.",
                _sin_revelar(
                    pasos[0],
                    respuesta,
                    "Divide las primeras cifras del dividendo por el divisor y anota lo que sobra.",
                ),
                pista_final,
            ],
        )


def _pasos_division(dividendo: int, divisor: int) -> tuple[list[str], int]:
    """Pasos del algoritmo de la división, cifra por cifra, en lenguaje de 5° básico.
    Devuelve también el último número que se divide (para la pista 3)."""
    cifras = str(dividendo)
    pasos: list[str] = []
    parcial = 0
    ultimo = 0
    empezo = False
    for i, cifra in enumerate(cifras):
        parcial = parcial * 10 + int(cifra)
        if not empezo and parcial < divisor and i < len(cifras) - 1:
            continue
        cabe = parcial // divisor
        ultimo = parcial
        sobra = parcial - cabe * divisor
        prefijo = "Se baja el " + cifra + f" y queda {parcial}. " if empezo else ""
        pasos.append(
            f"{prefijo}{parcial} : {divisor} = {cabe}, porque {cabe} × {divisor} = "
            f"{cabe * divisor}. Sobra {sobra}."
        )
        parcial = sobra
        empezo = True
    return pasos, ultimo


# 4B-OA9: suma y resta de fracciones con igual denominador (§4.2) ------------------------


class SumaIgualDenominador:
    id = "4B-OA9-suma-igual-den"
    unidad_id = "4B-OA9"
    version = 1
    DENOMINADORES = [2, 3, 4, 5, 6, 8, 10, 12]

    def instanciar(self, nivel: int, azar: random.Random) -> EjercicioGenerado:
        # N1: d ≤ 4, siempre pictórico · N2: cualquier d, pictórico la mitad de las veces ·
        # N3: resta, o suma cuyo resultado es 1.
        # En N1 y N2 el resultado es propio (a + b < d), así que d = 2 no sirve: 1/2 + 1/2 = 1.
        opciones = [d for d in self.DENOMINADORES if d >= 3 and (nivel != 1 or d <= 4)]
        d = azar.choice(opciones if nivel < 3 else self.DENOMINADORES)
        resta = nivel == 3 and azar.random() < 0.5
        if resta:
            a = azar.randint(2, d)
            b = azar.randint(1, a - 1)
            resultado = a - b
        elif nivel == 3:
            a = azar.randint(1, d - 1)
            b = d - a
            resultado = d
        else:
            a = azar.randint(1, d - 2)
            b = azar.randint(1, d - a - 1)
            resultado = a + b

        signo = "−" if resta else "+"
        respuesta = f"{resultado}/{d}"
        operacion = "Se restan" if resta else "Se suman"
        solucion = [
            f"Los denominadores ya son iguales ({d}), así que no hay que cambiarlos.",
            f"{operacion} solo los numeradores: {a} {signo} {b} = {resultado}.",
            f"El resultado es {respuesta}.",
        ]
        if resta:
            candidatos = [
                (
                    f"{a + b}/{d}",
                    "sumó en vez de restar",
                    "Fíjate en el signo: aquí hay que restar.",
                ),
            ]
        else:
            candidatos = [
                (
                    f"{a + b}/{2 * d}",
                    "sumó también los denominadores",
                    "Cuando los denominadores son iguales, se mantienen: "
                    "solo se suman los numeradores.",
                ),
                (
                    str(a + b),
                    "ignoró el denominador",
                    "El resultado es una fracción: no olvides el número de abajo.",
                ),
                (
                    f"{a * b}/{d}",
                    "multiplicó los numeradores",
                    "Es una suma: los numeradores se suman, no se multiplican.",
                ),
            ]

        pictorico = not resta and (nivel == 1 or nivel == 3 or azar.random() < 0.5)
        return EjercicioGenerado(
            unidad_id=self.unidad_id,
            plantilla_id=self.id,
            nivel=nivel,
            enunciado=f"Calcula {a}/{d} {signo} {b}/{d}.",
            formato_respuesta="fraccion",
            respuesta_final=respuesta,
            solucion_referencia=solucion,
            errores_comunes=_errores(respuesta, candidatos),
            pistas=[
                "Mira los números de abajo. ¿Qué tienen en común?",
                "Si los denominadores son iguales, el denominador del resultado es el mismo.",
                f"{'Resta' if resta else 'Suma'} solo los numeradores: {a} {signo} {b}. "
                f"El denominador sigue siendo {d}.",
            ],
            representacion=(
                {
                    "tipo": "fraccion-circulo",
                    "parametros": {"denominador": d, "partesDestacadas": [a, b]},
                }
                if pictorico
                else None
            ),
        )


PLANTILLAS: dict[str, Plantilla] = {p.id: p for p in (DivisionConResto(), SumaIgualDenominador())}
