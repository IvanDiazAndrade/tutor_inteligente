import { router } from 'expo-router';
import { useMemo, useState } from 'react';
import { Pressable, ScrollView, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { GraficoSemanal } from '@/components/GraficoSemanal';
import { MedidorDominio } from '@/components/MedidorDominio';
import { Octavio } from '@/components/Octavio';
import { PISTAS_PROMEDIO_EJEMPLO, type Periodo, RESUMENES_EJEMPLO } from '@/datos/apoderado';
import { DOMINIOS_EJEMPLO, ESTUDIANTE_EJEMPLO, UNIDADES } from '@/datos/ejemplo';
import { useDistribucion } from '@/hooks/useDistribucion';
import { api } from '@/api/cliente';
import { Protegida } from '@/sesion/Protegida';
import { useSesion } from '@/sesion/SesionContext';
import { useConsulta } from '@/sesion/useConsulta';
import { banda, type Dominio, paraRepasar, type Unidad, unidadSugerida } from '@/modelo/progreso';

const PISTAS_ALTAS = 1.5;

const duracion = (minutos: number) => {
  const h = Math.floor(minutos / 60);
  const m = minutos % 60;
  if (h === 0) return `${m} min`;
  return m === 0 ? `${h} h` : `${h} h ${m} min`;
};

const minuscula = (texto: string) => texto.charAt(0).toLowerCase() + texto.slice(1);

// Comentario en lenguaje simple por unidad, por reglas (RF-DA5): nada de LLM en el panel (AD-6).
function comentarioDe(dominio: Dominio, pistas: number, hoy: Date): string {
  const b = banda(dominio.indice);
  if (b === 'Dominado') return 'Lo maneja muy bien, ya casi no necesita pistas.';
  if (pistas >= PISTAS_ALTAS) return 'Le está costando un poco: usa hartas pistas aquí.';
  if (paraRepasar(dominio, hoy)) return 'Hace más de 3 semanas que no practica este tema.';
  if (b === 'Practicando') return 'Va avanzando parejo, con práctica regular.';
  return 'Recién está partiendo con este tema, es normal ir lento.';
}

// Panel del apoderado (CU-10; mockup "Dashboard Apoderado"): resumen semanal, qué está
// aprendiendo y sugerencia de la semana. Pocos indicadores y encuadre de avance (RF-DA4, DA6).
// El nombre del estudiante viene del servidor; los indicadores siguen siendo de ejemplo hasta
// que el servicio dashboard (F4) esté disponible (tarea 65).
function Panel() {
  const { dosColumnas, esTablet: g } = useDistribucion();
  const [periodo, setPeriodo] = useState<Periodo>('esta');
  const { cerrar } = useSesion();
  const perfil = useConsulta('estudiante-del-apoderado', api.estudianteDelApoderado);
  const estudiante = { ...ESTUDIANTE_EJEMPLO, alias: perfil.data?.alias ?? '…' };
  const resumen = RESUMENES_EJEMPLO[periodo];

  const { medidores, sugerencia } = useMemo(() => {
    const hoy = new Date();
    const dominios = new Map(DOMINIOS_EJEMPLO.map((d) => [d.unidadId, d]));
    const visibles = UNIDADES.filter((u) => u.curso <= estudiante.curso);
    const iniciadas = visibles.filter((u) => u.curso === estudiante.curso && dominios.has(u.id));
    const medidores = iniciadas.map((u) => {
      const d = dominios.get(u.id)!;
      return {
        unidad: u,
        dominio: d,
        comentario: comentarioDe(d, PISTAS_PROMEDIO_EJEMPLO[u.id] ?? 0, hoy),
      };
    });
    const sugerida = unidadSugerida(visibles, dominios, hoy, estudiante.curso);
    const textoSugerencia = (u: Unidad) => {
      const d = dominios.get(u.id);
      if (!d) return `Esta semana pueden empezar con ${minuscula(u.ciudadana)}.`;
      if (paraRepasar(d, hoy)) return `Esta semana conviene repasar ${minuscula(u.ciudadana)}.`;
      return `Esta semana conviene practicar ${minuscula(u.ciudadana)}.`;
    };
    return { medidores, sugerencia: sugerida && textoSugerencia(sugerida) };
  }, [estudiante.curso]);

  const minutos = resumen.minutosPorDia.reduce((a, b) => a + b, 0);
  const dias = resumen.minutosPorDia.filter((m) => m > 0).length;
  const deCadaDiez = resumen.ejercicios
    ? Math.round((resumen.correctos / resumen.ejercicios) * 10)
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
        {indicador(String(resumen.ejercicios), 'ejercicios resueltos')}
        {indicador(`${deCadaDiez} de 10`, 'ejercicios correctos')}
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
      {medidores.map(({ unidad, dominio, comentario }) => (
        <MedidorDominio
          key={unidad.id}
          descripcion={unidad.ciudadana}
          indice={dominio.indice}
          banda={banda(dominio.indice)}
          comentario={comentario}
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
        <View className="rounded-xl border-[1.5px] border-ambar-borde bg-ambar-fondo px-3 py-2">
          <Text className={`font-nunito-bold text-ambar ${g ? 'text-base' : 'text-xs'}`}>
            Vista previa: los indicadores son de ejemplo hasta conectar el panel (tarea 65).
          </Text>
        </View>
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
