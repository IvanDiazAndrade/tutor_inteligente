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

// Pantalla de acceso (CU-1, RF-A2, RF-A3; mockup "Acceso"). Sin un dispositivo vinculado abre
// directamente el inicio de sesión. Con el dispositivo vinculado, el estudiante toca su perfil
// y entra sin PIN; el apoderado entra al panel con su PIN de 4 números, que valida el servidor.
export default function Acceso() {
  const { dosColumnas, esTablet } = useDistribucion();
  const compacta = dosColumnas && !esTablet;
  const { cargando, dispositivo, sesion, perfiles, iniciar, desvincular } = useSesion();
  const [pidiendoPin, setPidiendoPin] = useState(false);
  const [pin, setPin] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [entrando, setEntrando] = useState<string | null>(null); // id del perfil o 'panel'

  const temporizador = useRef<ReturnType<typeof setTimeout>>(undefined);
  useEffect(() => () => clearTimeout(temporizador.current), []);

  if (cargando) return null;
  if (sesion?.rol === 'estudiante') return <Redirect href="/estudiante" />;
  if (sesion?.rol === 'apoderado') return <Redirect href="/apoderado" />;
  if (!dispositivo) return <Redirect href="/apoderado/ingreso" />;

  // El token del dispositivo vence a los 30 días o pudo revocarse: se vuelve a iniciar sesión.
  const manejarError = (e: unknown, mostrar: (mensaje: string) => void) => {
    if (e instanceof ErrorApi && (e.estado === 401 || e.estado === 403)) desvincular();
    else mostrar(e instanceof ErrorApi ? e.message : 'Algo salió mal. Intenta otra vez.');
  };

  const entrarComoEstudiante = async (perfilId: string) => {
    if (entrando) return;
    setEntrando(perfilId);
    setError(null);
    try {
      const { token } = await api.entrarComoEstudiante(dispositivo);
      await iniciar(token, 'estudiante');
      router.replace('/estudiante');
    } catch (e) {
      manejarError(e, setError);
    } finally {
      setEntrando(null);
    }
  };

  const mostrarErrorPin = (mensaje: string) => {
    setError(mensaje);
    // Los puntos quedan en naranjo un momento y luego se limpian para reintentar.
    temporizador.current = setTimeout(() => {
      setPin('');
      setError(null);
    }, 1400);
  };

  // Se envía el PIN al escribir el último dígito.
  const cambiarPin = async (nuevo: string) => {
    if (error || entrando) return;
    setPin(nuevo);
    if (nuevo.length < LARGO_PIN) return;
    setEntrando('panel');
    try {
      const { token } = await api.abrirPanel(dispositivo, nuevo);
      await iniciar(token, 'apoderado');
      router.replace(perfiles.length === 0 ? '/apoderado/perfil' : '/apoderado');
    } catch (e) {
      if (e instanceof ErrorApi && e.estado === 401)
        mostrarErrorPin('Ese PIN no es. Prueba otra vez');
      else if (e instanceof ErrorApi && e.estado === 423)
        mostrarErrorPin('Espera un momento e intenta otra vez');
      else manejarError(e, mostrarErrorPin);
    } finally {
      setEntrando(null);
    }
  };

  const alternarPin = (pedir: boolean) => {
    clearTimeout(temporizador.current);
    setPidiendoPin(pedir);
    setPin('');
    setError(null);
  };

  const textoTitulo = `font-nunito-black text-tinta ${esTablet ? 'text-2xl' : 'text-lg'}`;
  const textoAyuda = `font-nunito-bold text-apagado-oscuro ${esTablet ? 'text-lg' : 'text-sm'}`;

  const listaPerfiles = (
    <View className="gap-2.5">
      <Text className={textoTitulo}>¿Quién va a practicar?</Text>
      {perfiles.length === 0 ? (
        <Text className={textoAyuda}>
          Todavía no hay un perfil de estudiante. Entra como apoderado para crearlo.
        </Text>
      ) : (
        perfiles.map((p) => (
          <TarjetaPerfil
            key={p.id}
            alias={p.alias}
            curso={p.curso}
            seleccionado={entrando === p.id}
            onPress={() => entrarComoEstudiante(p.id)}
            compacta={compacta}
            grande={esTablet}
          />
        ))
      )}
      {error && !pidiendoPin && (
        <Text className="font-nunito-bold text-sm text-amber-700">{error}</Text>
      )}
    </View>
  );

  const bloquePin = (
    <View className="items-center gap-2.5 rounded-[18px] bg-white px-4 py-3">
      <View className="flex-row items-center gap-2">
        <Octavio tamano={esTablet ? 56 : 40} guino />
        <Text
          className={`shrink font-nunito-black text-tinta ${esTablet ? 'text-xl' : 'text-base'}`}
        >
          {error ?? (entrando === 'panel' ? 'Revisando…' : 'Escribe tu PIN de apoderado')}
        </Text>
      </View>
      <TecladoPin pin={pin} onCambio={cambiarPin} error={error !== null} grande={esTablet} />
      <Pressable accessibilityRole="button" onPress={() => alternarPin(false)} className="py-1">
        <Text
          className={`font-nunito-extrabold text-apagado-oscuro ${esTablet ? 'text-lg' : 'text-sm'}`}
        >
          ← Volver a los perfiles
        </Text>
      </Pressable>
    </View>
  );

  // En dos columnas, a la derecha va el PIN del apoderado o una bienvenida de Octavio.
  const bienvenida = (
    <View className="items-center gap-3 rounded-[18px] bg-white px-4 py-6">
      <Octavio tamano={esTablet ? 96 : 64} conVarita />
      <Text className={`text-center ${textoTitulo}`}>
        {perfiles.length === 0
          ? '¡Hola! Primero hay que crear un perfil'
          : 'Toca tu perfil para empezar'}
      </Text>
    </View>
  );

  const enlaceApoderado = (
    <Pressable
      accessibilityRole="link"
      onPress={() => alternarPin(true)}
      className={`flex-row flex-wrap items-center justify-between gap-x-3 gap-y-1 rounded-2xl border-[1.5px] bg-white px-4 active:bg-panel ${
        pidiendoPin ? 'border-primario-claro' : 'border-borde'
      } ${esTablet ? 'py-5' : 'py-3'}`}
    >
      <Text
        className={`font-nunito-extrabold text-apagado-oscuro ${esTablet ? 'text-lg' : 'text-sm'}`}
      >
        👤 Soy el apoderado
      </Text>
      <Text className={`font-nunito-black text-primario ${esTablet ? 'text-lg' : 'text-sm'}`}>
        {perfiles.length === 0 ? 'crear perfil →' : 'ver progreso →'}
      </Text>
    </Pressable>
  );

  return (
    <SafeAreaView className="flex-1 bg-fondo">
      <ScrollView contentContainerClassName="grow justify-center p-3">
        {dosColumnas ? (
          <View className="w-full max-w-[1100px] flex-row gap-4 self-center">
            <View className="flex-1 justify-between gap-4 rounded-[22px] bg-panel p-4">
              <Encabezado grande={esTablet} />
              {listaPerfiles}
              {enlaceApoderado}
            </View>
            <View className="flex-1 justify-center rounded-[22px] bg-panel p-4">
              {pidiendoPin ? bloquePin : bienvenida}
            </View>
          </View>
        ) : (
          <View
            className={`w-full gap-3 self-center rounded-[22px] bg-panel ${
              esTablet ? 'max-w-[600px] gap-6 p-8' : 'max-w-[480px] p-4'
            }`}
          >
            <Encabezado grande={esTablet} />
            {pidiendoPin ? bloquePin : listaPerfiles}
            {!pidiendoPin && enlaceApoderado}
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}
