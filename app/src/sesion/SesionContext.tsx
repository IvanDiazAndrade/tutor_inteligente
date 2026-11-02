import * as SecureStore from 'expo-secure-store';
import { createContext, type ReactNode, useCallback, useContext, useEffect, useState } from 'react';

// Sesión en el dispositivo (RNF-S1): los tokens se guardan cifrados con expo-secure-store.
// - dispositivo: vincula el teléfono a la cuenta del apoderado (RF-A2, RF-A3). Se obtiene al
//   iniciar sesión con correo y contraseña y solo sirve para entrar como el estudiante (sin
//   PIN) o para abrir el panel con el PIN del apoderado.
// - sesion: la sesión activa, del estudiante o del panel. Cerrarla no desvincula el teléfono.
// También se recuerdan los perfiles de estudiante de la cuenta (solo id, alias y curso) para
// que el niño elija el suyo sin escribir nada.

export type Rol = 'apoderado' | 'estudiante';
export type PerfilRecordado = { id: string; alias: string; curso: number };

type Sesion = { token: string; rol: Rol };

type ValorSesion = {
  cargando: boolean;
  dispositivo: string | null;
  sesion: Sesion | null;
  perfiles: PerfilRecordado[];
  vincular: (tokenDispositivo: string) => Promise<void>;
  iniciar: (token: string, rol: Rol) => Promise<void>;
  cerrar: () => Promise<void>;
  desvincular: () => Promise<void>;
  recordarPerfil: (perfil: PerfilRecordado) => Promise<void>;
};

const CLAVE_DISPOSITIVO = 'tutor.dispositivo';
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
  const [dispositivo, setDispositivo] = useState<string | null>(null);
  const [sesion, setSesion] = useState<Sesion | null>(null);
  const [perfiles, setPerfiles] = useState<PerfilRecordado[]>([]);

  useEffect(() => {
    Promise.all([
      leerJson<Sesion | null>(CLAVE_SESION, null),
      leerJson<PerfilRecordado[]>(CLAVE_PERFILES, []),
      SecureStore.getItemAsync(CLAVE_DISPOSITIVO).catch(() => null),
    ]).then(([s, p, d]) => {
      setDispositivo(d);
      setSesion(s);
      setPerfiles(p);
      setCargando(false);
    });
  }, []);

  // Vincular el teléfono a una cuenta olvida los perfiles de otras cuentas: el token del
  // dispositivo solo entra al estudiante de su cuenta, y un perfil ajeno en la lista haría
  // entrar a otro niño con ese nombre.
  const vincular = useCallback(async (tokenDispositivo: string) => {
    await SecureStore.setItemAsync(CLAVE_DISPOSITIVO, tokenDispositivo);
    await SecureStore.deleteItemAsync(CLAVE_PERFILES);
    setDispositivo(tokenDispositivo);
    setPerfiles([]);
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

  // Cerrar sesión en este dispositivo: quita el vínculo con la cuenta y los perfiles
  // recordados, y la app vuelve al inicio de sesión.
  const desvincular = useCallback(async () => {
    await Promise.all(
      [CLAVE_SESION, CLAVE_DISPOSITIVO, CLAVE_PERFILES].map((c) => SecureStore.deleteItemAsync(c)),
    );
    setSesion(null);
    setDispositivo(null);
    setPerfiles([]);
  }, []);

  // Una cuenta tiene un estudiante (RF-A1), así que la lista es solo el perfil de la cuenta
  // vinculada. Se mantiene como lista para cuando se admita más de un estudiante por cuenta.
  const recordarPerfil = useCallback(async (perfil: PerfilRecordado) => {
    const lista = [perfil];
    await SecureStore.setItemAsync(CLAVE_PERFILES, JSON.stringify(lista));
    setPerfiles(lista);
  }, []);

  return (
    <ContextoSesion.Provider
      value={{
        cargando,
        dispositivo,
        sesion,
        perfiles,
        vincular,
        iniciar,
        cerrar,
        desvincular,
        recordarPerfil,
      }}
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
