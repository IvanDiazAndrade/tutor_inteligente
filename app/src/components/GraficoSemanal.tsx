import { useState } from 'react';
import { Pressable, Text, View } from 'react-native';

const DIAS = ['L', 'M', 'X', 'J', 'V', 'S', 'D'];
const NOMBRES = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'];
const ALTO = 40;

const minutosATexto = (m: number) => (m === 0 ? 'sin práctica' : `${m} min`);

// Minutos de práctica por día (RF-DA1). Una sola serie de barras en un tono, sin leyenda;
// los días sin práctica llevan una marca corta neutra. Al tocar una barra se muestra su valor.
export function GraficoSemanal({
  minutosPorDia,
  grande = false,
}: {
  minutosPorDia: number[];
  grande?: boolean;
}) {
  const [elegido, setElegido] = useState<number | null>(null);
  const maximo = Math.max(...minutosPorDia, 1);
  const alto = grande ? ALTO * 1.5 : ALTO;

  return (
    <View className="gap-1">
      <Text className={`font-nunito-bold text-apagado-oscuro ${grande ? 'text-sm' : 'text-xs'}`}>
        {elegido === null
          ? 'Minutos de práctica por día · toca una barra'
          : `${NOMBRES[elegido]}: ${minutosATexto(minutosPorDia[elegido])}`}
      </Text>
      <View className="flex-row gap-2.5 px-1" style={{ height: alto }}>
        {minutosPorDia.map((m, i) => (
          <Pressable
            key={i}
            accessibilityRole="button"
            accessibilityLabel={`${NOMBRES[i]}: ${minutosATexto(m)}`}
            onPress={() => setElegido(elegido === i ? null : i)}
            className="flex-1 items-center justify-end"
          >
            <View
              className={`w-full max-w-[26px] ${
                m > 0 ? 'rounded-t-[4px] bg-banda-practicando' : 'rounded-[3px] bg-banda-riel'
              } ${elegido === i ? 'opacity-70' : ''}`}
              style={{ height: m > 0 ? Math.max(6, (m / maximo) * alto) : 6 }}
            />
          </Pressable>
        ))}
      </View>
      <View className="flex-row gap-2.5 px-1">
        {DIAS.map((d, i) => (
          <Text
            key={d}
            className={`flex-1 text-center font-nunito-extrabold ${grande ? 'text-sm' : 'text-[11px]'} ${
              elegido === i ? 'text-tinta' : 'text-apagado'
            }`}
          >
            {d}
          </Text>
        ))}
      </View>
    </View>
  );
}
