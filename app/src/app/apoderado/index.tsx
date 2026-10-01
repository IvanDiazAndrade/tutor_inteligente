import { Redirect, router } from 'expo-router';
import { useState } from 'react';
import { Pressable, ScrollView, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { api, ErrorApi } from '@/api/cliente';
import { EstadoConsulta } from '@/components/EstadoConsulta';
import { GraficoSemanal } from '@/components/GraficoSemanal';
import { MedidorDominio } from '@/components/MedidorDominio';
import { Octavio } from '@/components/Octavio';
import { useDistribucion } from '@/hooks/useDistribucion';
import { Protegida } from '@/sesion/Protegida';
import { useSesion } from '@/sesion/SesionContext';
import { useConsulta } from '@/sesion/useConsulta';

type Periodo = 'esta' | 'pasada';

const duracion = (minutos: number) => {
  const h = Math.floor(minutos / 60);
  const m = minutos % 60;
  if (h === 0) return `${m} min`;
  return m === 0 ? `${h} h` : `${h} h ${m} min`;
};

// Panel del apoderado (CU-10, F4): resumen semanal, qué está aprendiendo y sugerencia de la
// semana. Pocos indicadores y encuadre de avance (RF-DA4, DA6). Todo viene calculado del
// servidor por reglas, sin LLM (AD-6): la app solo lo muestra.
function Panel() {
  const { dosColumnas, esTablet: g } = useDistribucion();
  const [periodo, setPeriodo] = useState<Periodo>('esta');
  const { cerrar } = useSesion();
  const consulta = useConsulta('panel-apoderado', api.panelApoderado);

  if (consulta.isPending) {
    return <EstadoConsulta texto="Octavio está reuniendo el avance…" esTablet={g} />;
  }
  if (consulta.error instanceof ErrorApi && consulta.error.estado === 404) {
    // La cuenta todavía no tiene estudiante: primero se crea su perfil (CU-9).
    return <Redirect href="/apoderado/perfil" />;
  }
  if (consulta.isError) {
    return (
      <EstadoConsulta
        texto={consulta.error.message}
        esTablet={g}
        onReintentar={() => consulta.refetch()}
      />
    );
  }

  const panel = consulta.data;
  const estudiante = { alias: panel.alias };
  const resumen = periodo === 'esta' ? panel.estaSemana : panel.semanaPasada;
  const { medidores, sugerencia } = panel;
  const minutos = resumen.minutosPorDia.reduce((a, b) => a + b, 0);
  const dias = resumen.minutosPorDia.filter((m) => m > 0).length;
  const deCadaDiez = resumen.respuestas
    ? Math.round((resumen.correctas / resumen.respuestas) * 10)
    : 0;

  const tituloTarjeta = (texto: string) => (
    <Text
      className={`font-nunito-black uppercase tracking-wider text-seccion ${g ? 'text-sm' : 'text-xs'}`}
    >
      {texto}
    </Text>
  );

  const indicador = (valor: string, etiqueta: string) => (
    <View className="w-[48%]">
      <Text className={`font-nunito-black text-tinta ${g ? 'text-3xl' : 'text-xl'}`}>{valor}</Text>
      <Text className={`font-nunito-bold text-apagado-oscuro ${g ? 'text-base' : 'text-xs'}`}>
        {etiqueta}
      </Text>
    </View>
  );

  const encabezado = (
    <View className="gap-3">
      <View className="flex-row items-end justify-between gap-3">
        <View className="flex-1">
          <Text className={`font-nunito-bold text-seccion ${g ? 'text-base' : 'text-xs'}`}>
            Modo apoderado
          </Text>
          <Text className={`font-nunito-black text-tinta ${g ? 'text-3xl' : 'text-[21px]'}`}>
            Progreso de {estudiante.alias}
          </Text>
        </View>
      </View>
      <View
        accessibilityRole="radiogroup"
        className="flex-row self-start rounded-xl border-[1.5px] border-borde bg-white p-1"
      >
        {(['esta', 'pasada'] as const).map((p) => (
          <Pressable
            key={p}
            accessibilityRole="radio"
            accessibilityState={{ selected: periodo === p }}
            onPress={() => setPeriodo(p)}
            className={`rounded-lg px-3.5 py-2 ${periodo === p ? 'bg-primario' : ''}`}
          >
            <Text
              className={`font-nunito-extrabold ${g ? 'text-base' : 'text-[13px]'} ${
                periodo === p ? 'text-white' : 'text-tinta-tecla'
              }`}
            >
              {p === 'esta' ? 'Esta semana' : 'Semana pasada'}
            </Text>
          </Pressable>
        ))}
      </View>
    </View>
  );

  const tarjetaResumen = (
    <View className={`rounded-[20px] bg-white ${g ? 'gap-4 p-6' : 'gap-3 p-4'}`}>
      {tituloTarjeta('Resumen semanal')}
      <View className="flex-row flex-wrap justify-between gap-y-3">
        {indicador(String(resumen.ejercicios), 'ejercicios practicados')}
        {indicador(resumen.respuestas ? `${deCadaDiez} de 10` : '—', 'respuestas correctas')}
        {indicador(duracion(minutos), 'de práctica')}
        {indicador(
          `${dias} ${dias === 1 ? 'día' : 'días'}`,
          periodo === 'esta' ? 'practicó esta semana' : 'practicó la semana pasada',
        )}
      </View>
      <View className="border-t-[1.5px] border-banda-riel pt-3">
        <GraficoSemanal minutosPorDia={resumen.minutosPorDia} grande={g} />
      </View>
    </View>
  );

  const tarjetaAprendiendo = (
    <View className={`rounded-[20px] bg-white ${g ? 'gap-5 p-6' : 'gap-3.5 p-4'}`}>
      {tituloTarjeta('Qué está aprendiendo')}
      {medidores.length === 0 && (
        <Text className={`font-nunito-bold text-apagado-oscuro ${g ? 'text-base' : 'text-[13px]'}`}>
          Cuando {estudiante.alias} practique, aquí verás cómo avanza en cada tema.
        </Text>
      )}
      {medidores.map((m) => (
        <MedidorDominio
          key={m.unidadId}
          descripcion={m.descripcion}
          indice={m.indice}
          banda={m.banda}
          comentario={m.comentario}
          grande={g}
        />
      ))}
    </View>
  );

  const tarjetaSugerencia = sugerencia && (
    <View
      className={`flex-row items-start gap-3 rounded-[20px] border-[1.5px] border-nueva-borde bg-fondo ${
        g ? 'p-6' : 'p-3.5'
      }`}
    >
      <Octavio tamano={g ? 72 : 50} />
      <View className="flex-1 gap-1">
        <Text
          className={`font-nunito-black uppercase tracking-wider text-primario ${g ? 'text-sm' : 'text-xs'}`}
        >
          Sugerencia de la semana
        </Text>
        <Text
          className={`font-nunito-bold text-tinta-tecla ${g ? 'text-lg leading-7' : 'text-[13px] leading-5'}`}
        >
          {sugerencia} Practicar 10 minutos, 2 o 3 veces por semana, ayuda más que una sesión larga.
        </Text>
      </View>
    </View>
  );

  const pie = (
    <View className="items-center gap-2 pt-1">
      <Text className={`text-center font-nunito text-apagado ${g ? 'text-sm' : 'text-[11px]'}`}>
        🔒 Ves indicadores del avance de {estudiante.alias}. Las conversaciones con el tutor son
        privadas.
      </Text>
      <Pressable
        accessibilityRole="button"
        onPress={() => cerrar().then(() => router.replace('/'))}
        className="py-2"
      >
        <Text
          className={`font-nunito-extrabold text-primario-claro underline ${g ? 'text-base' : 'text-[13px]'}`}
        >
          Cerrar sesión
        </Text>
      </Pressable>
    </View>
  );

  return (
    <SafeAreaView className="flex-1 bg-panel">
      <ScrollView
        contentContainerClassName={`gap-3 pb-4 pt-2 ${g ? 'gap-5 px-8' : 'px-4'} ${
          !dosColumnas && g ? 'w-full max-w-[760px] self-center' : ''
        }`}
      >
        {encabezado}
        {dosColumnas ? (
          <View className={`flex-row items-start ${g ? 'gap-5' : 'gap-3'}`}>
            <View className={`flex-1 ${g ? 'gap-5' : 'gap-3'}`}>
              {tarjetaResumen}
              {tarjetaSugerencia}
            </View>
            <View className="flex-1">{tarjetaAprendiendo}</View>
          </View>
        ) : (
          <>
            {tarjetaResumen}
            {tarjetaAprendiendo}
            {tarjetaSugerencia}
          </>
        )}
        {pie}
      </ScrollView>
    </SafeAreaView>
  );
}

export default function PanelApoderado() {
  return (
    <Protegida rol="apoderado">
      <Panel />
    </Protegida>
  );
}
