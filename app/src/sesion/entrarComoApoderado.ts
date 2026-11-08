import { router } from 'expo-router';

import { api, ErrorApi, type Esquemas } from '@/api/cliente';
import type { PerfilRecordado, Rol } from '@/sesion/SesionContext';

type Acciones = {
  vincular: (tokenDispositivo: string) => Promise<void>;
  iniciar: (token: string, rol: Rol) => Promise<void>;
  recordarPerfil: (perfil: PerfilRecordado) => Promise<void>;
};

// Después de iniciar sesión con correo y contraseña el teléfono queda vinculado a la cuenta
// (RF-A2, RF-A3) y se vuelve a la pantalla de acceso, donde se elige entre entrar como el
// estudiante o abrir el panel con el PIN. El token del panel solo se usa aquí para leer el
// perfil del estudiante y recordarlo; no se abre el panel. Si la cuenta todavía no tiene
// estudiante (recién registrada), primero se pide crearlo (CU-9).
export async function entrarComoApoderado(
  ingreso: Esquemas['IngresoConDispositivo'],
  { vincular, iniciar, recordarPerfil }: Acciones,
) {
  await vincular(ingreso.tokenDispositivo);
  try {
    const { id, alias, curso } = await api.estudianteDelApoderado(ingreso.token);
    await recordarPerfil({ id, alias, curso });
    router.replace('/');
  } catch (e) {
    if (!(e instanceof ErrorApi && e.estado === 404)) throw e;
    await iniciar(ingreso.token, 'apoderado');
    router.replace('/apoderado/perfil');
  }
}
