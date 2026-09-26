import Constants from 'expo-constants';
import { Platform, Text, useWindowDimensions, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

// Pantalla provisoria de la tarea 36: confirma que el entorno compila y corre en el dispositivo.
// Se reemplaza por la pantalla de acceso en la Fase IV (tarea 50).
export default function Inicio() {
  const { width, height } = useWindowDimensions();
  const orientacion = width > height ? 'horizontal' : 'vertical';

  return (
    <SafeAreaView className="flex-1 bg-white">
      <View className="flex-1 items-center justify-center gap-3 px-6">
        <Text className="text-3xl font-bold text-violet-700">Tutor Inteligente</Text>
        <Text className="text-base text-slate-600">Entorno de desarrollo listo</Text>
        <Text className="text-sm text-slate-500">
          Expo SDK {Constants.expoConfig?.sdkVersion} · Android API {Platform.Version} · {orientacion}
        </Text>
      </View>
    </SafeAreaView>
  );
}
