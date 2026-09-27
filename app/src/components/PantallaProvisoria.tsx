import { router } from 'expo-router';
import { Pressable, Text } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { Octavio } from '@/components/Octavio';

type Props = { titulo: string; descripcion: string; conVolver?: boolean };

// Marcador para pantallas del prototipo que todavía no se construyen.
export function PantallaProvisoria({ titulo, descripcion, conVolver = false }: Props) {
  return (
    <SafeAreaView className="flex-1 items-center justify-center gap-4 bg-panel p-6">
      <Octavio tamano={96} conVarita />
      <Text className="text-center font-nunito-black text-2xl text-tinta">{titulo}</Text>
      <Text className="text-center font-nunito-bold text-base text-apagado-oscuro">
        {descripcion}
      </Text>
      {conVolver && (
        <Pressable
          onPress={() => router.back()}
          className="mt-2 rounded-full bg-primario px-6 py-3 active:bg-primario-oscuro"
        >
          <Text className="font-nunito-black text-white">Volver</Text>
        </Pressable>
      )}
    </SafeAreaView>
  );
}
