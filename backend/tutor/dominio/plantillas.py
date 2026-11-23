"""Generador paramétrico (AD-9; modelo_dominio.md §4).

Cada plantilla sortea sus parámetros dentro del rango del OA y construye el ejercicio completo
con el esquema de §2: enunciado, respuesta final, solución paso a paso, errores comunes (como
fórmulas de los parámetros), tres pistas y representación pictórica opcional. El resultado es
correcto por construcción: la respuesta sale de los parámetros, nunca al revés. Los niveles
cambian los parámetros, no la plantilla.

Aquí están los dos ejemplares que el diseño especifica en detalle (§4.1 y §4.2) y el registro
de todas las plantillas; las demás fichas están en plantillas_cuarto, _quinto y _sexto. Las
unidades solo LLM de §4 no tienen plantilla: se llenan con el pipeline de F5.
"""

import random

from tutor.dominio.columnas import con_bloque, pistas_division, separar_bloque
from tutor.dominio.plantillas_base import (
    EjercicioGenerado,
    Plantilla,
    _errores,
    _sin_revelar,
    menciona,
    revela,
)
from tutor.dominio.plantillas_cuarto import (
    ConceptoFraccion,
    Division,
    Multiplicacion,
    SumaResta,
    TablasMentales,
    ValorPosicional,
)
from tutor.dominio.plantillas_quinto import (
    CompararDecimales,
    Equivalencia,
    FraccionDecimal,
    Multiplicacion2x2,
    NumerosGrandes,
    OperatoriaCombinada,
    SumaDistintoDenominador,
    SumaRestaDecimales,
)
from tutor.dominio.plantillas_sexto import (
    ImpropiasMixtos,
    MultiplicarDividirDecimales,
    OperatoriaMixtos,
)

__all__ = ["PLANTILLAS", "EjercicioGenerado", "Plantilla", "menciona", "revela"]


# 5B-OA4: división de 3 dígitos por 1 dígito, con resto (§4.1) ---------------------------


class DivisionConResto:
    id = "5B-OA4-div-resto"
    unidad_id = "5B-OA4"
    version = 2  # v2: pistas con la división escrita paso a paso (columnas.py)

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
        pasos, _ = _pasos_division(dividendo, divisor)
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

        # La división escrita paso a paso (columnas.py): la pista 3 deja todo hecho salvo el
        # último paso, así no se ve ni la última cifra del cociente ni el resto.
        estrategia, primer_paso, casi = pistas_division(dividendo, divisor)
        if pide_resto:
            frase, bloque = separar_bloque(casi)
            casi = con_bloque(f"{frase} Lo que sobra al final es el resto.", bloque)
        generica = "Divide la parte que falta y fíjate en lo que sobra."

        return EjercicioGenerado(
            unidad_id=self.unidad_id,
            plantilla_id=self.id,
            nivel=nivel,
            enunciado=f"Calcula {dividendo} : {divisor}. {pregunta}",
            formato_respuesta="numerico",
            respuesta_final=respuesta,
            solucion_referencia=solucion,
            errores_comunes=errores,
            pistas=[_sin_revelar(p, respuesta, generica) for p in (estrategia, primer_paso, casi)],
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


PLANTILLAS: dict[str, Plantilla] = {
    p.id: p
    for p in (
        ValorPosicional(),
        TablasMentales(),
        SumaResta(),
        Multiplicacion(),
        Division(),
        ConceptoFraccion(),
        SumaIgualDenominador(),
        NumerosGrandes(),
        Multiplicacion2x2(),
        DivisionConResto(),
        OperatoriaCombinada(),
        Equivalencia(),
        SumaDistintoDenominador(),
        FraccionDecimal(),
        CompararDecimales(),
        SumaRestaDecimales(),
        ImpropiasMixtos(),
        OperatoriaMixtos(),
        MultiplicarDividirDecimales(),
    )
}
