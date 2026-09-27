import { Pressable, Text } from 'react-native';

type Props = {
  titulo: string;
  onPress: () => void;
  deshabilitado?: boolean;
  grande?: boolean;
};

// Botón principal con la "sombra sólida" de los mockups; al presionarlo baja 4 px.
export function BotonPrimario({ titulo, onPress, deshabilitado = false, grande = false }: Props) {
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityState={{ disabled: deshabilitado }}
      disabled={deshabilitado}
      onPress={onPress}
      className="rounded-2xl bg-primario-oscuro disabled:opacity-50"
    >
      {({ pressed }) => (
        <Text
          className={`rounded-2xl bg-primario text-center font-nunito-black text-white ${
            grande ? 'h-16 text-2xl leading-[64px]' : 'h-12 text-base leading-[48px]'
          } ${pressed ? 'translate-y-0' : '-translate-y-1'}`}
        >
          {titulo}
        </Text>
      )}
    </Pressable>
  );
}
