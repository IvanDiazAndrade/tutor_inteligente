import { router } from 'expo-router';
import { useState } from 'react';
import { KeyboardAvoidingView, Pressable, ScrollView, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { BotonPrimario } from '@/components/BotonPrimario';
import { CampoTexto } from '@/components/CampoTexto';
import { Encabezado } from '@/components/Encabezado';

// Ingreso del apoderado con correo y contraseña (CU-1, RF-A1, RF-A2; mockup "Acceso", panel A).
// Prototipo: no llama a la API; cualquier correo y contraseña no vacíos entran al panel.
export default function IngresoApoderado() {
  const [correo, setCorreo] = useState('');
  const [contrasena, setContrasena] = useState('');
  const [aviso, setAviso] = useState('');

  const entrar = () => {
    if (!correo.includes('@') || contrasena.length === 0) {
      setAviso('Escribe tu correo y tu contraseña para continuar.');
      return;
    }
    setAviso('');
    router.replace('/apoderado');
  };

  return (
    <SafeAreaView className="flex-1 bg-fondo">
      <KeyboardAvoidingView behavior="height" className="flex-1">
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
            />
            {aviso !== '' && (
              <Text className="font-nunito-bold text-sm text-amber-700">{aviso}</Text>
            )}
            <View className="mt-1">
              <BotonPrimario titulo="Entrar" onPress={entrar} />
            </View>
            <Pressable accessibilityRole="link" className="items-center py-1">
              <Text className="font-nunito-extrabold text-sm text-primario-claro underline">
                Crear cuenta
              </Text>
            </Pressable>
          </View>
          <Pressable
            accessibilityRole="button"
            onPress={() => router.back()}
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
