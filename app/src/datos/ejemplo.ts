// Datos de ejemplo del prototipo (tarea 42), sintéticos (RNF-S4). Desde la tarea 50 el acceso,
// la home y el perfil usan la API; esto queda solo para el panel del apoderado (tarea 65) y
// los puntos iniciales del ejercicio (tareas 56-61).
import type { Dominio, Unidad } from '@/modelo/progreso';

// Estudiante de ejemplo para los indicadores del panel del apoderado (hasta la tarea 65).
export const ESTUDIANTE_EJEMPLO = { alias: 'Vale', curso: 5 };

// Unidades del Anillo 1 para 4° y 5° (modelo_dominio.md §4). Los nombres cortos (estudiante) y las
// descripciones ciudadanas (apoderado) son provisorios: en la Fase IV vienen del catálogo.
export const UNIDADES: Unidad[] = [
  {
    id: '4B-OA1',
    curso: 4,
    nombre: 'Números hasta 10.000',
    ciudadana: 'Leer y escribir números hasta 10.000',
  },
  {
    id: '4B-OA2',
    curso: 4,
    nombre: 'Cálculo mental',
    ciudadana: 'Tablas de multiplicar y división mental',
  },
  {
    id: '4B-OA3',
    curso: 4,
    nombre: 'Sumar y restar hasta 1.000',
    ciudadana: 'Sumar y restar números hasta 1.000',
  },
  {
    id: '4B-OA5',
    curso: 4,
    nombre: 'Multiplicación',
    ciudadana: 'Multiplicar un número de tres cifras por uno de una',
  },
  {
    id: '4B-OA6',
    curso: 4,
    nombre: 'División',
    ciudadana: 'Dividir un número de dos cifras por uno de una',
  },
  {
    id: '4B-OA7',
    curso: 4,
    nombre: 'Problemas con dinero',
    ciudadana: 'Resolver problemas con dinero',
  },
  {
    id: '4B-OA8',
    curso: 4,
    nombre: '¿Qué es una fracción?',
    ciudadana: 'Entender qué es una fracción',
  },
  {
    id: '4B-OA9',
    curso: 4,
    nombre: 'Sumar y restar fracciones',
    ciudadana: 'Sumar y restar fracciones con el mismo denominador',
  },
  {
    id: '5B-OA1',
    curso: 5,
    nombre: 'Números grandes',
    ciudadana: 'Leer y escribir números grandes',
  },
  {
    id: '5B-OA3',
    curso: 5,
    nombre: 'Multiplicación',
    ciudadana: 'Multiplicar números de dos cifras',
  },
  {
    id: '5B-OA4',
    curso: 5,
    nombre: 'División con resto',
    ciudadana: 'Dividir con resto',
  },
  {
    id: '5B-OA5',
    curso: 5,
    nombre: 'Operaciones combinadas',
    ciudadana: 'Resolver operaciones combinadas con paréntesis',
  },
  {
    id: '5B-OA6',
    curso: 5,
    nombre: 'Problemas con las 4 operaciones',
    ciudadana: 'Resolver problemas con las cuatro operaciones',
  },
  {
    id: '5B-OA7',
    curso: 5,
    nombre: 'Fracciones equivalentes',
    ciudadana: 'Fracciones equivalentes',
  },
  {
    id: '5B-OA9',
    curso: 5,
    nombre: 'Sumar y restar fracciones',
    ciudadana: 'Sumar y restar fracciones',
  },
  {
    id: '5B-OA10',
    curso: 5,
    nombre: 'De fracción a decimal',
    ciudadana: 'Pasar de fracción a número decimal',
  },
  {
    id: '5B-OA11',
    curso: 5,
    nombre: 'Comparar decimales',
    ciudadana: 'Comparar y ordenar números decimales',
  },
  {
    id: '5B-OA12',
    curso: 5,
    nombre: 'Sumar y restar decimales',
    ciudadana: 'Sumar y restar números decimales',
  },
  {
    id: '5B-OA13',
    curso: 5,
    nombre: 'Problemas con fracciones y decimales',
    ciudadana: 'Resolver problemas con fracciones y decimales',
  },
];

const haceDias = (dias: number) => new Date(Date.now() - dias * 24 * 60 * 60 * 1000);

// Progreso de Vale: índice de dominio por unidad (DominioOA). Las unidades sin fila no se han
// iniciado. 5B-OA7 lleva más de 21 días sin práctica, por eso queda "para repasar".
export const DOMINIOS_EJEMPLO: Dominio[] = [
  { unidadId: '4B-OA1', indice: 0.92, fechaUltimoIntento: haceDias(18) },
  { unidadId: '4B-OA8', indice: 0.84, fechaUltimoIntento: haceDias(15) },
  { unidadId: '4B-OA9', indice: 0.71, fechaUltimoIntento: haceDias(12) },
  { unidadId: '5B-OA1', indice: 0.9, fechaUltimoIntento: haceDias(2) },
  { unidadId: '5B-OA3', indice: 0.66, fechaUltimoIntento: haceDias(1) },
  { unidadId: '5B-OA4', indice: 0.62, fechaUltimoIntento: haceDias(3) },
  { unidadId: '5B-OA7', indice: 0.64, fechaUltimoIntento: haceDias(25) },
  { unidadId: '5B-OA9', indice: 0.32, fechaUltimoIntento: haceDias(1) },
];

export const PUNTOS_EJEMPLO = 1250;
