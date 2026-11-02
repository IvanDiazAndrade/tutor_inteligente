import { router } from 'expo-router';

import { api, ErrorApi, type Esquemas } from '@/api/cliente';
import type { PerfilRecordado, Rol } from '@/sesion/SesionContext';

type Acciones = {
  vincular: (tokenDispositivo: string) => Promise<void>;
  iniciar: (token: string, rol: Rol) => Promise<void>;
  recordarPerfil: (perfil: PerfilRecordado) => Promise<void>;
};

// Después de iniciar sesión con correo y contraseña: el teléfono queda vinculado a la cuenta
// (RF-A2, RF-A3) y se abre el panel. Si la cuenta ya tiene estudiante, se recuerda su perfil
// para que el niño lo elija en el acceso; si no, se pide crearlo (CU-9).
export async function entrarComoApoderado(
  ingreso: Esquemas['IngresoConDispositivo'],
  { vincular, iniciar, recordarPerfil }: Acciones,
) {
  await vincular(ingreso.tokenDispositivo);
  await iniciar(ingreso.token, 'apoderado');
  try {
    const { id, alias, curso } = await api.estudianteDelApoderado(ingreso.token);
    await recordarPerfil({ id, alias, curso });
    router.replace('/apoderado');
  } catch (e) {
    if (e instanceof ErrorApi && e.estado === 404) router.replace('/apoderado/perfil');
    else throw e;
  }
}
