import { View } from 'react-native';
import Svg, { Path } from 'react-native-svg';

const ESTRELLA =
  'M12 2.5 L14.9 8.6 L21.5 9.4 L16.6 13.9 L17.9 20.5 L12 17.2 L6.1 20.5 L7.4 13.9 L2.5 9.4 L9.1 8.6 Z';

// Nivel de la unidad en estrellas (modelo_estudiante.md §6): las no ganadas se ven tenues.
// Se dibujan en SVG porque los emoji no admiten opacidad dentro de un texto en React Native.
export function Estrellas({ cantidad, grande = false }: { cantidad: number; grande?: boolean }) {
  const tamano = grande ? 22 : 16;
  return (
    <View accessible accessibilityLabel={`${cantidad} de 3 estrellas`} className="flex-row gap-1">
      {[0, 1, 2].map((i) => (
        <Svg key={i} width={tamano} height={tamano} viewBox="0 0 24 24">
          <Path
            d={ESTRELLA}
            fill={i < cantidad ? '#FBBF24' : '#FDE7B0'}
            stroke={i < cantidad ? '#F59E0B' : '#FBE3A6'}
            strokeWidth={1.2}
            strokeLinejoin="round"
          />
        </Svg>
      ))}
    </View>
  );
}
