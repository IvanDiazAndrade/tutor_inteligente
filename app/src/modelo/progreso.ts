// Reglas del modelo del estudiante que la app muestra (modelo_estudiante.md §5 y §6).
// En la Fase IV el servidor entrega estos valores ya calculados; aquí se usan para que el
// prototipo muestre exactamente lo que el diseño define.

export const UMBRAL_BAJO = 0.4;
export const UMBRAL_ALTO = 0.8;
export const DIAS_PARA_REPASAR = 21;

// nombre: corto, para el estudiante. ciudadana: descripción para el apoderado (RF-DA2).
export type Unidad = { id: string; curso: number; nombre: string; ciudadana: string };

export type Dominio = {
  unidadId: string;
  indice: number;
  fechaUltimoIntento: Date;
};

export type Banda = 'Empezando' | 'Practicando' | 'Dominado';

export function banda(indice: number): Banda {
  if (indice < UMBRAL_BAJO) return 'Empezando';
  if (indice < UMBRAL_ALTO) return 'Practicando';
  return 'Dominado';
}

// Estrellas de la vista del estudiante: 0 si la unidad no se ha iniciado, luego una por banda.
export function estrellas(dominio?: Dominio): number {
  if (!dominio) return 0;
  return { Empezando: 1, Practicando: 2, Dominado: 3 }[banda(dominio.indice)];
}

const MS_POR_DIA = 24 * 60 * 60 * 1000;

export function paraRepasar(dominio: Dominio | undefined, hoy: Date): boolean {
  if (!dominio || dominio.indice < UMBRAL_BAJO) return false;
  return hoy.getTime() - dominio.fechaUltimoIntento.getTime() > DIAS_PARA_REPASAR * MS_POR_DIA;
}

// Unidad sugerida (§5): 1) la "para repasar" más antigua; 2) la iniciada con menor índice
// (< 0,6); 3) la siguiente no iniciada según el orden del catálogo de su curso.
export function unidadSugerida(
  unidades: Unidad[],
  dominios: Map<string, Dominio>,
  hoy: Date,
  curso: number,
): Unidad | undefined {
  const aRepasar = unidades
    .filter((u) => paraRepasar(dominios.get(u.id), hoy))
    .sort(
      (a, b) =>
        dominios.get(a.id)!.fechaUltimoIntento.getTime() -
        dominios.get(b.id)!.fechaUltimoIntento.getTime(),
    );
  if (aRepasar.length > 0) return aRepasar[0];

  const debiles = unidades
    .filter((u) => (dominios.get(u.id)?.indice ?? 1) < 0.6)
    .sort((a, b) => dominios.get(a.id)!.indice - dominios.get(b.id)!.indice);
  if (debiles.length > 0) return debiles[0];

  return unidades.find((u) => u.curso === curso && !dominios.has(u.id));
}
