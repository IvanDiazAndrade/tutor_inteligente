import { router } from 'expo-router';

import { api, type Esquemas } from '@/api/cliente';
import type { PerfilRecordado, Rol } from '@/sesion/SesionContext';

type Acciones = {
  vincular: (tokenDispositivo: string) => Promise<void>;
  iniciar: (token: string, rol: Rol) => Promise<void>;
  recordarPerfiles: (lista: PerfilRecordado[]) => Promise<void>;
};

// Después de iniciar sesión con correo y contraseña el teléfono queda vinculado a la cuenta
// (RF-A2, RF-A3) y se vuelve a la pantalla de acceso, donde se elige entre entrar como uno de
// los estudiantes o abrir el panel con el PIN. El token del panel solo se usa aquí para leer los
// perfiles de la cuenta y recordarlos; no se abre el panel. Si la cuenta todavía no tiene
// estudiantes (recién registrada), primero se pide crear uno (CU-9).
export async function entrarComoApoderado(
  ingreso: Esquemas['IngresoConDispositivo'],
  { vincular, iniciar, recordarPerfiles }: Acciones,
) {
  await vincular(ingreso.tokenDispositivo);
  const perfiles = await api.estudiantesDelApoderado(ingreso.token);
  if (perfiles.length > 0) {
    await recordarPerfiles(perfiles);
    router.replace('/');
    return;
  }
  await iniciar(ingreso.token, 'apoderado');
  router.replace('/apoderado/perfil');
}
