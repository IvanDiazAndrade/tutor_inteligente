import { ScrollView, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { api } from '@/api/cliente';
import { EstadoConsulta } from '@/components/EstadoConsulta';
import { Estrellas } from '@/components/Estrellas';
import { Octavio } from '@/components/Octavio';
import { useDistribucion } from '@/hooks/useDistribucion';
import { useConsulta } from '@/sesion/useConsulta';

const conPuntoDeMiles = (n: number) => String(n).replace(/\B(?=(\d{3})+(?!\d))/g, '.');

// "Mis logros" (CU-6; RF-G1–G4): puntos, marca de la semana, estrellas e insignias propias.
// Solo progreso personal: no hay rankings ni comparación con otros niños (RF-G3). Todo lo
// calcula el servidor (GET /estudiante/progreso).
export default function Logros() {
  const { dosColumnas, esTablet: g } = useDistribucion();
  const rejilla = dosColumnas || g;
  const consulta = useConsulta('progreso', api.progreso);

  if (consulta.isPending) {
    return <EstadoConsulta texto="Octavio está contando tus logros…" esTablet={g} />;
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

  const p = consulta.data;
  const marca = p.mejorSemanaAnterior;
  const avance = marca > 0 ? Math.min(1, p.puntosSemana / marca) : p.puntosSemana > 0 ? 1 : 0;

  const cifra = (icono: string, valor: string, etiqueta: string) => (
    <View className="flex-1 items-center rounded-[22px] bg-white px-1.5 py-4">
      <Text className={g ? 'text-5xl' : 'text-4xl'} accessibilityElementsHidden>
        {icono}
      </Text>
      <Text
        numberOfLines={1}
        adjustsFontSizeToFit
        className={`font-nunito-black text-tinta ${g ? 'text-5xl' : 'text-4xl'}`}
      >
        {valor}
      </Text>
      <Text
        className={`text-center font-nunito-bold text-apagado-oscuro ${g ? 'text-xl' : 'text-sm'}`}
      >
        {etiqueta}
      </Text>
    </View>
  );

  const titulo = (texto: string) => (
    <Text
      className={`px-1 font-nunito-black uppercase tracking-wide text-seccion ${
        g ? 'text-xl' : 'text-base'
      }`}
    >
      {texto}
    </Text>
  );

  return (
    <SafeAreaView edges={['top', 'left', 'right']} className="flex-1 bg-panel">
      <ScrollView
        contentContainerClassName={`gap-4 px-4 pb-6 pt-3 ${rejilla ? 'w-full max-w-[960px] self-center' : ''}`}
      >
        <View className="flex-row items-center gap-2.5">
          <Octavio tamano={g ? 120 : 88} conVarita />
          <View className="flex-1">
            <Text className={`font-nunito-black text-tinta ${g ? 'text-4xl' : 'text-[30px]'}`}>
              Mis logros
            </Text>
            <Text className={`font-nunito-bold text-lila ${g ? 'text-xl' : 'text-base'}`}>
              Solo te comparas contigo, {p.alias}.
            </Text>
          </View>
        </View>

        <View className="flex-row gap-2.5">
          {cifra('⭐', conPuntoDeMiles(p.puntosTotal), 'puntos en total')}
          {cifra('✏️', String(p.ejerciciosResueltos), 'ejercicios resueltos')}
          {cifra('🏅', String(p.insignias), p.insignias === 1 ? 'insignia' : 'insignias')}
        </View>

        <View className={`gap-3.5 rounded-[22px] bg-white ${g ? 'p-7' : 'p-5'}`}>
          {titulo('Esta semana')}
          <Text className={`font-nunito-black text-tinta ${g ? 'text-4xl' : 'text-[28px]'}`}>
            {conPuntoDeMiles(p.puntosSemana)} puntos
            {marca > 0 && (
              <Text
                className={`font-nunito-bold text-apagado-oscuro ${g ? 'text-2xl' : 'text-lg'}`}
              >
                {' '}
                · tu mejor semana: {conPuntoDeMiles(marca)}
              </Text>
            )}
          </Text>
          <View
            accessible
            accessibilityRole="progressbar"
            accessibilityValue={{ min: 0, max: 100, now: Math.round(avance * 100) }}
            className="h-5 overflow-hidden rounded-full bg-lila-fondo"
          >
            <View className="h-5 rounded-full bg-dorado" style={{ width: `${avance * 100}%` }} />
          </View>
          <Text className={`font-nunito-bold text-tinta-media ${g ? 'text-xl' : 'text-lg'}`}>
            {p.mensaje}
          </Text>
        </View>

        {titulo('Mis unidades')}
        {p.unidades.length === 0 ? (
          <Text
            className={`px-1 font-nunito-bold text-apagado-oscuro ${g ? 'text-xl' : 'text-lg'}`}
          >
            Cuando practiques una unidad, aquí verás sus estrellas. Con 3 estrellas ganas su
            insignia.
          </Text>
        ) : (
          <View className={rejilla ? 'flex-row flex-wrap justify-between gap-y-3' : 'gap-2.5'}>
            {p.unidades.map((u) => (
              <View
                key={u.id}
                className={`flex-row items-center gap-4 rounded-[22px] border-2 bg-white p-5 ${
                  u.insignia ? 'border-dorado' : 'border-divisor'
                } ${rejilla ? 'w-[49%]' : ''}`}
              >
                <Text className={g ? 'text-6xl' : 'text-5xl'} accessibilityElementsHidden>
                  {u.insignia ? '🏅' : '📘'}
                </Text>
                <View className="flex-1 gap-2">
                  <Text className={`font-nunito-black text-tinta ${g ? 'text-2xl' : 'text-xl'}`}>
                    {u.descripcion}
                  </Text>
                  <View className="flex-row flex-wrap items-center gap-x-3 gap-y-1">
                    <Estrellas cantidad={u.estrellas} grande={g} />
                    <Text
                      className={`font-nunito-bold text-apagado-oscuro ${g ? 'text-lg' : 'text-[15px]'}`}
                    >
                      {u.insignia ? '¡Dominada!' : `Nivel ${u.nivel} · ${u.curso}° básico`}
                    </Text>
                  </View>
                </View>
              </View>
            ))}
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}
