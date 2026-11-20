import { router } from 'expo-router';
import { useState } from 'react';
import { Pressable, ScrollView, Text, View } from 'react-native';
import { KeyboardAvoidingView } from 'react-native-keyboard-controller';
import { SafeAreaView } from 'react-native-safe-area-context';

import { api, ErrorApi } from '@/api/cliente';
import { BotonPrimario } from '@/components/BotonPrimario';
import { CampoTexto } from '@/components/CampoTexto';
import { Encabezado } from '@/components/Encabezado';
import { entrarComoApoderado } from '@/sesion/entrarComoApoderado';
import { useSesion } from '@/sesion/SesionContext';

// Ingreso del apoderado con correo y contraseña (CU-1, RF-A1, RF-A2; mockup "Acceso", panel A).
export default function IngresoApoderado() {
  const { iniciar, recordarPerfil } = useSesion();
  const [correo, setCorreo] = useState('');
  const [contrasena, setContrasena] = useState('');
  const [aviso, setAviso] = useState('');
  const [enviando, setEnviando] = useState(false);

  const entrar = async () => {
    if (!correo.includes('@') || contrasena.length === 0) {
      setAviso('Escribe tu correo y tu contraseña para continuar.');
      return;
    }
    setAviso('');
    setEnviando(true);
    try {
      const { token } = await api.ingresarApoderado(correo.trim(), contrasena);
      await entrarComoApoderado(token, iniciar, recordarPerfil);
    } catch (e) {
      setAviso(e instanceof ErrorApi ? e.message : 'Algo salió mal. Intenta otra vez.');
    } finally {
      setEnviando(false);
    }
  };

  return (
    <SafeAreaView className="flex-1 bg-fondo">
      <KeyboardAvoidingView behavior="padding" style={{ flex: 1 }}>
        <ScrollView
          contentContainerClassName="grow justify-center p-4"
          keyboardShouldPersistTaps="handled"
        >
          <View className="w-full max-w-[440px] gap-3 self-center rounded-[22px] bg-panel p-5">
            <Encabezado />
            <Text className="mt-1 font-nunito-black text-lg text-tinta">Ingreso del apoderado</Text>
            <CampoTexto
              placeholder="Correo"
              value={correo}
              onChangeText={setCorreo}
              keyboardType="email-address"
              autoCapitalize="none"
              autoComplete="email"
            />
            <CampoTexto
              placeholder="Contraseña"
              value={contrasena}
              onChangeText={setContrasena}
              secureTextEntry
              autoComplete="password"
              onSubmitEditing={entrar}
            />
            {aviso !== '' && (
              <Text className="font-nunito-bold text-sm text-amber-700">{aviso}</Text>
            )}
            <View className="mt-1">
              <BotonPrimario
                titulo={enviando ? 'Entrando…' : 'Entrar'}
                onPress={entrar}
                deshabilitado={enviando}
              />
            </View>
            <Pressable
              accessibilityRole="link"
              onPress={() => router.push('/apoderado/registro')}
              className="items-center py-1"
            >
              <Text className="font-nunito-extrabold text-sm text-primario-claro underline">
                Crear cuenta
              </Text>
            </Pressable>
          </View>
          <Pressable
            accessibilityRole="button"
            onPress={() => (router.canGoBack() ? router.back() : router.replace('/'))}
            className="mt-4 items-center py-2"
          >
            <Text className="font-nunito-extrabold text-sm text-apagado-oscuro">
              ← Volver a ¿Quién va a practicar?
            </Text>
          </Pressable>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}
