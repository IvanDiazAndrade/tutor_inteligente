import { router, useLocalSearchParams } from 'expo-router';
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

// Crear un perfil de estudiante (CU-9; RF-A1, A5): solo alias y curso. No se piden nombre
// completo, RUT, colegio ni fecha de nacimiento (RNF-S2). El estudiante no tiene PIN: entra
// tocando su perfil en el dispositivo vinculado (RF-A3). Una cuenta puede tener hasta 3. El
// primero se crea al registrarse (y luego se vuelve al acceso); los demás, desde el panel.
function CrearPerfil() {
  const { sesion, perfiles, actualizarPerfil, cerrar } = useSesion();
  const primero = perfiles.length === 0;
  // Desde la pantalla de acceso ("+ Agregar estudiante") se vuelve a ella; desde el panel, al panel.
  const { volver } = useLocalSearchParams<{ volver?: 'acceso' }>();
  const alAcceso = primero || volver === 'acceso';
  const regresar = async () => {
    if (alAcceso) {
      await cerrar();
      router.replace('/');
    } else {
      router.replace('/apoderado');
    }
  };
  const [alias, setAlias] = useState('');
  const [curso, setCurso] = useState<number | null>(null);
  const [aviso, setAviso] = useState('');
  const [enviando, setEnviando] = useState(false);

  const crear = async () => {
    if (alias.trim().length === 0) return setAviso('Escribe cómo quiere que lo llamen.');
    if (curso === null) return setAviso('Elige el curso.');
    setAviso('');
    setEnviando(true);
    try {
      const perfil = await api.crearEstudiante(sesion!.token, { alias: alias.trim(), curso });
      await actualizarPerfil({ id: perfil.id, alias: perfil.alias, curso: perfil.curso });
      // Con el perfil creado se vuelve a la pantalla de acceso (para elegir a qué entrar) o al panel.
      await regresar();
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
                {primero ? 'Perfil del estudiante' : 'Agregar otro estudiante'}
              </Text>
            </View>
            <Text className="font-nunito-bold text-sm text-apagado-oscuro">
              Solo pedimos un apodo y el curso. El estudiante entra tocando su perfil, sin correo ni
              PIN.
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
            {!primero && (
              <Pressable
                accessibilityRole="button"
                onPress={regresar}
                className="items-center py-2"
              >
                <Text className="font-nunito-extrabold text-sm text-apagado-oscuro">
                  {alAcceso ? '← Volver' : '← Volver al panel'}
                </Text>
              </Pressable>
            )}
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
