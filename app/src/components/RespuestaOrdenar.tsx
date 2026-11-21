import { Pressable, Text, View } from 'react-native';

type Props = {
  valores: string[];
  seleccion: string[];
  onCambio: (seleccion: string[]) => void;
  deshabilitado?: boolean;
  grande?: boolean;
};

// Respuesta "ordenar" (modelo_dominio.md §3.2): el niño toca los valores en el orden pedido y
// van quedando numerados en la fila de arriba. Tocar uno ya elegido lo quita (y los siguientes),
// así puede corregir sin borrar todo. Sin arrastrar: tocar es más fácil a los 9-12 años.
export function RespuestaOrdenar({
  valores,
  seleccion,
  onCambio,
  deshabilitado = false,
  grande = false,
}: Props) {
  const elegidos = new Set(seleccion);
  const texto = grande ? 'text-3xl' : 'text-2xl';
  const ficha = grande ? 'min-w-24 px-5 py-4' : 'min-w-[72px] px-4 py-3';

  return (
    <View className="w-full items-center gap-4">
      <View className="min-h-16 flex-row flex-wrap justify-center gap-2">
        {valores.map((_, i) => {
          const valor = seleccion[i];
          return (
            <Pressable
              key={i}
              accessibilityRole="button"
              accessibilityLabel={
                valor ? `Lugar ${i + 1}: ${valor}. Tocar para quitar` : `Lugar ${i + 1}, vacío`
              }
              disabled={deshabilitado || !valor}
              onPress={() => onCambio(seleccion.slice(0, i))}
              className={`items-center rounded-2xl border-[2.5px] ${ficha} ${
                valor ? 'border-primario bg-fondo' : 'border-dashed border-lila-suave bg-white'
              }`}
            >
              <Text className="font-nunito-bold text-xs text-lila">{i + 1}°</Text>
              <Text className={`font-nunito-black text-tinta ${texto}`}>{valor ?? ' '}</Text>
            </Pressable>
          );
        })}
      </View>
      <View className="flex-row flex-wrap justify-center gap-2">
        {valores
          .filter((v) => !elegidos.has(v))
          .map((valor) => (
            <Pressable
              key={valor}
              accessibilityRole="button"
              accessibilityLabel={`Elegir ${valor}`}
              disabled={deshabilitado}
              onPress={() => onCambio([...seleccion, valor])}
              className={`items-center rounded-2xl bg-primario active:bg-primario-oscuro ${ficha}`}
            >
              <Text className={`font-nunito-black text-white ${texto}`}>{valor}</Text>
            </Pressable>
          ))}
      </View>
    </View>
  );
}
