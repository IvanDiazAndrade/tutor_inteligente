import { Redirect } from 'expo-router';
import type { ReactNode } from 'react';

import { type Rol, useSesion } from '@/sesion/SesionContext';

// Muestra la pantalla solo con una sesión del rol indicado; si no, vuelve al acceso (RF-A2).
export function Protegida({ rol, children }: { rol: Rol; children: ReactNode }) {
  const { cargando, sesion } = useSesion();
  if (cargando) return null;
  if (sesion?.rol !== rol) {
    return <Redirect href={rol === 'apoderado' ? '/apoderado/ingreso' : '/'} />;
  }
  return <>{children}</>;
}
