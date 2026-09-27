import { Pressable, Text, View } from 'react-native';

import { Etiqueta, type TipoEtiqueta } from '@/components/Etiqueta';

type Props = {
  nombre: string;
  etiqueta?: TipoEtiqueta;
  onPracticar: () => void;
  grande?: boolean;
  apilada?: boolean;
};

// Unidad sugerida destacada en la home (modelo_estudiante.md §5). Con poco ancho, el botón
// va debajo del nombre (apilada).
export function SugerenciaOctavio({
  nombre,
  etiqueta,
  onPracticar,
  grande = false,
  apilada = false,
}: Props) {
  return (
    <View className="mt-3 rounded-[20px] border-[2.5px] border-primario-claro bg-fondo px-4 pb-4 pt-5">
      <View className="absolute -top-3 left-3.5 rounded-full bg-primario px-3 py-1">
        <Text className={`font-nunito-black text-white ${grande ? 'text-sm' : 'text-xs'}`}>
          ✨ Octavio te sugiere
        </Text>
      </View>
      <View className={apilada ? 'gap-3' : 'flex-row items-center gap-3'}>
        <View className={apilada ? 'gap-1.5' : 'flex-1 gap-1.5'}>
          <Text className={`font-nunito-black text-tinta ${grande ? 'text-2xl' : 'text-[17px]'}`}>
            {nombre}
          </Text>
          {etiqueta && <Etiqueta tipo={etiqueta} grande={grande} />}
        </View>
        <Pressable
          accessibilityRole="button"
          accessibilityLabel={`Practicar ${nombre}`}
          onPress={onPracticar}
          className="rounded-2xl bg-primario-oscuro"
        >
          {({ pressed }) => (
            <Text
              className={`rounded-2xl bg-primario px-5 text-center font-nunito-black text-white ${
                grande ? 'h-14 text-lg leading-[56px]' : 'h-12 text-base leading-[48px]'
              } ${pressed ? 'translate-y-0' : '-translate-y-1'}`}
            >
              Practicar
            </Text>
          )}
        </Pressable>
      </View>
    </View>
  );
}
