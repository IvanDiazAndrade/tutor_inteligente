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
        grande ? 'py-7' : 'py-5'
      } ${etiqueta === 'repasar' ? 'border-2 border-lila-suave' : 'border-2 border-white'}`}
    >
      <View className={`flex-1 ${grande ? 'gap-3' : 'gap-2'}`}>
        <Text
          className={`font-nunito-extrabold text-tinta-media ${grande ? 'text-2xl' : 'text-xl'}`}
        >
          {nombre}
        </Text>
        <View className="flex-row flex-wrap items-center justify-between gap-2">
          <Estrellas cantidad={estrellas} grande={grande} />
          {etiqueta && <Etiqueta tipo={etiqueta} grande={grande} />}
        </View>
      </View>
    </Pressable>
  );
}
