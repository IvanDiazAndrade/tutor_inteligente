import { Pressable, Text } from 'react-native';

type Props = {
  texto: string;
  onPress: () => void;
  deshabilitado?: boolean;
  destacado?: boolean;
  grande?: boolean;
};

// Botón redondeado de las acciones del tutor: pista, no entiendo, otro ejercicio (§2 del
// modelo pedagógico). "destacado" se usa para ofrecer "¿Lo resolvemos juntos?".
export function BotonAccion({
  texto,
  onPress,
  deshabilitado = false,
  destacado = false,
  grande = false,
}: Props) {
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityState={{ disabled: deshabilitado }}
      disabled={deshabilitado}
      onPress={onPress}
      className={`rounded-full border-[1.5px] disabled:opacity-40 ${grande ? 'px-5 py-4' : 'px-3.5 py-3'} ${
        destacado
          ? 'border-primario bg-primario active:bg-primario-oscuro'
          : 'border-globo bg-white active:bg-fondo'
      }`}
    >
      <Text
        className={`font-nunito-extrabold ${grande ? 'text-lg' : 'text-[13px]'} ${
          destacado ? 'text-white' : 'text-primario'
        }`}
      >
        {texto}
      </Text>
    </Pressable>
  );
}
