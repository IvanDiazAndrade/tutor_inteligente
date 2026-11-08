import type { ReactNode } from 'react';
import { Pressable, Text, View } from 'react-native';

// Une con espacios no separables los signos y sus números ("7 : 3 = 2"), para que una
// operación no quede cortada entre dos líneas.
const sinCortes = (texto: string) => texto.replace(/ ([:×+−=]) /g, '\u00A0$1\u00A0');

type Props = {
  antetitulo: string; // "Lección 3", "Parte 2", "Ejercicio 1"…
  titulo: string;
  resumen: string;
  lineasResumen?: number; // sin límite si se omite (p. ej. la explicación de una parte)
  pie?: ReactNode; // estrellas, etiquetas…
  onPress?: () => void; // sin onPress la tarjeta solo muestra contenido
  deshabilitada?: boolean;
  grande?: boolean;
};

// Tarjeta común de las pestañas Lecciones y Ejercicios, para que ambas se vean iguales.
// Al tocarla, el borde y el fondo toman el color de acento y la tarjeta se eleva.
export function TarjetaLista({
  antetitulo,
  titulo,
  resumen,
  lineasResumen,
  pie,
  onPress,
  deshabilitada = false,
  grande = false,
}: Props) {
  const contenido = (presionada: boolean) => (
    <View
      className={`gap-1 rounded-[20px] border-2 px-4 ${grande ? 'py-5' : 'py-4'} ${
        presionada ? 'border-primario-claro bg-lila-fondo' : 'border-borde bg-white'
      } ${deshabilitada ? 'opacity-60' : ''}`}
      style={{ elevation: presionada ? 4 : 0 }}
    >
      <Text
        className={`font-nunito-black uppercase tracking-wide text-primario-claro ${
          grande ? 'text-sm' : 'text-xs'
        }`}
      >
        {antetitulo}
      </Text>
      <Text className={`font-nunito-black text-tinta ${grande ? 'text-2xl' : 'text-xl'}`}>
        {titulo}
      </Text>
      <Text
        numberOfLines={lineasResumen}
        className={`font-nunito-bold text-apagado-oscuro ${grande ? 'text-lg' : 'text-[15px]'}`}
      >
        {sinCortes(resumen)}
      </Text>
      {pie && <View className="mt-1.5 flex-row flex-wrap items-center gap-2">{pie}</View>}
    </View>
  );

  if (!onPress) return contenido(false);
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityLabel={`${antetitulo}: ${titulo}`}
      accessibilityState={{ disabled: deshabilitada }}
      disabled={deshabilitada}
      onPress={onPress}
    >
      {({ pressed }) => contenido(pressed)}
    </Pressable>
  );
}
