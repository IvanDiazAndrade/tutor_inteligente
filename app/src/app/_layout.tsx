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
import { KeyboardProvider } from 'react-native-keyboard-controller';

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
    // KeyboardProvider: mide el teclado también con el modo edge-to-edge de Android, donde el
    // KeyboardAvoidingView de react-native no achica la pantalla.
    <KeyboardProvider>
      <QueryClientProvider client={queryClient}>
        <ProveedorSesion>
          <Stack
            screenOptions={{ headerShown: false, contentStyle: { backgroundColor: '#F5F1FF' } }}
          />
        </ProveedorSesion>
      </QueryClientProvider>
    </KeyboardProvider>
  );
}
