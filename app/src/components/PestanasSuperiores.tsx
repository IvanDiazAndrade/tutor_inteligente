import { useState } from 'react';
import { Animated, Pressable, Text, View } from 'react-native';

type Props = {
  titulos: string[];
  activa: number;
  onElegir: (indice: number) => void;
  // Posición del deslizamiento entre pestañas: 0 = primera, 1 = segunda... Mueve la barra
  // indicadora junto con el dedo.
  posicion: Animated.Value | Animated.AnimatedInterpolation<number>;
  grande?: boolean;
};

// Pestañas superiores (estilo de las redes sociales): títulos del mismo ancho y una barra bajo
// el activo que acompaña el deslizamiento.
export function PestanasSuperiores({ titulos, activa, onElegir, posicion, grande = false }: Props) {
  const [anchoPestana, setAnchoPestana] = useState(0);
  const anchoBarra = grande ? 88 : 64;
  const inicio = (anchoPestana - anchoBarra) / 2;

  return (
    <View
      accessibilityRole="tablist"
      onLayout={(e) => setAnchoPestana(e.nativeEvent.layout.width / titulos.length)}
      className="border-b-[1.5px] border-borde"
    >
      <View className="flex-row">
        {titulos.map((titulo, i) => (
          <Pressable
            key={titulo}
            accessibilityRole="tab"
            accessibilityState={{ selected: i === activa }}
            onPress={() => onElegir(i)}
            className={`flex-1 items-center justify-center active:bg-lila-fondo ${
              grande ? 'h-14' : 'h-12'
            }`}
          >
            <Text
              className={`${grande ? 'text-xl' : 'text-base'} ${
                i === activa ? 'font-nunito-black text-tinta' : 'font-nunito-bold text-apagado'
              }`}
            >
              {titulo}
            </Text>
          </Pressable>
        ))}
      </View>
      {anchoPestana > 0 && (
        <Animated.View
          className="absolute bottom-0 left-0 h-1 rounded-full bg-primario"
          style={{
            width: anchoBarra,
            transform: [
              {
                translateX: posicion.interpolate({
                  inputRange: [0, titulos.length - 1],
                  outputRange: [inicio, inicio + anchoPestana * (titulos.length - 1)],
                  extrapolate: 'clamp',
                }),
              },
            ],
          }}
        />
      )}
    </View>
  );
}
