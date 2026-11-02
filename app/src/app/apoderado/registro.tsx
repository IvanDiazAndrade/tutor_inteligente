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

const soloDigitos = (v: string) => v.replace(/\D/g, '').slice(0, 4);

// Registro del apoderado, titular de la cuenta (CU-9, RF-A1). Aquí se define también el PIN
// del panel (RF-A3). Tras registrarse entra directamente, el teléfono queda vinculado y pasa a
// crear el perfil del estudiante.
export default function RegistroApoderado() {
  const { vincular, iniciar, recordarPerfil } = useSesion();
  const [correo, setCorreo] = useState('');
  const [contrasena, setContrasena] = useState('');
  const [repetida, setRepetida] = useState('');
  const [pin, setPin] = useState('');
  const [pinRepetido, setPinRepetido] = useState('');
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
    if (pin.length !== 4) {
      setAviso('El PIN debe tener 4 números.');
      return;
    }
    if (pin !== pinRepetido) {
      setAviso('Los PIN no coinciden.');
      return;
    }
    setAviso('');
    setEnviando(true);
    try {
      await api.registrarApoderado(correo.trim(), contrasena, pin);
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
            <Text className="mt-1 font-nunito-black text-lg text-tinta">Registrarse</Text>
            <Text className="font-nunito-bold text-sm text-apagado-oscuro">
              La cuenta es del apoderado. Después vas a crear el perfil del estudiante.
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
            />
            <Text className="mt-1 font-nunito-bold text-sm text-apagado-oscuro">
              PIN de apoderado: 4 números para entrar a tu panel. El estudiante entra sin PIN.
            </Text>
            <CampoTexto
              placeholder="PIN de 4 números"
              value={pin}
              onChangeText={(v) => setPin(soloDigitos(v))}
              keyboardType="number-pad"
              secureTextEntry
            />
            <CampoTexto
              placeholder="Repite el PIN"
              value={pinRepetido}
              onChangeText={(v) => setPinRepetido(soloDigitos(v))}
              keyboardType="number-pad"
              secureTextEntry
              onSubmitEditing={crear}
            />
            {aviso !== '' && (
              <Text className="font-nunito-bold text-sm text-amber-700">{aviso}</Text>
            )}
            <View className="mt-1">
              <BotonPrimario
                titulo={enviando ? 'Registrando…' : 'Registrarse'}
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
