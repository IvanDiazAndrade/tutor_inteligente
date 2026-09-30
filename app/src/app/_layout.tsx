import '@/global.css';

import {
  Nunito_600SemiBold,
  Nunito_700Bold,
  Nunito_800ExtraBold,
  Nunito_900Black,
  useFonts,
} from '@expo-google-fonts/nunito';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Stack } from 'expo-router';
import * as SplashScreen from 'expo-splash-screen';
import { useEffect } from 'react';

import { ProveedorSesion } from '@/sesion/SesionContext';

SplashScreen.preventAutoHideAsync();

const queryClient = new QueryClient();

export default function RootLayout() {
  const [fuentesListas, errorFuentes] = useFonts({
    Nunito_600SemiBold,
    Nunito_700Bold,
    Nunito_800ExtraBold,
    Nunito_900Black,
  });

  useEffect(() => {
    if (fuentesListas || errorFuentes) {
      SplashScreen.hideAsync();
    }
  }, [fuentesListas, errorFuentes]);

  if (!fuentesListas && !errorFuentes) {
    return null;
  }

  return (
    <QueryClientProvider client={queryClient}>
      <ProveedorSesion>
        <Stack
          screenOptions={{ headerShown: false, contentStyle: { backgroundColor: '#F5F1FF' } }}
        />
      </ProveedorSesion>
    </QueryClientProvider>
  );
}
