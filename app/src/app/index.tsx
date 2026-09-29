import { router } from 'expo-router';
import { useEffect, useRef, useState } from 'react';
import { Pressable, ScrollView, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { Encabezado } from '@/components/Encabezado';
import { Octavio } from '@/components/Octavio';
import { TarjetaPerfil } from '@/components/TarjetaPerfil';
import { LARGO_PIN, TecladoPin } from '@/components/TecladoPin';
import { PERFILES_EJEMPLO, PIN_EJEMPLO } from '@/datos/ejemplo';
import { useDistribucion } from '@/hooks/useDistribucion';

// Pantalla de acceso (CU-1, RF-A2, RF-A3; mockup "Acceso"). El estudiante elige su perfil
// y escribe su PIN; el apoderado entra por el enlace inferior con correo y contraseña.
export default function Acceso() {
  const { dosColumnas, esTablet } = useDistribucion();
  const compacta = dosColumnas && !esTablet;
  const [perfilId, setPerfilId] = useState(PERFILES_EJEMPLO[0].id);
  const [pin, setPin] = useState('');
  const [error, setError] = useState(false);
  const perfil = PERFILES_EJEMPLO.find((p) => p.id === perfilId) ?? PERFILES_EJEMPLO[0];

  const temporizador = useRef<ReturnType<typeof setTimeout>>(undefined);
  useEffect(() => () => clearTimeout(temporizador.current), []);

  // Se revisa el PIN al escribir el último dígito. Con error, los puntos quedan en naranjo
  // un momento y luego se limpian para reintentar.
  const cambiarPin = (nuevo: string) => {
    if (error) return;
    setPin(nuevo);
    if (nuevo.length < LARGO_PIN) return;
    if (nuevo === PIN_EJEMPLO) {
      setPin('');
      router.replace('/estudiante');
      return;
    }
    setError(true);
    temporizador.current = setTimeout(() => {
      setPin('');
      setError(false);
    }, 900);
  };

  const elegirPerfil = (id: string) => {
    clearTimeout(temporizador.current);
    setPerfilId(id);
    setPin('');
    setError(false);
  };

  const perfiles = (
    <View className="gap-2.5">
      <Text className={`font-nunito-black text-tinta ${esTablet ? 'text-2xl' : 'text-lg'}`}>
        ¿Quién va a practicar?
      </Text>
      {PERFILES_EJEMPLO.map((p) => (
        <TarjetaPerfil
          key={p.id}
          alias={p.alias}
          curso={p.curso}
          seleccionado={p.id === perfilId}
          onPress={() => elegirPerfil(p.id)}
          compacta={compacta}
          grande={esTablet}
        />
      ))}
    </View>
  );

  const bloquePin = (
    <View className="items-center gap-2.5 rounded-[18px] bg-white px-4 py-3">
      <View className="flex-row items-center gap-2">
        <Octavio tamano={esTablet ? 56 : 40} guino />
        <Text
          className={`shrink font-nunito-black text-tinta ${esTablet ? 'text-xl' : 'text-base'}`}
        >
          {error ? '¡Uy! Ese PIN no es. Prueba otra vez' : `Hola ${perfil.alias}, escribe tu PIN`}
        </Text>
      </View>
      <TecladoPin pin={pin} onCambio={cambiarPin} error={error} grande={esTablet} />
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
        ver progreso →
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
              {perfiles}
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
            {perfiles}
            {bloquePin}
            {enlaceApoderado}
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}
