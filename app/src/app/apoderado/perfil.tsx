import { useQueryClient } from '@tanstack/react-query';
import { router } from 'expo-router';
import { useState } from 'react';
import { Pressable, ScrollView, Text, View } from 'react-native';
import { KeyboardAvoidingView } from 'react-native-keyboard-controller';
import { SafeAreaView } from 'react-native-safe-area-context';

import { api, ErrorApi, type PerfilEstudiante } from '@/api/cliente';
import { BotonPrimario } from '@/components/BotonPrimario';
import { CampoTexto } from '@/components/CampoTexto';
import { EstadoConsulta } from '@/components/EstadoConsulta';
import { Octavio } from '@/components/Octavio';
import { Protegida } from '@/sesion/Protegida';
import { useSesion } from '@/sesion/SesionContext';
import { useConsulta } from '@/sesion/useConsulta';

const CURSOS = [4, 5, 6] as const;

// Crear o editar el perfil del estudiante (CU-9; RF-A1, A3, A4, A5): solo alias, curso y un
// PIN corto. No se piden nombre completo, RUT, colegio ni fecha de nacimiento (RNF-S2).
// Al editar, el PIN vacío se mantiene, y cambiar de curso conserva el historial (RF-A4).
function FormularioPerfil({ existente }: { existente: PerfilEstudiante | null }) {
  const { sesion, recordarPerfil } = useSesion();
  const consultas = useQueryClient();
  const editando = existente !== null;
  const [alias, setAlias] = useState(existente?.alias ?? '');
  const [curso, setCurso] = useState<number | null>(existente?.curso ?? null);
  const [pin, setPin] = useState('');
  const [pinRepetido, setPinRepetido] = useState('');
  const [aviso, setAviso] = useState('');
  const [enviando, setEnviando] = useState(false);

  const soloDigitos = (v: string) => v.replace(/\D/g, '').slice(0, 4);

  const crear = async () => {
    if (alias.trim().length === 0) return setAviso('Escribe cómo quiere que lo llamen.');
    if (curso === null) return setAviso('Elige el curso.');
    const cambiaPin = !editando || pin.length > 0 || pinRepetido.length > 0;
    if (cambiaPin && pin.length !== 4) return setAviso('El PIN debe tener 4 números.');
    if (cambiaPin && pin !== pinRepetido) return setAviso('Los PIN no coinciden.');
    setAviso('');
    setEnviando(true);
    try {
      const datos = { alias: alias.trim(), curso, ...(cambiaPin ? { pin } : {}) };
      const perfil = editando
        ? await api.editarEstudiante(sesion!.token, datos)
        : await api.crearEstudiante(sesion!.token, { ...datos, pin });
      await recordarPerfil({ id: perfil.id, alias: perfil.alias, curso: perfil.curso });
      await consultas.invalidateQueries({ queryKey: ['panel-apoderado'] });
      await consultas.invalidateQueries({ queryKey: ['estudiante-del-apoderado'] });
      router.replace('/apoderado');
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
            <View className="flex-row items-center gap-3">
              <Octavio tamano={56} conVarita />
              <Text className="flex-1 font-nunito-black text-lg text-tinta">
                {editando ? 'Editar perfil' : 'Perfil del estudiante'}
              </Text>
            </View>
            <Text className="font-nunito-bold text-sm text-apagado-oscuro">
              {editando
                ? 'Si cambia de curso, su avance se conserva. Deja el PIN en blanco para no cambiarlo.'
                : 'Solo pedimos un apodo y el curso. Con el PIN, el estudiante entra sin correo.'}
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
              placeholder={editando ? 'PIN nuevo (opcional)' : 'PIN de 4 números'}
              value={pin}
              onChangeText={(v) => setPin(soloDigitos(v))}
              keyboardType="number-pad"
              secureTextEntry
            />
            <CampoTexto
              placeholder={editando ? 'Repite el PIN nuevo' : 'Repite el PIN'}
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
                titulo={enviando ? 'Guardando…' : editando ? 'Guardar cambios' : 'Crear perfil'}
                onPress={crear}
                deshabilitado={enviando}
              />
            </View>
            {editando && (
              <Pressable
                accessibilityRole="button"
                onPress={() => router.replace('/apoderado')}
                className="items-center py-2"
              >
                <Text className="font-nunito-extrabold text-[13px] text-primario-claro underline">
                  Volver sin guardar
                </Text>
              </Pressable>
            )}
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

// Si la cuenta ya tiene estudiante, el formulario se abre para editarlo.
function CargarPerfil() {
  const consulta = useConsulta('estudiante-del-apoderado', api.estudianteDelApoderado);
  if (consulta.isPending) return <EstadoConsulta texto="Cargando el perfil…" esTablet={false} />;
  if (consulta.isError && !(consulta.error instanceof ErrorApi && consulta.error.estado === 404)) {
    return (
      <EstadoConsulta
        texto={consulta.error.message}
        esTablet={false}
        onReintentar={() => consulta.refetch()}
      />
    );
  }
  return <FormularioPerfil existente={consulta.data ?? null} />;
}

export default function PantallaPerfil() {
  return (
    <Protegida rol="apoderado">
      <CargarPerfil />
    </Protegida>
  );
}
