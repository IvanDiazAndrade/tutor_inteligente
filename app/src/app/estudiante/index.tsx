import { router, useLocalSearchParams } from 'expo-router';
import { Pressable, Text } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { Octavio } from '@/components/Octavio';

// Marcador de la home del estudiante: se construye en el siguiente paso de la tarea 42.
export default function HomeEstudiante() {
  const { alias } = useLocalSearchParams<{ alias?: string }>();
  return (
    <SafeAreaView className="flex-1 items-center justify-center gap-4 bg-fondo p-6">
      <Octavio tamano={96} conVarita />
      <Text className="font-nunito-black text-2xl text-tinta">¡Hola, {alias ?? 'estudiante'}!</Text>
      <Text className="text-center font-nunito-bold text-base text-apagado-oscuro">
        Aquí irá el mapa de unidades (siguiente pantalla del prototipo).
      </Text>
      <Pressable
        onPress={() => router.back()}
        className="mt-2 rounded-full bg-primario px-6 py-3 active:bg-primario-oscuro"
      >
        <Text className="font-nunito-black text-white">Salir</Text>
      </Pressable>
    </SafeAreaView>
  );
}
