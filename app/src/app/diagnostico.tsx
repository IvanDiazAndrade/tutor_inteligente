import { useQuery } from '@tanstack/react-query';
import Constants from 'expo-constants';
import { Platform, Pressable, Text, useWindowDimensions, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { API_URL, obtenerSalud } from '@/api/cliente';

// Pantalla de diagnóstico (tarea 36): confirma que la app corre en el dispositivo y alcanza
// la API y la base de datos. Se abre con la ruta /diagnostico.
export default function Diagnostico() {
  const { width, height } = useWindowDimensions();
  const orientacion = width > height ? 'horizontal' : 'vertical';
  const salud = useQuery({ queryKey: ['salud'], queryFn: obtenerSalud, retry: false });

  let servidor = 'Conectando con el servidor…';
  let colorServidor = 'text-slate-500';
  if (salud.isSuccess) {
    servidor = `Servidor: conectado (v${salud.data.version}) · Base de datos: ${salud.data.base_datos}`;
    colorServidor = salud.data.base_datos === 'ok' ? 'text-green-700' : 'text-amber-700';
  } else if (salud.isError) {
    servidor = 'Servidor: sin conexión';
    colorServidor = 'text-red-700';
  }

  return (
    <SafeAreaView className="flex-1 bg-white">
      <View className="flex-1 items-center justify-center gap-3 px-6">
        <Text className="text-3xl font-bold text-violet-700">Tutor Inteligente</Text>
        <Text className="text-base text-slate-600">Entorno de desarrollo listo</Text>
        <Text className="text-sm text-slate-500">
          Expo SDK {Constants.expoConfig?.sdkVersion} · Android API {Platform.Version} · {orientacion}
        </Text>
        <Text className={`text-center text-sm font-semibold ${colorServidor}`}>{servidor}</Text>
        <Text className="text-xs text-slate-400">{API_URL}</Text>
        <Pressable
          onPress={() => salud.refetch()}
          className="mt-2 rounded-full bg-violet-600 px-5 py-2 active:bg-violet-800"
        >
          <Text className="font-semibold text-white">Reintentar</Text>
        </Pressable>
      </View>
    </SafeAreaView>
  );
}
