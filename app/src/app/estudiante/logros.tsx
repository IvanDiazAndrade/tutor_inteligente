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
  const { esTablet: g } = useDistribucion();
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

  const cifra = (valor: string, etiqueta: string) => (
    <View className="flex-1 items-center rounded-[18px] bg-white px-2 py-3">
      <Text className={`font-nunito-black text-tinta ${g ? 'text-3xl' : 'text-2xl'}`}>{valor}</Text>
      <Text
        className={`text-center font-nunito-bold text-apagado-oscuro ${g ? 'text-base' : 'text-xs'}`}
      >
        {etiqueta}
      </Text>
    </View>
  );

  const titulo = (texto: string) => (
    <Text
      className={`px-1 font-nunito-black uppercase tracking-wide text-seccion ${
        g ? 'text-base' : 'text-[13px]'
      }`}
    >
      {texto}
    </Text>
  );

  return (
    <SafeAreaView edges={['top', 'left', 'right']} className="flex-1 bg-panel">
      <ScrollView
        contentContainerClassName={`gap-4 px-4 pb-6 pt-3 ${g ? 'w-full max-w-[760px] self-center' : ''}`}
      >
        <View className="flex-row items-center gap-2.5">
          <Octavio tamano={g ? 88 : 62} conVarita />
          <View className="flex-1">
            <Text className={`font-nunito-black text-tinta ${g ? 'text-3xl' : 'text-[22px]'}`}>
              Mis logros
            </Text>
            <Text className={`font-nunito-bold text-lila ${g ? 'text-base' : 'text-xs'}`}>
              Solo te comparas contigo, {p.alias}.
            </Text>
          </View>
        </View>

        <View className="flex-row gap-2.5">
          {cifra(`⭐ ${conPuntoDeMiles(p.puntosTotal)}`, 'puntos en total')}
          {cifra(String(p.ejerciciosResueltos), 'ejercicios resueltos')}
          {cifra(`🏅 ${p.insignias}`, p.insignias === 1 ? 'insignia' : 'insignias')}
        </View>

        <View className={`gap-2.5 rounded-[20px] bg-white ${g ? 'p-6' : 'p-4'}`}>
          {titulo('Esta semana')}
          <Text className={`font-nunito-black text-tinta ${g ? 'text-2xl' : 'text-lg'}`}>
            {conPuntoDeMiles(p.puntosSemana)} puntos
            {marca > 0 && (
              <Text className="font-nunito-bold text-apagado-oscuro">
                {' '}
                · tu mejor semana: {conPuntoDeMiles(marca)}
              </Text>
            )}
          </Text>
          <View
            accessible
            accessibilityRole="progressbar"
            accessibilityValue={{ min: 0, max: 100, now: Math.round(avance * 100) }}
            className="h-3 overflow-hidden rounded-full bg-lila-fondo"
          >
            <View className="h-3 rounded-full bg-dorado" style={{ width: `${avance * 100}%` }} />
          </View>
          <Text className={`font-nunito-bold text-tinta-media ${g ? 'text-base' : 'text-sm'}`}>
            {p.mensaje}
          </Text>
        </View>

        {titulo('Mis unidades')}
        {p.unidades.length === 0 ? (
          <Text
            className={`px-1 font-nunito-bold text-apagado-oscuro ${g ? 'text-base' : 'text-sm'}`}
          >
            Cuando practiques una unidad, aquí verás sus estrellas. Con 3 estrellas ganas su
            insignia.
          </Text>
        ) : (
          <View className={g ? 'flex-row flex-wrap gap-3' : 'gap-2.5'}>
            {p.unidades.map((u) => (
              <View
                key={u.id}
                className={`flex-row items-center gap-3 rounded-[18px] border-[1.5px] bg-white p-3.5 ${
                  u.insignia ? 'border-dorado' : 'border-divisor'
                } ${g ? 'w-[48.5%]' : ''}`}
              >
                <Text className={g ? 'text-4xl' : 'text-3xl'} accessibilityElementsHidden>
                  {u.insignia ? '🏅' : '📘'}
                </Text>
                <View className="flex-1 gap-1">
                  <Text className={`font-nunito-black text-tinta ${g ? 'text-lg' : 'text-[15px]'}`}>
                    {u.descripcion}
                  </Text>
                  <View className="flex-row items-center gap-2">
                    <Estrellas cantidad={u.estrellas} grande={g} />
                    <Text
                      className={`font-nunito-bold text-apagado-oscuro ${g ? 'text-sm' : 'text-xs'}`}
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
