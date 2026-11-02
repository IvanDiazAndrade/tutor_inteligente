import { Redirect } from 'expo-router';
import type { ReactNode } from 'react';

import { type Rol, useSesion } from '@/sesion/SesionContext';

// Muestra la pantalla solo con una sesión del rol indicado; si no, vuelve a la pantalla de
// acceso, que pide el PIN del panel o, sin dispositivo vinculado, el inicio de sesión (RF-A2).
export function Protegida({ rol, children }: { rol: Rol; children: ReactNode }) {
  const { cargando, sesion } = useSesion();
  if (cargando) return null;
  if (sesion?.rol !== rol) return <Redirect href="/" />;
  return <>{children}</>;
}
