import { router } from 'expo-router';
import { Children, type ReactNode } from 'react';
import { Pressable, ScrollView, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import Svg, { Path } from 'react-native-svg';

import { Octavio } from '@/components/Octavio';
import { useDistribucion } from '@/hooks/useDistribucion';

// Contenedor de las pantallas de las pestañas del estudiante: fondo, márgenes y ancho máximo.
// La barra de pestañas queda abajo, fuera del desplazamiento.
export function PantallaEstudiante({ children }: { children: ReactNode }) {
  const { esTablet } = useDistribucion();
  return (
    <SafeAreaView edges={['top', 'left', 'right']} className="flex-1 bg-panel">
      <ScrollView
        contentContainerClassName={`w-full self-center pb-6 ${
          esTablet ? 'max-w-[960px] gap-5 px-6 pt-5' : 'max-w-[720px] gap-4 px-4 pt-3'
        }`}
      >
        {children}
      </ScrollView>
    </SafeAreaView>
  );
}

// Título grande de una pantalla de lista ("Lecciones", "Ejercicios", "Mi perfil").
export function TituloPantalla({ titulo, subtitulo }: { titulo: string; subtitulo?: string }) {
  const { esTablet } = useDistribucion();
  return (
    <View className="gap-0.5 px-1">
      <Text className={`font-nunito-black text-tinta ${esTablet ? 'text-4xl' : 'text-[28px]'}`}>
        {titulo}
      </Text>
      {subtitulo && (
        <Text className={`font-nunito-bold text-lila ${esTablet ? 'text-lg' : 'text-sm'}`}>
          {subtitulo}
        </Text>
      )}
    </View>
  );
}

// Encabezado del detalle: botón para volver a la lista, título y una línea divisoria.
export function EncabezadoDetalle({
  antetitulo,
  titulo,
  alVolver,
  derecha,
}: {
  antetitulo: string;
  titulo: string;
  alVolver: () => void;
  derecha?: ReactNode;
}) {
  const { esTablet: g } = useDistribucion();
  return (
    <View className="gap-3">
      <View className="flex-row items-center gap-3">
        <Pressable
          accessibilityRole="button"
          accessibilityLabel="Volver a la lista"
          onPress={alVolver}
          className={`items-center justify-center rounded-[14px] border-2 border-borde bg-white active:border-primario-claro active:bg-lila-fondo ${
            g ? 'h-14 w-14' : 'h-11 w-11'
          }`}
        >
          <Svg width={g ? 24 : 18} height={g ? 24 : 18} viewBox="0 0 18 18">
            <Path
              d="M11.5 3.5 L6 9 L11.5 14.5"
              fill="none"
              stroke="#6D28D9"
              strokeWidth={2.6}
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </Svg>
        </Pressable>
        <View className="flex-1">
          <Text
            className={`font-nunito-black uppercase tracking-wide text-primario-claro ${
              g ? 'text-sm' : 'text-xs'
            }`}
          >
            {antetitulo}
          </Text>
          <Text className={`font-nunito-black text-tinta ${g ? 'text-3xl' : 'text-[22px]'}`}>
            {titulo}
          </Text>
        </View>
        {derecha}
      </View>
      <View className="h-[1.5px] bg-borde" />
    </View>
  );
}

// Vuelve a la lista de la misma pestaña. No se usa router.back(): si el detalle se abrió desde
// otra pestaña (p. ej. "Practicar esta lección"), back() volvería a esa otra pestaña.
export function volverALista(lista: '/estudiante/lecciones' | '/estudiante/ejercicios') {
  router.dismissTo(lista);
}

// Lista de tarjetas: una columna en teléfono vertical, dos en tablet o en horizontal.
export function Rejilla({ children }: { children: ReactNode }) {
  const { esTablet, dosColumnas } = useDistribucion();
  if (!esTablet && !dosColumnas) return <View className="gap-3">{children}</View>;
  return (
    <View className="flex-row flex-wrap justify-between gap-y-3">
      {Children.map(children, (hijo) => hijo && <View className="w-[49%]">{hijo}</View>)}
    </View>
  );
}

// Enlace de texto (p. ej. para ver las unidades de cursos anteriores).
export function Enlace({ texto, onPress }: { texto: string; onPress: () => void }) {
  const { esTablet } = useDistribucion();
  return (
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
}

// Carga o error, con Octavio y un botón para reintentar.
export function EstadoCarga({ texto, onReintentar }: { texto: string; onReintentar?: () => void }) {
  const { esTablet } = useDistribucion();
  return (
    <SafeAreaView
      edges={['top', 'left', 'right']}
      className="flex-1 items-center justify-center gap-4 bg-panel p-6"
    >
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
