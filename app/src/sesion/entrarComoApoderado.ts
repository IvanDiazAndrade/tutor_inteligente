import { router } from 'expo-router';

import { api, ErrorApi } from '@/api/cliente';
import type { PerfilRecordado, Rol } from '@/sesion/SesionContext';

// Después de ingresar: si la cuenta ya tiene estudiante, se recuerda su perfil en este
// dispositivo (para que el niño lo elija en el acceso) y se abre el panel; si no, se pide
// crearlo (CU-9).
export async function entrarComoApoderado(
  token: string,
  iniciar: (token: string, rol: Rol) => Promise<void>,
  recordarPerfil: (perfil: PerfilRecordado) => Promise<void>,
) {
  await iniciar(token, 'apoderado');
  try {
    const { id, alias, curso } = await api.estudianteDelApoderado(token);
    await recordarPerfil({ id, alias, curso });
    router.replace('/apoderado');
  } catch (e) {
    if (e instanceof ErrorApi && e.estado === 404) router.replace('/apoderado/perfil');
    else throw e;
  }
}
