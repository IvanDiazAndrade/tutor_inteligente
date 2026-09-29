import { router } from 'expo-router';
import { useMemo, useState } from 'react';
import { Pressable, ScrollView, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import type { TipoEtiqueta } from '@/components/Etiqueta';
import { Octavio } from '@/components/Octavio';
import { SugerenciaOctavio } from '@/components/SugerenciaOctavio';
import { TarjetaUnidad } from '@/components/TarjetaUnidad';
import {
  DOMINIOS_EJEMPLO,
  ESTUDIANTE_EJEMPLO,
  PUNTOS_EJEMPLO,
  RACHA_DIAS_EJEMPLO,
  UNIDADES,
} from '@/datos/ejemplo';
import { useDistribucion } from '@/hooks/useDistribucion';
import { estrellas, paraRepasar, type Unidad, unidadSugerida } from '@/modelo/progreso';

const conPuntoDeMiles = (n: number) => String(n).replace(/\B(?=(\d{3})+(?!\d))/g, '.');

// Home del estudiante (CU-2, CU-6; mockup "Home Estudiante"): saludo, puntos y racha,
// unidad sugerida y mapa de unidades de su curso; las de cursos anteriores se abren aparte.
export default function HomeEstudiante() {
  const { dosColumnas, esTablet } = useDistribucion();
  const [verAnteriores, setVerAnteriores] = useState(false);
  const estudiante = ESTUDIANTE_EJEMPLO;

  const { delCurso, anteriores, dominios, sugerida, primeraNueva, hoy } = useMemo(() => {
    const hoy = new Date();
    const dominios = new Map(DOMINIOS_EJEMPLO.map((d) => [d.unidadId, d]));
    // El estudiante ve su curso y los anteriores, nunca los superiores (modelo_estudiante.md §5).
    const visibles = UNIDADES.filter((u) => u.curso <= estudiante.curso);
    const delCurso = visibles.filter((u) => u.curso === estudiante.curso);
    return {
      hoy,
      dominios,
      delCurso,
      anteriores: visibles.filter((u) => u.curso < estudiante.curso),
      sugerida: unidadSugerida(visibles, dominios, hoy),
      primeraNueva: delCurso.find((u) => !dominios.has(u.id)),
    };
  }, [estudiante.curso]);

  const etiquetaDe = (u: Unidad): TipoEtiqueta | undefined => {
    const d = dominios.get(u.id);
    if (paraRepasar(d, hoy)) return 'repasar';
    if (estrellas(d) === 3) return 'dominada';
    if (u.id === primeraNueva?.id) return 'nueva';
    return undefined;
  };

  const practicar = (u: Unidad) =>
    router.push({ pathname: '/ejercicio', params: { unidad: u.id, nombre: u.nombre } });

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
      <View className="items-end gap-1.5">
        <View className="rounded-full bg-white px-3 py-1.5">
          <Text
            className={`font-nunito-black text-ambar ${esTablet ? 'text-base' : 'text-[13px]'}`}
          >
            ⭐ {conPuntoDeMiles(PUNTOS_EJEMPLO)}
          </Text>
        </View>
        <View className="rounded-full border-[1.5px] border-ambar-borde bg-ambar-fondo px-3 py-1">
          <Text
            className={`font-nunito-extrabold text-ambar ${esTablet ? 'text-base' : 'text-xs'}`}
          >
            🔥 {RACHA_DIAS_EJEMPLO} días
          </Text>
        </View>
      </View>
    </View>
  );

  const sugerencia = sugerida && (
    <SugerenciaOctavio
      nombre={sugerida.nombre}
      etiqueta={etiquetaDe(sugerida) === 'repasar' ? 'repasar' : undefined}
      onPracticar={() => practicar(sugerida)}
      grande={esTablet}
      apilada={dosColumnas && !esTablet}
    />
  );

  const listaUnidades = (unidades: Unidad[]) => (
    <View className={esTablet ? 'flex-row flex-wrap gap-3' : 'gap-2.5'}>
      {unidades.map((u) => (
        <View key={u.id} className={esTablet ? 'w-[48.5%]' : ''}>
          <TarjetaUnidad
            nombre={u.nombre}
            estrellas={estrellas(dominios.get(u.id))}
            etiqueta={etiquetaDe(u)}
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

  const unidades = (
    <View className="gap-3">
      {tituloSeccion(`Tus unidades · ${estudiante.curso}° básico`)}
      {listaUnidades(delCurso)}
      {anteriores.length > 0 &&
        enlace(
          verAnteriores
            ? `Ocultar unidades de ${estudiante.curso - 1}° básico`
            : `Ver unidades de ${estudiante.curso - 1}° básico`,
          () => setVerAnteriores((v) => !v),
        )}
      {verAnteriores && (
        <View className="gap-3">
          {tituloSeccion(`Repaso · ${estudiante.curso - 1}° básico`)}
          {listaUnidades(anteriores)}
        </View>
      )}
    </View>
  );

  const salir = enlace('Cambiar de perfil', () => router.replace('/'));

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
            <ScrollView contentContainerClassName="pb-4">{unidades}</ScrollView>
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
          {unidades}
          {salir}
        </ScrollView>
      )}
    </SafeAreaView>
  );
}
