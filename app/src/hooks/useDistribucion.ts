import { useWindowDimensions } from 'react-native';

// Decide la distribución según el espacio disponible (RNF-U4): en horizontal hay ancho para
// dos columnas; en vertical (teléfono o tablet) todo va en una columna. En tablet todo se agranda.
export function useDistribucion() {
  const { width, height } = useWindowDimensions();
  return {
    dosColumnas: width > height,
    esTablet: Math.min(width, height) >= 600,
  };
}
