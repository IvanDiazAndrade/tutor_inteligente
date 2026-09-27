// Datos de ejemplo del prototipo (tarea 42). Son sintéticos (RNF-S4) y se reemplazan por
// la API en la Fase IV: los perfiles vendrán de expo-secure-store y el PIN lo valida el servidor.
export type PerfilLocal = { id: string; alias: string; curso: number };

export const PERFILES_EJEMPLO: PerfilLocal[] = [
  { id: 'ejemplo-vale', alias: 'Vale', curso: 5 },
];

// Solo para el prototipo: el PIN real se compara con bcrypt en el servidor (CU-1).
export const PIN_EJEMPLO = '1234';
