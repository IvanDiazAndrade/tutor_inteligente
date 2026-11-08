import { Stack } from 'expo-router';

// La lista queda siempre debajo del detalle, aunque el detalle se abra desde otra pestaña.
export const unstable_settings = { initialRouteName: 'index' };

export default function LayoutPestana() {
  return (
    <Stack screenOptions={{ headerShown: false, contentStyle: { backgroundColor: '#FAF7FF' } }} />
  );
}
