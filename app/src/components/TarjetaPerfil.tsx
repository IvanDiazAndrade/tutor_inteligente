import { Pressable, Text, View } from 'react-native';
import Svg, { Circle, Path } from 'react-native-svg';

type Props = {
  alias: string;
  curso: number;
  seleccionado: boolean;
  onPress: () => void;
  compacta?: boolean;
  grande?: boolean;
};

// Tarjeta de un perfil de estudiante recordado en el dispositivo (RF-A3: perfil + PIN).
export function TarjetaPerfil({
  alias,
  curso,
  seleccionado,
  onPress,
  compacta = false,
  grande = false,
}: Props) {
  const avatar = grande ? 60 : compacta ? 36 : 44;
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityLabel={`${alias}, ${curso}° básico`}
      accessibilityState={{ selected: seleccionado }}
      onPress={onPress}
      className={`flex-row items-center rounded-[18px] border-2 bg-white ${grande ? 'py-5' : 'py-3'} ${
        compacta ? 'gap-2 px-3' : 'gap-3 px-4'
      } ${seleccionado ? 'border-primario-claro' : 'border-borde'}`}
    >
      <Svg width={avatar} height={avatar} viewBox="0 0 48 48">
        <Circle cx={24} cy={24} r={24} fill="#EDE6FC" />
        <Circle cx={24} cy={19} r={8.5} fill="#8B5CF6" />
        <Path d="M8 44 Q24 28 40 44 Z" fill="#8B5CF6" />
      </Svg>
      <View className="flex-1">
        <Text className={`font-nunito-black text-tinta-media ${grande ? 'text-2xl' : 'text-base'}`}>
          {alias} · {curso}° básico
        </Text>
        <Text className={`font-nunito-bold text-lila ${grande ? 'text-base' : 'text-xs'}`}>
          Entra con tu PIN, sin correo
        </Text>
      </View>
      <Svg width={16} height={16} viewBox="0 0 18 18">
        <Path
          d="M6.5 3.5 L12 9 L6.5 14.5"
          fill="none"
          stroke="#8B5CF6"
          strokeWidth={2.6}
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </Svg>
    </Pressable>
  );
}
