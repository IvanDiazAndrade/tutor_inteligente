import { Text, View } from 'react-native';

import { Octavio } from '@/components/Octavio';

// Marca de la app: Octavio con varita + nombre y lema.
export function Encabezado({ grande = false }: { grande?: boolean }) {
  return (
    <View className="flex-row items-center gap-3">
      <Octavio tamano={grande ? 88 : 56} conVarita />
      <View>
        <Text
          className={`font-nunito-black text-primario ${grande ? 'text-3xl' : 'text-xl leading-6'}`}
        >
          Tutor Octavio
        </Text>
        <Text className={`font-nunito-bold text-lila ${grande ? 'text-base' : 'text-xs'}`}>
          Matemáticas con magia
        </Text>
      </View>
    </View>
  );
}
