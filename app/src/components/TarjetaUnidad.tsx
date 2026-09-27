import { Pressable, Text, View } from 'react-native';

import { Estrellas } from '@/components/Estrellas';
import { Etiqueta, type TipoEtiqueta } from '@/components/Etiqueta';

type Props = {
  nombre: string;
  estrellas: number;
  etiqueta?: TipoEtiqueta;
  onPress: () => void;
  grande?: boolean;
};

// Fila del mapa de unidades de la home (RF-E5, RF-G2). Las unidades para repasar llevan borde.
export function TarjetaUnidad({ nombre, estrellas, etiqueta, onPress, grande = false }: Props) {
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityLabel={`${nombre}, ${estrellas} de 3 estrellas`}
      onPress={onPress}
      className={`flex-row items-center gap-2.5 rounded-[20px] bg-white px-4 active:bg-panel ${
        grande ? 'py-5' : 'py-3'
      } ${etiqueta === 'repasar' ? 'border-2 border-lila-suave' : 'border-2 border-white'}`}
    >
      <View className="flex-1 gap-0.5">
        <Text
          className={`font-nunito-extrabold text-tinta-media ${grande ? 'text-xl' : 'text-[15px]'}`}
        >
          {nombre}
        </Text>
        <Estrellas cantidad={estrellas} grande={grande} />
      </View>
      {etiqueta && <Etiqueta tipo={etiqueta} grande={grande} />}
    </Pressable>
  );
}
