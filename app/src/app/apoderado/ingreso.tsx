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

// Inicio de sesión del apoderado con correo y contraseña (CU-1, RF-A1, RF-A2; mockup "Acceso",
// panel A). Es la primera pantalla mientras el dispositivo no esté vinculado a una cuenta; al
// entrar queda vinculado y después el niño entra tocando su perfil.
export default function IngresoApoderado() {
  const { vincular, iniciar, recordarPerfil } = useSesion();
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
      const ingreso = await api.ingresarApoderado(correo.trim(), contrasena);
      await entrarComoApoderado(ingreso, { vincular, iniciar, recordarPerfil });
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
            <Text className="mt-1 font-nunito-black text-lg text-tinta">Inicio de sesión</Text>
            <Text className="font-nunito-bold text-sm text-apagado-oscuro">
              La cuenta es del apoderado. Inicias sesión una sola vez en este teléfono; después el
              estudiante entra tocando su perfil.
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
                ¿No tienes cuenta? Registrarse
              </Text>
            </Pressable>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}
