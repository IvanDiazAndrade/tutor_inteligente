import { router, useLocalSearchParams } from 'expo-router';
import { useEffect, useState } from 'react';
import { AccessibilityInfo, Pressable, ScrollView, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import Svg, { Path } from 'react-native-svg';

import { BotonesVoz } from '@/components/BotonesVoz';
import { BotonPrimario } from '@/components/BotonPrimario';
import { cuantasPalabras, EnunciadoResaltado } from '@/components/EnunciadoResaltado';
import { EstadoConsulta } from '@/components/EstadoConsulta';
import { Octavio } from '@/components/Octavio';
import { OctavioHablando } from '@/components/OctavioHablando';
import { useDistribucion } from '@/hooks/useDistribucion';
import { Protegida } from '@/sesion/Protegida';
import { nombreLeccion, useContenidoEstudiante } from '@/sesion/useContenidoEstudiante';
import { useVoz } from '@/voz/useVoz';

const MS_POR_PALABRA = 110;
const MS_POR_PALABRA_CON_VOZ = 340; // al ritmo de la voz; al terminar se muestra todo

// Une con espacios no separables las operaciones cortas ("24 : 6 = 4"), para que no queden
// cortadas entre dos líneas. Las largas se dejan, porque no cabrían en una.
const sinCortes = (texto: string) =>
  texto.replace(/[\d.,/]+(?: [:×+−=] [\d.,/]+)+/g, (operacion) =>
    operacion.length <= 16 ? operacion.replace(/ /g, '\u00A0') : operacion,
  );

// Lección de una unidad (RF-D9): Octavio explica una parte a la vez y el niño avanza con
// "Siguiente". Al terminar, invita a los ejercicios. Los textos vienen del servidor.
function PantallaLeccion() {
  const { unidad } = useLocalSearchParams<{ unidad: string }>();
  const { dosColumnas, esTablet: g } = useDistribucion();
  const c = useContenidoEstudiante();
  const [paso, setPaso] = useState(0);
  const [dichas, setDichas] = useState(0); // palabras que Octavio ya dijo de este paso
  const [sinAnimar, setSinAnimar] = useState(false);
  const [vez, setVez] = useState(0); // cambia al pedir que repita
  const { activa: vozActiva, hablando: suena, alternar: alternarVoz, decir } = useVoz();

  const leccion = c.listo ? c.leccion(unidad) : undefined;
  const partes = leccion?.partes ?? [];
  const disponible = (c.listo && c.porUnidad.get(unidad)?.conEjercicios) || false;
  const esCierre = paso >= partes.length;
  const texto = !leccion
    ? ''
    : !esCierre
      ? sinCortes(partes[paso].explicacion)
      : disponible
        ? '¡Muy bien! Ya terminaste la lección. Practiquemos lo que aprendiste.'
        : '¡Muy bien! Ya terminaste la lección. Todavía estoy preparando los ejercicios de esta unidad.';
  const total = cuantasPalabras(texto);
  // Con voz, Octavio dice primero el título de la parte: el texto aparece después.
  const titulo = esCierre ? '' : partes[paso].titulo;
  const espera = vozActiva && titulo ? cuantasPalabras(titulo) : 0;
  const visibles = sinAnimar ? total : Math.max(0, Math.min(dichas - espera, total));
  const apareciendo = visibles < total;
  const textoVoz = titulo ? `${titulo}. ${texto}` : texto;

  useEffect(() => {
    let activa = true;
    AccessibilityInfo.isReduceMotionEnabled().then((si) => activa && setSinAnimar(si));
    return () => {
      activa = false;
    };
  }, []);

  useEffect(() => {
    if (!apareciendo || vozActiva === null) return;
    const reloj = setInterval(
      () => setDichas((n) => n + 1),
      vozActiva ? MS_POR_PALABRA_CON_VOZ : MS_POR_PALABRA,
    );
    return () => clearInterval(reloj);
  }, [apareciendo, vozActiva, paso]);

  // Lee la parte en voz alta; al cambiar de parte, silenciar o salir, se calla.
  useEffect(() => {
    if (!vozActiva || !textoVoz) return;
    return decir(textoVoz, () => setDichas(Infinity));
  }, [vozActiva, textoVoz, vez, decir]);

  if (!c.listo) {
    return (
      <EstadoConsulta
        texto={c.error ? c.error.message : 'Octavio está preparando la lección…'}
        esTablet={g}
        onReintentar={c.error ? c.reintentar : undefined}
      />
    );
  }

  const irA = (nuevo: number) => {
    setPaso(nuevo);
    setDichas(0);
  };
  // Reemplaza la lección: al volver del ejercicio se llega al inicio.
  const practicar = () => router.replace({ pathname: '/ejercicio', params: { unidad } });

  if (!leccion) {
    return (
      <SafeAreaView className="flex-1 items-center justify-center gap-4 bg-panel p-6">
        <Octavio tamano={g ? 120 : 88} conVarita />
        <Text className="text-center font-nunito-bold text-base text-apagado-oscuro">
          Esta unidad todavía no tiene lección.
        </Text>
        <View className="w-full max-w-[420px]">
          <BotonPrimario
            titulo={disponible ? 'Ir a los ejercicios →' : 'Volver'}
            onPress={disponible ? practicar : () => router.back()}
            grande={g}
          />
        </View>
      </SafeAreaView>
    );
  }

  const encabezado = (
    <View className="gap-3">
      <View className="flex-row items-center gap-3">
        <Pressable
          accessibilityRole="button"
          accessibilityLabel="Volver"
          onPress={() => router.back()}
          className={`items-center justify-center rounded-[14px] bg-white active:bg-fondo ${
            g ? 'h-14 w-14' : 'h-11 w-11'
          }`}
        >
          <Svg width={g ? 24 : 20} height={g ? 24 : 20} viewBox="0 0 18 18">
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
          <Text className={`font-nunito-bold text-lila ${g ? 'text-base' : 'text-xs'}`}>
            {nombreLeccion(leccion, c.estudiante.curso)}
          </Text>
          <Text className={`font-nunito-black text-tinta ${g ? 'text-3xl' : 'text-xl'}`}>
            {leccion.titulo}
          </Text>
        </View>
        {disponible && !esCierre && (
          <Pressable
            accessibilityRole="button"
            accessibilityLabel="Saltar la lección e ir a los ejercicios"
            onPress={practicar}
            className={`rounded-full border-[1.5px] border-nueva-borde bg-white active:bg-fondo ${
              g ? 'px-5 py-3' : 'px-3.5 py-2.5'
            }`}
          >
            <Text
              className={`font-nunito-extrabold text-primario ${g ? 'text-base' : 'text-[13px]'}`}
            >
              Ejercicios
            </Text>
          </Pressable>
        )}
      </View>
      <View
        accessible
        accessibilityRole="progressbar"
        accessibilityLabel={
          esCierre ? 'Lección terminada' : `Parte ${paso + 1} de ${partes.length}`
        }
        className="flex-row gap-1.5"
      >
        {partes.map((parte, i) => (
          <View
            key={parte.titulo}
            className={`flex-1 rounded-full ${g ? 'h-3' : 'h-2'} ${
              i <= paso ? 'bg-dorado' : 'bg-lila-fondo'
            }`}
          />
        ))}
      </View>
    </View>
  );

  // Tocar el globo muestra de una vez todo lo que falta por aparecer.
  const globo = (
    <Pressable
      accessibilityRole="text"
      onPress={() => setDichas(Infinity)}
      className={`rounded-[24px] border-2 border-globo bg-white ${g ? 'gap-4 p-8' : 'gap-2.5 p-5'}`}
    >
      <View className="flex-row items-center gap-2">
        <Text
          className={`flex-1 font-nunito-black uppercase tracking-wide text-primario-claro ${
            g ? 'text-base' : 'text-[13px]'
          }`}
        >
          {esCierre ? '¡Lección terminada!' : `Parte ${paso + 1} de ${partes.length}`}
        </Text>
        <BotonesVoz
          activa={vozActiva}
          onAlternar={alternarVoz}
          onRepetir={() => setVez((n) => n + 1)}
          grande={g}
        />
      </View>
      {!esCierre && (
        <Text className={`font-nunito-black text-tinta ${g ? 'text-3xl' : 'text-2xl'}`}>
          {partes[paso].titulo}
        </Text>
      )}
      <EnunciadoResaltado texto={texto} grande={g} visibles={visibles} />
      <View
        pointerEvents="none"
        className={`absolute h-5 w-5 rotate-45 border-globo bg-white ${
          dosColumnas ? '-left-[11px] bottom-10 border-b-2 border-l-2' : ''
        } ${dosColumnas ? '' : '-bottom-[11px] left-1/2 -ml-2.5 border-b-2 border-r-2'}`}
      />
    </Pressable>
  );

  const octavio = (
    <View className="items-center">
      <OctavioHablando
        tamano={g ? 240 : dosColumnas ? 150 : 170}
        hablando={suena || apareciendo}
        conVarita={!esCierre}
        tutor={esCierre}
        guino={esCierre}
      />
    </View>
  );

  const botones = (
    <View className={`flex-row gap-3 ${g ? 'w-full max-w-[640px] self-center' : ''}`}>
      {paso > 0 && (
        <Pressable
          accessibilityRole="button"
          onPress={() => irA(paso - 1)}
          className={`items-center justify-center rounded-2xl border-2 border-lila-suave bg-white active:bg-fondo ${
            g ? 'h-16 px-7' : 'h-14 px-5'
          }`}
        >
          <Text className={`font-nunito-black text-primario ${g ? 'text-xl' : 'text-base'}`}>
            ← Anterior
          </Text>
        </Pressable>
      )}
      <View className="flex-1">
        <BotonPrimario
          titulo={!esCierre ? 'Siguiente →' : disponible ? '¡A practicar!' : 'Volver al inicio'}
          onPress={!esCierre ? () => irA(paso + 1) : disponible ? practicar : () => router.back()}
          grande={g}
        />
      </View>
    </View>
  );

  return (
    <SafeAreaView className="flex-1 bg-panel">
      <View className={`flex-1 gap-3 pb-3 pt-2 ${g ? 'px-8' : 'px-4'}`}>
        {encabezado}
        {dosColumnas ? (
          <View className="flex-1 flex-row items-center gap-5">
            {octavio}
            <ScrollView
              className="flex-1"
              contentContainerClassName="grow justify-center py-2 pl-3"
            >
              {globo}
            </ScrollView>
          </View>
        ) : (
          // En el teléfono vertical el globo va arriba y Octavio habla desde abajo.
          <ScrollView
            className="flex-1"
            contentContainerClassName={`grow justify-center gap-5 py-2 ${
              g ? 'w-full max-w-[760px] self-center' : ''
            }`}
          >
            {globo}
            {octavio}
          </ScrollView>
        )}
        {botones}
      </View>
    </SafeAreaView>
  );
}

export default function Leccion() {
  return (
    <Protegida rol="estudiante">
      <PantallaLeccion />
    </Protegida>
  );
}
