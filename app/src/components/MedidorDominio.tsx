import { Text, View } from 'react-native';

import type { Banda } from '@/modelo/progreso';

const COLOR_BANDA: Record<Banda, string> = {
  Dominado: 'bg-banda-dominado',
  Practicando: 'bg-banda-practicando',
  Empezando: 'bg-banda-empezando',
};

type Props = {
  descripcion: string;
  indice: number;
  banda: Banda;
  comentario: string;
  grande?: boolean;
};

// Skill meter de una unidad para el apoderado (RF-DA2, modelo_estudiante.md §6): barra continua
// con la banda en palabras. Sin porcentajes tipo nota ni rojos (RF-DA6). La banda siempre va
// escrita junto a su color, así el dato no depende solo del color.
export function MedidorDominio({ descripcion, indice, banda, comentario, grande = false }: Props) {
  return (
    <View
      accessible
      accessibilityLabel={`${descripcion}: ${banda}. ${comentario}`}
      className="gap-1.5"
    >
      <View className="flex-row items-baseline justify-between gap-2">
        <Text
          className={`flex-1 font-nunito-extrabold text-tinta-media ${grande ? 'text-lg' : 'text-[13.5px]'}`}
        >
          {descripcion}
        </Text>
        <View className="flex-row items-center gap-1.5">
          <View className={`h-2.5 w-2.5 rounded-full ${COLOR_BANDA[banda]}`} />
          <Text className={`font-nunito-black text-tinta ${grande ? 'text-base' : 'text-xs'}`}>
            {banda}
          </Text>
        </View>
      </View>
      <View className={`overflow-hidden rounded-full bg-banda-riel ${grande ? 'h-3.5' : 'h-2.5'}`}>
        <View
          className={`h-full rounded-full ${COLOR_BANDA[banda]}`}
          style={{ width: `${Math.max(6, Math.round(indice * 100))}%` }}
        />
      </View>
      <Text className={`font-nunito text-apagado-oscuro ${grande ? 'text-base' : 'text-xs'}`}>
        {comentario}
      </Text>
    </View>
  );
}
