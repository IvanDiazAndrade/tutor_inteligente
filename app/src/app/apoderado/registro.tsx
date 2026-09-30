import { router } from 'expo-router';
import { useState } from 'react';
import { KeyboardAvoidingView, Pressable, ScrollView, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { api, ErrorApi } from '@/api/cliente';
import { BotonPrimario } from '@/components/BotonPrimario';
import { CampoTexto } from '@/components/CampoTexto';
import { Encabezado } from '@/components/Encabezado';
import { entrarComoApoderado } from '@/sesion/entrarComoApoderado';
import { useSesion } from '@/sesion/SesionContext';

const LARGO_MINIMO = 8;

// Registro del apoderado, titular de la cuenta (CU-9, RF-A1). Tras crear la cuenta entra
// directamente y pasa a crear el perfil del estudiante.
export default function RegistroApoderado() {
  const { iniciar, recordarPerfil } = useSesion();
  const [correo, setCorreo] = useState('');
  const [contrasena, setContrasena] = useState('');
  const [repetida, setRepetida] = useState('');
  const [aviso, setAviso] = useState('');
  const [enviando, setEnviando] = useState(false);

  const crear = async () => {
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(correo.trim())) {
      setAviso('Escribe un correo válido.');
      return;
    }
    if (contrasena.length < LARGO_MINIMO) {
      setAviso(`La contraseña debe tener al menos ${LARGO_MINIMO} caracteres.`);
      return;
    }
    if (contrasena !== repetida) {
      setAviso('Las contraseñas no coinciden.');
      return;
    }
    setAviso('');
    setEnviando(true);
    try {
      await api.registrarApoderado(correo.trim(), contrasena);
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
      <KeyboardAvoidingView behavior="height" className="flex-1">
        <ScrollView
          contentContainerClassName="grow justify-center p-4"
          keyboardShouldPersistTaps="handled"
        >
          <View className="w-full max-w-[440px] gap-3 self-center rounded-[22px] bg-panel p-5">
            <Encabezado />
            <Text className="mt-1 font-nunito-black text-lg text-tinta">Crear cuenta</Text>
            <Text className="font-nunito-bold text-sm text-apagado-oscuro">
              La cuenta es del apoderado. Después vas a crear el perfil del estudiante con un PIN de
              4 números.
            </Text>
            <CampoTexto
              placeholder="Correo"
              value={correo}
              onChangeText={setCorreo}
              keyboardType="email-address"
              autoCapitalize="none"
              autoComplete="email"
            />
            <CampoTexto
              placeholder={`Contraseña (mínimo ${LARGO_MINIMO} caracteres)`}
              value={contrasena}
              onChangeText={setContrasena}
              secureTextEntry
              autoComplete="new-password"
            />
            <CampoTexto
              placeholder="Repite la contraseña"
              value={repetida}
              onChangeText={setRepetida}
              secureTextEntry
              autoComplete="new-password"
              onSubmitEditing={crear}
            />
            {aviso !== '' && (
              <Text className="font-nunito-bold text-sm text-amber-700">{aviso}</Text>
            )}
            <View className="mt-1">
              <BotonPrimario
                titulo={enviando ? 'Creando…' : 'Crear cuenta'}
                onPress={crear}
                deshabilitado={enviando}
              />
            </View>
          </View>
          <Pressable
            accessibilityRole="button"
            onPress={() => router.back()}
            className="mt-4 items-center py-2"
          >
            <Text className="font-nunito-extrabold text-sm text-apagado-oscuro">
              ← Ya tengo cuenta
            </Text>
          </Pressable>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}
