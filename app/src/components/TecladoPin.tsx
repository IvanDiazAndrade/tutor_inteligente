import { Pressable, Text, View } from 'react-native';

export const LARGO_PIN = 4;

type Props = {
  pin: string;
  onCambio: (pin: string) => void;
  error?: boolean;
  grande?: boolean;
};

const TECLAS = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '', '0', '⌫'];

// Puntos de avance + teclado numérico propio: evita el teclado del sistema y deja
// botones grandes para niños de 9 a 12 años (RNF-U1).
export function TecladoPin({ pin, onCambio, error = false, grande = false }: Props) {
  const claseTecla = grande ? 'h-16 w-24' : 'h-12 w-[72px]';
  const pulsar = (tecla: string) => {
    if (tecla === '⌫') {
      onCambio(pin.slice(0, -1));
    } else if (pin.length < LARGO_PIN) {
      onCambio(pin + tecla);
    }
  };

  return (
    <View className="items-center gap-3">
      <View className="flex-row gap-3" accessibilityLabel={`${pin.length} de ${LARGO_PIN} dígitos`}>
        {Array.from({ length: LARGO_PIN }, (_, i) => (
          <View
            key={i}
            className={`rounded-full ${grande ? 'h-6 w-6' : 'h-[18px] w-[18px]'} ${
              i < pin.length
                ? error
                  ? 'bg-amber-500'
                  : 'bg-primario'
                : 'border-[2.5px] border-lila-suave bg-white'
            }`}
          />
        ))}
      </View>
      <View
        className={`flex-row flex-wrap justify-center ${grande ? 'w-[312px] gap-2' : 'w-[228px] gap-1.5'}`}
      >
        {TECLAS.map((t, i) =>
          t === '' ? (
            <View key={i} className={claseTecla} />
          ) : (
            <Pressable
              key={i}
              accessibilityRole="button"
              accessibilityLabel={t === '⌫' ? 'Borrar' : t}
              onPress={() => pulsar(t)}
              className={`${claseTecla} items-center justify-center rounded-xl ${
                t === '⌫' ? 'active:bg-fondo' : 'bg-fondo active:bg-lila-fondo'
              }`}
            >
              <Text
                className={`font-nunito-black ${grande ? 'text-3xl' : 'text-xl'} ${t === '⌫' ? 'text-lila-apagado' : 'text-tinta-tecla'}`}
              >
                {t}
              </Text>
            </Pressable>
          ),
        )}
      </View>
    </View>
  );
}
