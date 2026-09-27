import { useLocalSearchParams } from 'expo-router';

import { PantallaProvisoria } from '@/components/PantallaProvisoria';

// Pantalla del ejercicio con Octavio (mockup "Ejercicio Estudiante"): siguiente paso de la tarea 42.
export default function Ejercicio() {
  const { nombre } = useLocalSearchParams<{ nombre?: string }>();
  return (
    <PantallaProvisoria
      titulo={nombre ?? 'Ejercicio'}
      descripcion="Aquí irá el ejercicio con Octavio (siguiente pantalla del prototipo)."
      conVolver
    />
  );
}
