// Datos de ejemplo del panel del apoderado (tarea 42). En la Fase IV los entrega el servicio
// dashboard (F4) agregando intentos y sesiones de la base de datos, sin LLM (AD-6).

export type ResumenSemana = {
  ejercicios: number;
  correctos: number;
  // Minutos de práctica por día, de lunes a domingo (RF-DA1: tiempo de uso y frecuencia).
  minutosPorDia: [number, number, number, number, number, number, number];
};

export type Periodo = 'esta' | 'pasada';

export const RESUMENES_EJEMPLO: Record<Periodo, ResumenSemana> = {
  esta: { ejercicios: 23, correctos: 16, minutosPorDia: [35, 0, 40, 0, 25, 0, 0] },
  pasada: { ejercicios: 17, correctos: 11, minutosPorDia: [0, 20, 0, 30, 0, 25, 0] },
};

// Pistas usadas en promedio por ejercicio en cada unidad durante la semana. Alimenta el
// indicador de "unidades con mayor dificultad" (RF-DA3).
export const PISTAS_PROMEDIO_EJEMPLO: Record<string, number> = {
  '5B-OA1': 0.2,
  '5B-OA3': 0.6,
  '5B-OA4': 0.9,
  '5B-OA7': 1.8,
  '5B-OA9': 1.1,
};
