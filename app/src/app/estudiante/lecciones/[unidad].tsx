import { useLocalSearchParams } from 'expo-router';

import { DetalleUnidad, type Vista } from '@/components/DetalleUnidad';

// Pestaña Lecciones, nivel 2: la unidad con su lección y sus ejercicios en pestañas superiores.
// `?vista=ejercicios` la abre directamente en los ejercicios.
export default function DetalleLeccion() {
  const { unidad, vista } = useLocalSearchParams<{ unidad: string; vista?: Vista }>();
  return (
    <DetalleUnidad unidad={unidad} inicial={vista === 'ejercicios' ? 'ejercicios' : 'leccion'} />
  );
}
