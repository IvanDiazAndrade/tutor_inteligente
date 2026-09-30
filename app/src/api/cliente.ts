// Cliente HTTP de la API. En el emulador de Android, 10.0.2.2 es el "localhost" del PC.
// Para un teléfono real o para Render, definir EXPO_PUBLIC_API_URL (ver .env.example).
// Los tipos vienen de esquema.ts, generado desde el OpenAPI del backend (npm run api:tipos).
import type { components } from '@/api/esquema';

export type Esquemas = components['schemas'];
export type PerfilEstudiante = Esquemas['PerfilEstudiante'];
export type UnidadEstudiante = Esquemas['UnidadEstudiante'];
export type Token = Esquemas['Token'];

export const API_URL = process.env.EXPO_PUBLIC_API_URL ?? 'http://10.0.2.2:8000';

const TIEMPO_MAXIMO_MS = 8000;

// Error con el código HTTP y un mensaje listo para mostrar. estado 0 = sin conexión.
export class ErrorApi extends Error {
  constructor(
    public readonly estado: number,
    mensaje: string,
  ) {
    super(mensaje);
  }
}

type Opciones = { cuerpo?: unknown; token?: string | null };

async function pedir<T>(metodo: 'GET' | 'POST' | 'PATCH', ruta: string, op: Opciones = {}) {
  const controlador = new AbortController();
  const temporizador = setTimeout(() => controlador.abort(), TIEMPO_MAXIMO_MS);
  let respuesta: Response;
  try {
    respuesta = await fetch(`${API_URL}${ruta}`, {
      method: metodo,
      signal: controlador.signal,
      headers: {
        ...(op.cuerpo !== undefined && { 'Content-Type': 'application/json' }),
        ...(op.token && { Authorization: `Bearer ${op.token}` }),
      },
      body: op.cuerpo !== undefined ? JSON.stringify(op.cuerpo) : undefined,
    });
  } catch {
    throw new ErrorApi(0, 'No pudimos conectar con el servidor. Revisa tu conexión.');
  } finally {
    clearTimeout(temporizador);
  }

  if (!respuesta.ok) {
    let mensaje = 'Algo salió mal. Intenta otra vez.';
    try {
      const { detail } = await respuesta.json();
      // FastAPI entrega un texto en los errores propios y una lista en los de validación.
      if (typeof detail === 'string') mensaje = detail;
      else if (Array.isArray(detail)) mensaje = 'Revisa los datos ingresados.';
    } catch {}
    throw new ErrorApi(respuesta.status, mensaje);
  }
  return (await respuesta.json()) as T;
}

export type Salud = { estado: string; version: string; base_datos: string };

export const api = {
  salud: () => pedir<Salud>('GET', '/salud'),

  registrarApoderado: (email: string, contrasena: string) =>
    pedir<Esquemas['ApoderadoCreado']>('POST', '/auth/apoderado/registro', {
      cuerpo: { email, contrasena },
    }),
  ingresarApoderado: (email: string, contrasena: string) =>
    pedir<Token>('POST', '/auth/apoderado/login', { cuerpo: { email, contrasena } }),
  ingresarEstudiante: (estudianteId: string, pin: string) =>
    pedir<Token>('POST', '/auth/estudiante/login', { cuerpo: { estudianteId, pin } }),

  estudianteDelApoderado: (token: string) =>
    pedir<PerfilEstudiante>('GET', '/apoderado/estudiante', { token }),
  crearEstudiante: (token: string, datos: Esquemas['EstudianteNuevo']) =>
    pedir<PerfilEstudiante>('POST', '/apoderado/estudiante', { token, cuerpo: datos }),

  perfilEstudiante: (token: string) =>
    pedir<PerfilEstudiante>('GET', '/estudiante/perfil', { token }),
  unidades: (token: string) => pedir<UnidadEstudiante[]>('GET', '/estudiante/unidades', { token }),
};

// Compatibilidad con la pantalla de diagnóstico (tarea 36).
export const obtenerSalud = api.salud;
