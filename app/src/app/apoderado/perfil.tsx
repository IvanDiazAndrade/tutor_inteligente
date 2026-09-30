import { router } from 'expo-router';
import { useState } from 'react';
import { KeyboardAvoidingView, Pressable, ScrollView, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { api, ErrorApi } from '@/api/cliente';
import { BotonPrimario } from '@/components/BotonPrimario';
import { CampoTexto } from '@/components/CampoTexto';
import { Octavio } from '@/components/Octavio';
import { Protegida } from '@/sesion/Protegida';
import { useSesion } from '@/sesion/SesionContext';

const CURSOS = [4, 5, 6] as const;

// Crear el perfil del estudiante (CU-9; RF-A1, A3, A5): solo alias, curso y un PIN corto.
// No se piden nombre completo, RUT, colegio ni fecha de nacimiento (RNF-S2).
function CrearPerfil() {
  const { sesion, recordarPerfil } = useSesion();
  const [alias, setAlias] = useState('');
  const [curso, setCurso] = useState<number | null>(null);
  const [pin, setPin] = useState('');
  const [pinRepetido, setPinRepetido] = useState('');
  const [aviso, setAviso] = useState('');
  const [enviando, setEnviando] = useState(false);

  const soloDigitos = (v: string) => v.replace(/\D/g, '').slice(0, 4);

  const crear = async () => {
    if (alias.trim().length === 0) return setAviso('Escribe cómo quiere que lo llamen.');
    if (curso === null) return setAviso('Elige el curso.');
    if (pin.length !== 4) return setAviso('El PIN debe tener 4 números.');
    if (pin !== pinRepetido) return setAviso('Los PIN no coinciden.');
    setAviso('');
    setEnviando(true);
    try {
      const perfil = await api.crearEstudiante(sesion!.token, { alias: alias.trim(), curso, pin });
      await recordarPerfil({ id: perfil.id, alias: perfil.alias, curso: perfil.curso });
      router.replace('/apoderado');
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
            <View className="flex-row items-center gap-3">
              <Octavio tamano={56} conVarita />
              <Text className="flex-1 font-nunito-black text-lg text-tinta">
                Perfil del estudiante
              </Text>
            </View>
            <Text className="font-nunito-bold text-sm text-apagado-oscuro">
              Solo pedimos un apodo y el curso. Con el PIN, el estudiante entra sin correo.
            </Text>
            <CampoTexto
              placeholder="Apodo (por ejemplo, Vale)"
              value={alias}
              onChangeText={setAlias}
              maxLength={30}
              autoCapitalize="words"
            />
            <View className="flex-row gap-2">
              {CURSOS.map((c) => (
                <Pressable
                  key={c}
                  accessibilityRole="radio"
                  accessibilityState={{ selected: curso === c }}
                  onPress={() => setCurso(c)}
                  className={`h-12 flex-1 items-center justify-center rounded-2xl border-[1.5px] ${
                    curso === c ? 'border-primario bg-primario' : 'border-borde bg-white'
                  }`}
                >
                  <Text
                    className={`font-nunito-black text-base ${
                      curso === c ? 'text-white' : 'text-tinta-tecla'
                    }`}
                  >
                    {c}° básico
                  </Text>
                </Pressable>
              ))}
            </View>
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
                titulo={enviando ? 'Creando…' : 'Crear perfil'}
                onPress={crear}
                deshabilitado={enviando}
              />
            </View>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

export default function PantallaPerfil() {
  return (
    <Protegida rol="apoderado">
      <CrearPerfil />
    </Protegida>
  );
}
