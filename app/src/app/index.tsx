import { Redirect, router } from 'expo-router';
import { useEffect, useRef, useState } from 'react';
import { Pressable, ScrollView, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { api, ErrorApi } from '@/api/cliente';
import { Encabezado } from '@/components/Encabezado';
import { Octavio } from '@/components/Octavio';
import { TarjetaPerfil } from '@/components/TarjetaPerfil';
import { LARGO_PIN, TecladoPin } from '@/components/TecladoPin';
import { useDistribucion } from '@/hooks/useDistribucion';
import { useSesion } from '@/sesion/SesionContext';

// Pantalla de acceso (CU-1, RF-A2, RF-A3; mockup "Acceso"). El estudiante elige uno de los
// perfiles recordados en este teléfono y escribe su PIN, que valida el servidor. El apoderado
// entra por el enlace inferior con correo y contraseña.
export default function Acceso() {
  const { dosColumnas, esTablet } = useDistribucion();
  const compacta = dosColumnas && !esTablet;
  const { cargando, sesion, perfiles, iniciar } = useSesion();
  const [perfilId, setPerfilId] = useState<string | null>(null);
  const [pin, setPin] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [verificando, setVerificando] = useState(false);
  const perfil = perfiles.find((p) => p.id === perfilId) ?? perfiles[0];

  const temporizador = useRef<ReturnType<typeof setTimeout>>(undefined);
  useEffect(() => () => clearTimeout(temporizador.current), []);

  if (cargando) return null;
  if (sesion?.rol === 'estudiante') return <Redirect href="/estudiante" />;
  if (sesion?.rol === 'apoderado') return <Redirect href="/apoderado" />;

  const mostrarError = (mensaje: string) => {
    setError(mensaje);
    // Los puntos quedan en naranjo un momento y luego se limpian para reintentar.
    temporizador.current = setTimeout(() => {
      setPin('');
      setError(null);
    }, 1400);
  };

  // Se envía el PIN al escribir el último dígito.
  const cambiarPin = async (nuevo: string) => {
    if (error || verificando || !perfil) return;
    setPin(nuevo);
    if (nuevo.length < LARGO_PIN) return;
    setVerificando(true);
    try {
      const { token } = await api.ingresarEstudiante(perfil.id, nuevo);
      await iniciar(token, 'estudiante');
      router.replace('/estudiante');
    } catch (e) {
      if (e instanceof ErrorApi && e.estado === 401)
        mostrarError('¡Uy! Ese PIN no es. Prueba otra vez');
      else if (e instanceof ErrorApi && e.estado === 423)
        mostrarError('Espera un momento e intenta otra vez');
      else mostrarError(e instanceof ErrorApi ? e.message : 'Algo salió mal. Intenta otra vez.');
    } finally {
      setVerificando(false);
    }
  };

  const elegirPerfil = (id: string) => {
    clearTimeout(temporizador.current);
    setPerfilId(id);
    setPin('');
    setError(null);
  };

  const listaPerfiles = (
    <View className="gap-2.5">
      <Text className={`font-nunito-black text-tinta ${esTablet ? 'text-2xl' : 'text-lg'}`}>
        ¿Quién va a practicar?
      </Text>
      {perfiles.length === 0 ? (
        <Text
          className={`font-nunito-bold text-apagado-oscuro ${esTablet ? 'text-lg' : 'text-sm'}`}
        >
          Todavía no hay perfiles en este dispositivo. El apoderado entra primero y crea el perfil
          del estudiante.
        </Text>
      ) : (
        perfiles.map((p) => (
          <TarjetaPerfil
            key={p.id}
            alias={p.alias}
            curso={p.curso}
            seleccionado={p.id === perfil?.id}
            onPress={() => elegirPerfil(p.id)}
            compacta={compacta}
            grande={esTablet}
          />
        ))
      )}
    </View>
  );

  const bloquePin = perfil && (
    <View className="items-center gap-2.5 rounded-[18px] bg-white px-4 py-3">
      <View className="flex-row items-center gap-2">
        <Octavio tamano={esTablet ? 56 : 40} guino />
        <Text
          className={`shrink font-nunito-black text-tinta ${esTablet ? 'text-xl' : 'text-base'}`}
        >
          {error ?? (verificando ? 'Revisando…' : `Hola ${perfil.alias}, escribe tu PIN`)}
        </Text>
      </View>
      <TecladoPin pin={pin} onCambio={cambiarPin} error={error !== null} grande={esTablet} />
    </View>
  );

  const enlaceApoderado = (
    <Pressable
      accessibilityRole="link"
      onPress={() => router.push('/apoderado/ingreso')}
      className={`flex-row flex-wrap items-center justify-between gap-x-3 gap-y-1 rounded-2xl border-[1.5px] border-borde bg-white px-4 active:bg-panel ${
        esTablet ? 'py-5' : 'py-3'
      }`}
    >
      <Text
        className={`font-nunito-extrabold text-apagado-oscuro ${esTablet ? 'text-lg' : 'text-sm'}`}
      >
        👤 Soy el apoderado
      </Text>
      <Text className={`font-nunito-black text-primario ${esTablet ? 'text-lg' : 'text-sm'}`}>
        {perfiles.length === 0 ? 'entrar →' : 'ver progreso →'}
      </Text>
    </Pressable>
  );

  return (
    <SafeAreaView className="flex-1 bg-fondo">
      <ScrollView contentContainerClassName="grow justify-center p-3">
        {dosColumnas && bloquePin ? (
          <View className="w-full max-w-[1100px] flex-row gap-4 self-center">
            <View className="flex-1 justify-between gap-4 rounded-[22px] bg-panel p-4">
              <Encabezado grande={esTablet} />
              {listaPerfiles}
              {enlaceApoderado}
            </View>
            <View className="flex-1 justify-center rounded-[22px] bg-panel p-4">{bloquePin}</View>
          </View>
        ) : (
          <View
            className={`w-full gap-3 self-center rounded-[22px] bg-panel ${
              esTablet ? 'max-w-[600px] gap-6 p-8' : 'max-w-[480px] p-4'
            }`}
          >
            <Encabezado grande={esTablet} />
            {listaPerfiles}
            {bloquePin}
            {enlaceApoderado}
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}
