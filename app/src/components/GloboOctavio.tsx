import type { ReactNode } from 'react';
import { Text, View } from 'react-native';

import { Octavio } from '@/components/Octavio';

type Props = { mensaje: string; grande?: boolean; children?: ReactNode };

// Zona del tutor: Octavio con su globo de diálogo (mockup "Ejercicio Estudiante").
// Los botones propios del momento (p. ej. "Siguiente →") van como children dentro del globo.
export function GloboOctavio({ mensaje, grande = false, children }: Props) {
  return (
    <View className="flex-row items-end gap-2">
      <Octavio tamano={grande ? 160 : 96} tutor />
      <View
        className={`mb-6 flex-1 gap-3 rounded-[18px] border-2 border-globo bg-white ${
          grande ? 'px-5 py-4' : 'px-3.5 py-3'
        }`}
      >
        <Text
          accessibilityLiveRegion="polite"
          className={`font-nunito-bold text-tinta-tecla ${grande ? 'text-xl leading-7' : 'text-sm leading-5'}`}
        >
          {mensaje}
        </Text>
        {children}
      </View>
    </View>
  );
}
