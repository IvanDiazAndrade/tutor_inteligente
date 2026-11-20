"""Plantillas paramétricas de 5° básico (modelo_dominio.md §4)."""

import random

from tutor.dominio.plantillas.base import EjercicioGenerado, _errores, _sin_revelar

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
