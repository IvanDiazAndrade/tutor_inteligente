// Corrector del prototipo: versión reducida de modelo_dominio.md §3 para simular la pantalla.
// En la Fase IV corrige el servidor (AD-2); la app nunca conoce la respuesta final.
// Solo usa enteros: nada de números con decimales flotantes.

import type { EjercicioEjemplo, ErrorComun } from '@/datos/ejercicios';

export type ResultadoCorreccion =
  | { tipo: 'formato_invalido'; mensaje: string }
  | { tipo: 'correcta'; esFormaCanonica: boolean }
  | { tipo: 'incorrecta'; errorComun?: ErrorComun };

type Fraccion = { num: number; den: number };

const aFraccion = (texto: string): Fraccion | null => {
  const m = /^\s*(\d+)\s*\/\s*(\d+)\s*$/.exec(texto);
  return m ? { num: Number(m[1]), den: Number(m[2]) } : null;
};

const equivalentes = (a: Fraccion, b: Fraccion) => a.num * b.den === b.num * a.den;

export function corregir(respuesta: string, ejercicio: EjercicioEjemplo): ResultadoCorreccion {
  if (ejercicio.formatoRespuesta === 'fraccion') {
    const dada = aFraccion(respuesta);
    if (!dada)
      return { tipo: 'formato_invalido', mensaje: 'Escribe los dos números de la fracción.' };
    if (dada.den === 0) {
      return { tipo: 'formato_invalido', mensaje: 'El número de abajo no puede ser 0.' };
    }
    const esperada = aFraccion(ejercicio.respuestaFinal)!;
    const exacta = dada.num === esperada.num && dada.den === esperada.den;
    if (exacta || (ejercicio.aceptaEquivalentes && equivalentes(dada, esperada))) {
      return { tipo: 'correcta', esFormaCanonica: exacta };
    }
    const errorComun = ejercicio.erroresComunes.find((e) => {
      const f = aFraccion(e.respuesta);
      return f !== null && f.num === dada.num && f.den === dada.den;
    });
    return { tipo: 'incorrecta', errorComun };
  }

  const limpia = respuesta.replace(/\s/g, '');
  if (!/^\d+$/.test(limpia)) return { tipo: 'formato_invalido', mensaje: 'Escribe un número.' };
  if (Number(limpia) === Number(ejercicio.respuestaFinal)) {
    return { tipo: 'correcta', esFormaCanonica: true };
  }
  const errorComun = ejercicio.erroresComunes.find((e) => Number(e.respuesta) === Number(limpia));
  return { tipo: 'incorrecta', errorComun };
}

// Puntos provisorios del prototipo (RF-G1): 10 por nivel, con el mismo descuento por pista que
// el índice de dominio (−15 % por pista, piso 40 %). La fórmula definitiva se fija en la Fase IV.
export const puntosPor = (nivel: number, pistasUsadas: number) =>
  Math.round(10 * nivel * Math.max(0.4, 1 - 0.15 * pistasUsadas));
