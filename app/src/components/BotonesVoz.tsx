import { Pressable, Text, View } from 'react-native';

type Props = {
  activa: boolean | null; // null: todavía no se sabe si está encendida
  onAlternar: () => void;
  onRepetir?: () => void; // sin esto no hay nada que repetir
  grande?: boolean;
};

// Encender o silenciar a Octavio, y escucharlo otra vez.
export function BotonesVoz({ activa, onAlternar, onRepetir, grande = false }: Props) {
  if (activa === null) return null;
  const boton = (icono: string, etiqueta: string, onPress: () => void) => (
    <Pressable
      accessibilityRole="button"
      accessibilityLabel={etiqueta}
      onPress={onPress}
      className={`items-center justify-center rounded-full bg-lila-fondo active:bg-lila-suave ${
        grande ? 'h-14 w-14' : 'h-11 w-11'
      }`}
    >
      <Text className={grande ? 'text-2xl' : 'text-xl'}>{icono}</Text>
    </Pressable>
  );
  return (
    <View className="flex-row gap-2">
      {activa && onRepetir && boton('🔁', 'Escuchar otra vez', onRepetir)}
      {boton(
        activa ? '🔊' : '🔇',
        activa ? 'Silenciar a Octavio' : 'Escuchar a Octavio',
        onAlternar,
      )}
    </View>
  );
}
