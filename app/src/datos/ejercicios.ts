// Ejercicios de ejemplo del prototipo (tarea 42), con el esquema de modelo_dominio.md §2.
// En la Fase IV la app recibe solo enunciado, representación y formato (EjercicioParaEstudiante):
// la respuesta, la solución y los errores comunes se quedan en el servidor (RF-D3, AD-1).

export type ErrorComun = { respuesta: string; causa: string; retroalimentacion: string };

export type EjercicioEjemplo = {
  id: string;
  unidadId: string;
  unidadNombre: string;
  nivel: 1 | 2 | 3;
  enunciado: string;
  representacion?: { tipo: 'fraccion-circulo'; denominador: number; partesDestacadas: number[] };
  formatoRespuesta: 'fraccion' | 'numerico';
  respuestaFinal: string;
  aceptaEquivalentes: boolean;
  solucionReferencia: string[];
  erroresComunes: ErrorComun[];
  pistas: [string, string, string];
  // Lo que respondería "No entiendo". En la Fase IV lo redacta el LLM; aquí es un ejemplo.
  reexplicacion: string;
  analogoId?: string;
};

export const EJERCICIOS: EjercicioEjemplo[] = [
  // Ejemplo literal de modelo_dominio.md §2.
  {
    id: 'ej-pizza',
    unidadId: '4B-OA9',
    unidadNombre: 'Fracciones: sumar con igual denominador',
    nivel: 2,
    enunciado:
      'Pedro tiene 1/4 de pizza y su hermana le regala 2/4 más. ¿Qué fracción de pizza tiene ahora?',
    representacion: { tipo: 'fraccion-circulo', denominador: 4, partesDestacadas: [1, 2] },
    formatoRespuesta: 'fraccion',
    respuestaFinal: '3/4',
    aceptaEquivalentes: true,
    solucionReferencia: [
      'Los denominadores ya son iguales (4), así que no hay que cambiarlos.',
      'Se suman solo los numeradores: 1 + 2 = 3.',
      'El resultado es 3/4 de pizza.',
    ],
    erroresComunes: [
      {
        respuesta: '3/8',
        causa: 'sumó también los denominadores',
        retroalimentacion:
          'Cuando los denominadores son iguales, se mantienen: solo se suman los numeradores.',
      },
    ],
    pistas: [
      'Fíjate en los denominadores. ¿Son iguales o distintos?',
      'Cuando los denominadores son iguales, se mantienen. Solo trabajas con los de arriba.',
      'Suma solo los numeradores: 1 + 2. El denominador sigue siendo 4.',
    ],
    reexplicacion:
      'Imagina la pizza cortada en 4 trozos iguales. Pedro tenía algunos trozos y le dieron otros más. ¿Cuántos trozos de 4 tiene en total?',
    analogoId: 'ej-suma-sextos',
  },
  // Instancia de la plantilla paramétrica 4B-OA9-suma-igual-den (modelo_dominio.md §4.2).
  {
    id: 'ej-suma-sextos',
    unidadId: '4B-OA9',
    unidadNombre: 'Fracciones: sumar con igual denominador',
    nivel: 2,
    enunciado: 'Calcula 2/6 + 3/6.',
    representacion: { tipo: 'fraccion-circulo', denominador: 6, partesDestacadas: [2, 3] },
    formatoRespuesta: 'fraccion',
    respuestaFinal: '5/6',
    aceptaEquivalentes: true,
    solucionReferencia: [
      'Los denominadores son iguales (6), así que se mantienen.',
      'Se suman los numeradores: 2 + 3 = 5.',
      'El resultado es 5/6.',
    ],
    erroresComunes: [
      {
        respuesta: '5/12',
        causa: 'sumó también los denominadores',
        retroalimentacion:
          'Cuando los denominadores son iguales, se mantienen: solo se suman los numeradores.',
      },
    ],
    pistas: [
      'Mira los números de abajo. ¿Qué tienen en común?',
      'Si los denominadores son iguales, el denominador del resultado es el mismo.',
      'Suma solo los numeradores: 2 + 3. El denominador sigue siendo 6.',
    ],
    reexplicacion:
      'Piensa en un círculo cortado en 6 partes iguales. Pinta 2 partes y luego 3 más. ¿Cuántas partes de 6 pintaste?',
  },
  // Instancia de la plantilla paramétrica 5B-OA4-div-resto, nivel 2 (modelo_dominio.md §4.1).
  {
    id: 'ej-division',
    unidadId: '5B-OA4',
    unidadNombre: 'División con resto',
    nivel: 2,
    enunciado: 'Calcula 157 : 6. ¿Cuál es el cociente?',
    formatoRespuesta: 'numerico',
    respuestaFinal: '26',
    aceptaEquivalentes: false,
    solucionReferencia: [
      'Se divide 15 : 6 = 2, porque 2 × 6 = 12. Sobran 15 − 12 = 3.',
      'Se baja el 7 y queda 37. Luego 37 : 6 = 6, porque 6 × 6 = 36. Sobra 1.',
      'El cociente es 26 y el resto es 1.',
    ],
    erroresComunes: [
      {
        respuesta: '27',
        causa: 'siguió dividiendo de más',
        retroalimentacion: 'Revisa el último paso: el resto tiene que ser menor que el divisor.',
      },
      {
        respuesta: '1',
        causa: 'confundió cociente con resto',
        retroalimentacion: 'Ese número es lo que sobra. La pregunta pide cuántas veces cabe el 6.',
      },
    ],
    pistas: [
      'Empieza por las primeras cifras del dividendo: ¿cuántas veces cabe el 6 en 15?',
      'El 6 cabe 2 veces en 15 y sobran 3. Ahora baja el 7.',
      'Te queda 37 : 6. El cociente empieza con 2; busca la segunda cifra.',
    ],
    reexplicacion:
      'Dividir es repartir: tienes 157 dulces y los repartes en 6 bolsas iguales. ¿Cuántos dulces van en cada bolsa?',
  },
];

export const ejercicioPorId = (id: string) => EJERCICIOS.find((e) => e.id === id) ?? EJERCICIOS[0];

// Refuerzo positivo por plantilla local, sin LLM (modelo_pedagogico.md §3).
export const REFUERZOS = [
  '¡Muy bien! Lo lograste.',
  '¡Excelente! Vas muy bien.',
  '¡Eso es! Sigue así.',
  '¡Genial! Lo resolviste tú.',
];
