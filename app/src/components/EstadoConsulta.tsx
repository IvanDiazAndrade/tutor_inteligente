import { Pressable, Text } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { Octavio } from '@/components/Octavio';

// Carga o error, con Octavio y un botón para reintentar.
export function EstadoConsulta({
  texto,
  esTablet,
  onReintentar,
}: {
  texto: string;
  esTablet: boolean;
  onReintentar?: () => void;
}) {
  return (
    <SafeAreaView className="flex-1 items-center justify-center gap-4 bg-panel p-6">
      <Octavio tamano={esTablet ? 120 : 88} conVarita />
      <Text
        className={`text-center font-nunito-bold text-apagado-oscuro ${esTablet ? 'text-lg' : 'text-base'}`}
      >
        {texto}
      </Text>
      {onReintentar && (
        <Pressable
          onPress={onReintentar}
          className="rounded-full bg-primario px-6 py-3 active:bg-primario-oscuro"
        >
          <Text className="font-nunito-black text-white">Reintentar</Text>
        </Pressable>
      )}
    </SafeAreaView>
  );
}
