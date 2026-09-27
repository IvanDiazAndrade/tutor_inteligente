// Cliente HTTP de la API. En el emulador de Android, 10.0.2.2 es el "localhost" del PC.
// Para un teléfono real o para Render, definir EXPO_PUBLIC_API_URL (ver .env.example).
export const API_URL = process.env.EXPO_PUBLIC_API_URL ?? 'http://10.0.2.2:8000';

const TIEMPO_MAXIMO_MS = 8000;

async function obtenerJson<T>(ruta: string): Promise<T> {
  const controlador = new AbortController();
  const temporizador = setTimeout(() => controlador.abort(), TIEMPO_MAXIMO_MS);
  try {
    const respuesta = await fetch(`${API_URL}${ruta}`, { signal: controlador.signal });
    if (!respuesta.ok) {
      throw new Error(`HTTP ${respuesta.status}`);
    }
    return (await respuesta.json()) as T;
  } finally {
    clearTimeout(temporizador);
  }
}

export type Salud = {
  estado: string;
  version: string;
  base_datos: string;
};

export const obtenerSalud = () => obtenerJson<Salud>('/salud');
