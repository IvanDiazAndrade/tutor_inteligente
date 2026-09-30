import { router } from 'expo-router';
import { useState } from 'react';
import { Pressable, ScrollView, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { api, type UnidadEstudiante } from '@/api/cliente';
import { Octavio } from '@/components/Octavio';
import { SugerenciaOctavio } from '@/components/SugerenciaOctavio';
import { TarjetaUnidad } from '@/components/TarjetaUnidad';
import { useDistribucion } from '@/hooks/useDistribucion';
import { useSesion } from '@/sesion/SesionContext';
import { useConsulta } from '@/sesion/useConsulta';

const conPuntoDeMiles = (n: number) => String(n).replace(/\B(?=(\d{3})+(?!\d))/g, '.');

// Home del estudiante (CU-2, CU-6; mockup "Home Estudiante"): saludo, puntos, unidad sugerida
// y mapa de unidades de su curso; las de cursos anteriores se abren aparte. Estrellas,
// etiquetas y sugerencia las calcula el servidor (GET /estudiante/unidades).
export default function HomeEstudiante() {
  const { dosColumnas, esTablet } = useDistribucion();
  const { cerrar } = useSesion();
  const [verAnteriores, setVerAnteriores] = useState(false);
  const perfil = useConsulta('perfil-estudiante', api.perfilEstudiante);
  const unidades = useConsulta('unidades', api.unidades);

  if (perfil.isPending || unidades.isPending) {
    return <Estado texto="Octavio está preparando tus unidades…" esTablet={esTablet} />;
  }
  if (perfil.isError || unidades.isError) {
    return (
      <Estado
        texto={(perfil.error ?? unidades.error)?.message ?? 'Algo salió mal.'}
        esTablet={esTablet}
        onReintentar={() => {
          perfil.refetch();
          unidades.refetch();
        }}
      />
    );
  }

  const estudiante = perfil.data;
  const delCurso = unidades.data.filter((u) => u.curso === estudiante.curso);
  const anteriores = unidades.data.filter((u) => u.curso < estudiante.curso);
  const sugerida = unidades.data.find((u) => u.sugerida);

  const practicar = (u: UnidadEstudiante) =>
    router.push({ pathname: '/ejercicio', params: { unidad: u.id, nombre: u.descripcion } });

  const encabezado = (
    <View className="flex-row items-center gap-2.5">
      <Octavio tamano={esTablet ? 88 : 62} />
      <View className="flex-1">
        <Text className={`font-nunito-black text-tinta ${esTablet ? 'text-3xl' : 'text-[22px]'}`}>
          ¡Hola, {estudiante.alias}!
        </Text>
        <Text className={`font-nunito-bold text-lila ${esTablet ? 'text-base' : 'text-xs'}`}>
          ¿Practicamos un poco hoy?
        </Text>
      </View>
      <View className="rounded-full bg-white px-3 py-1.5">
        <Text className={`font-nunito-black text-ambar ${esTablet ? 'text-base' : 'text-[13px]'}`}>
          ⭐ {conPuntoDeMiles(estudiante.puntajeTotal)}
        </Text>
      </View>
    </View>
  );

  const sugerencia = sugerida && (
    <SugerenciaOctavio
      nombre={sugerida.descripcion}
      etiqueta={sugerida.etiqueta === 'repasar' ? 'repasar' : undefined}
      onPracticar={() => practicar(sugerida)}
      grande={esTablet}
      apilada={dosColumnas && !esTablet}
    />
  );

  const listaUnidades = (lista: UnidadEstudiante[]) => (
    <View className={esTablet ? 'flex-row flex-wrap gap-3' : 'gap-2.5'}>
      {lista.map((u) => (
        <View key={u.id} className={esTablet ? 'w-[48.5%]' : ''}>
          <TarjetaUnidad
            nombre={u.descripcion}
            estrellas={u.estrellas}
            etiqueta={u.etiqueta ?? undefined}
            onPress={() => practicar(u)}
            grande={esTablet}
          />
        </View>
      ))}
    </View>
  );

  const tituloSeccion = (texto: string) => (
    <Text
      className={`px-1 font-nunito-black uppercase tracking-wide text-seccion ${
        esTablet ? 'text-base' : 'text-[13px]'
      }`}
    >
      {texto}
    </Text>
  );

  const enlace = (texto: string, onPress: () => void) => (
    <Pressable accessibilityRole="link" onPress={onPress} className="items-center py-2">
      <Text
        className={`font-nunito-extrabold text-primario-claro underline ${
          esTablet ? 'text-base' : 'text-[13px]'
        }`}
      >
        {texto}
      </Text>
    </Pressable>
  );

  const mapa = (
    <View className="gap-3">
      {tituloSeccion(`Tus unidades · ${estudiante.curso}° básico`)}
      {listaUnidades(delCurso)}
      {anteriores.length > 0 &&
        enlace(
          verAnteriores
            ? 'Ocultar unidades de cursos anteriores'
            : 'Ver unidades de cursos anteriores',
          () => setVerAnteriores((v) => !v),
        )}
      {verAnteriores && (
        <View className="gap-3">
          {tituloSeccion('Repaso · cursos anteriores')}
          {listaUnidades(anteriores)}
        </View>
      )}
    </View>
  );

  const salir = enlace('Cambiar de perfil', () => cerrar().then(() => router.replace('/')));

  return (
    <SafeAreaView edges={['top', 'left', 'right']} className="flex-1 bg-panel">
      {dosColumnas ? (
        <View className="flex-1 flex-row gap-5 px-5 pt-3">
          <View className={esTablet ? 'flex-[2]' : 'flex-1'}>
            <ScrollView contentContainerClassName="gap-5 pb-4">
              {encabezado}
              {sugerencia}
              {salir}
            </ScrollView>
          </View>
          <View className={esTablet ? 'flex-[3]' : 'flex-1'}>
            <ScrollView contentContainerClassName="pb-4">{mapa}</ScrollView>
          </View>
        </View>
      ) : (
        <ScrollView
          contentContainerClassName={`gap-4 px-4 pb-4 pt-3 ${
            esTablet ? 'w-full max-w-[760px] self-center' : ''
          }`}
        >
          {encabezado}
          {sugerencia}
          {mapa}
          {salir}
        </ScrollView>
      )}
    </SafeAreaView>
  );
}

// Carga o error, con Octavio y un botón para reintentar.
function Estado({
  texto,
  esTablet,
  onReintentar,
}: {
  texto: string;
  esTablet: boolean;
  onReintentar?: () => void;
}) {
  return (
    <SafeAreaView className="flex-1 items-center justify-center gap-4 bg-panel p-6">
      <Octavio tamano={esTablet ? 120 : 88} conVarita />
      <Text
        className={`text-center font-nunito-bold text-apagado-oscuro ${esTablet ? 'text-lg' : 'text-base'}`}
      >
        {texto}
      </Text>
      {onReintentar && (
        <Pressable
          onPress={onReintentar}
          className="rounded-full bg-primario px-6 py-3 active:bg-primario-oscuro"
        >
          <Text className="font-nunito-black text-white">Reintentar</Text>
        </Pressable>
      )}
    </SafeAreaView>
  );
}
