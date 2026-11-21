import { Pressable, Text, View } from 'react-native';

type Props = {
  izquierda: string;
  derecha: string;
  simbolo: string;
  onCambio: (simbolo: string) => void;
  deshabilitado?: boolean;
  grande?: boolean;
};

const SIMBOLOS = [
  { simbolo: '<', nombre: 'es menor que' },
  { simbolo: '=', nombre: 'es igual a' },
  { simbolo: '>', nombre: 'es mayor que' },
];

// Respuesta "comparar" (modelo_dominio.md §3.2): los dos valores con un casillero al medio y
// tres botones grandes para elegir <, = o >. El elegido queda marcado y aparece en el casillero.
export function RespuestaComparar({
  izquierda,
  derecha,
  simbolo,
  onCambio,
  deshabilitado = false,
  grande = false,
}: Props) {
  const valor = grande ? 'text-4xl' : 'text-3xl';
  return (
    <View className="w-full items-center gap-4">
      <View className="flex-row items-center justify-center gap-3">
        <Text className={`font-nunito-black text-tinta ${valor}`}>{izquierda}</Text>
        <View
          className={`items-center justify-center rounded-2xl border-[2.5px] ${
            simbolo ? 'border-primario bg-fondo' : 'border-dashed border-lila-suave bg-white'
          } ${grande ? 'h-20 w-20' : 'h-16 w-16'}`}
        >
          <Text className={`font-nunito-black text-primario ${valor}`}>{simbolo || '?'}</Text>
        </View>
        <Text className={`font-nunito-black text-tinta ${valor}`}>{derecha}</Text>
      </View>
      <View className="flex-row justify-center gap-3">
        {SIMBOLOS.map((s) => (
          <Pressable
            key={s.simbolo}
            accessibilityRole="button"
            accessibilityLabel={`${izquierda} ${s.nombre} ${derecha}`}
            accessibilityState={{ selected: simbolo === s.simbolo, disabled: deshabilitado }}
            disabled={deshabilitado}
            onPress={() => onCambio(s.simbolo)}
            className={`items-center justify-center rounded-2xl ${grande ? 'h-20 w-24' : 'h-16 w-20'} ${
              simbolo === s.simbolo
                ? 'bg-primario active:bg-primario-oscuro'
                : 'border-[2.5px] border-lila-suave bg-white active:bg-fondo'
            }`}
          >
            <Text
              className={`font-nunito-black ${valor} ${simbolo === s.simbolo ? 'text-white' : 'text-primario'}`}
            >
              {s.simbolo}
            </Text>
          </Pressable>
        ))}
      </View>
    </View>
  );
}
