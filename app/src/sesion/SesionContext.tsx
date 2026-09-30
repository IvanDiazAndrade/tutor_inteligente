import * as SecureStore from 'expo-secure-store';
import { createContext, type ReactNode, useCallback, useContext, useEffect, useState } from 'react';

// Sesión en el dispositivo (RNF-S1): el token se guarda cifrado con expo-secure-store.
// También se recuerdan los perfiles de estudiante que entraron en este teléfono (solo id,
// alias y curso) para que el niño elija su perfil sin escribir un correo (RF-A3).

export type Rol = 'apoderado' | 'estudiante';
export type PerfilRecordado = { id: string; alias: string; curso: number };

type Sesion = { token: string; rol: Rol };

type ValorSesion = {
  cargando: boolean;
  sesion: Sesion | null;
  perfiles: PerfilRecordado[];
  iniciar: (token: string, rol: Rol) => Promise<void>;
  cerrar: () => Promise<void>;
  recordarPerfil: (perfil: PerfilRecordado) => Promise<void>;
};

const CLAVE_SESION = 'tutor.sesion';
const CLAVE_PERFILES = 'tutor.perfiles';

const leerJson = async <T,>(clave: string, porDefecto: T): Promise<T> => {
  try {
    const texto = await SecureStore.getItemAsync(clave);
    return texto ? (JSON.parse(texto) as T) : porDefecto;
  } catch {
    return porDefecto;
  }
};

const ContextoSesion = createContext<ValorSesion | null>(null);

export function ProveedorSesion({ children }: { children: ReactNode }) {
  const [cargando, setCargando] = useState(true);
  const [sesion, setSesion] = useState<Sesion | null>(null);
  const [perfiles, setPerfiles] = useState<PerfilRecordado[]>([]);

  useEffect(() => {
    Promise.all([
      leerJson<Sesion | null>(CLAVE_SESION, null),
      leerJson<PerfilRecordado[]>(CLAVE_PERFILES, []),
    ]).then(([s, p]) => {
      setSesion(s);
      setPerfiles(p);
      setCargando(false);
    });
  }, []);

  const iniciar = useCallback(async (token: string, rol: Rol) => {
    const nueva = { token, rol };
    await SecureStore.setItemAsync(CLAVE_SESION, JSON.stringify(nueva));
    setSesion(nueva);
  }, []);

  const cerrar = useCallback(async () => {
    await SecureStore.deleteItemAsync(CLAVE_SESION);
    setSesion(null);
  }, []);

  const recordarPerfil = useCallback(
    async (perfil: PerfilRecordado) => {
      const lista = [perfil, ...perfiles.filter((p) => p.id !== perfil.id)];
      await SecureStore.setItemAsync(CLAVE_PERFILES, JSON.stringify(lista));
      setPerfiles(lista);
    },
    [perfiles],
  );

  return (
    <ContextoSesion.Provider
      value={{ cargando, sesion, perfiles, iniciar, cerrar, recordarPerfil }}
    >
      {children}
    </ContextoSesion.Provider>
  );
}

export function useSesion(): ValorSesion {
  const valor = useContext(ContextoSesion);
  if (!valor) throw new Error('useSesion debe usarse dentro de ProveedorSesion');
  return valor;
}
