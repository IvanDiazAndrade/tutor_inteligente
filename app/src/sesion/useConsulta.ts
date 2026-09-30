import { useQuery } from '@tanstack/react-query';
import { useEffect } from 'react';

import { ErrorApi } from '@/api/cliente';
import { useSesion } from '@/sesion/SesionContext';

// Consulta autenticada: pasa el token de la sesión y, si el servidor responde 401 (token
// vencido o inválido), cierra la sesión para que la app vuelva a la pantalla de acceso.
export function useConsulta<T>(clave: string, consulta: (token: string) => Promise<T>) {
  const { sesion, cerrar } = useSesion();
  const token = sesion?.token ?? null;
  const resultado = useQuery({
    queryKey: [clave, token],
    queryFn: () => consulta(token!),
    enabled: token !== null,
    retry: (intentos, error) =>
      !(error instanceof ErrorApi && error.estado >= 400 && error.estado < 500) && intentos < 2,
  });

  const error = resultado.error;
  useEffect(() => {
    if (error instanceof ErrorApi && error.estado === 401) cerrar();
  }, [error, cerrar]);

  return resultado;
}
