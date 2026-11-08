import { router } from 'expo-router';
import { Pressable, Text, View } from 'react-native';

import { Estrellas } from '@/components/Estrellas';
import { EstadoCarga, PantallaEstudiante, TituloPantalla } from '@/components/PantallaEstudiante';
import { useDistribucion } from '@/hooks/useDistribucion';
import { useSesion } from '@/sesion/SesionContext';
import { useContenidoEstudiante } from '@/sesion/useContenidoEstudiante';

const conPuntoDeMiles = (n: number) => String(n).replace(/\B(?=(\d{3})+(?!\d))/g, '.');

// Pestaña Perfil (CU-6, RF-E5): alias, curso, puntos y avance por unidad de su curso en
// estrellas. Solo se compara consigo mismo (RF-G3, RF-G4).
export default function Perfil() {
  const { esTablet: g } = useDistribucion();
  const { cerrar } = useSesion();
  const c = useContenidoEstudiante();

  if (!c.listo) {
    return c.error ? (
      <EstadoCarga texto={c.error.message} onReintentar={c.reintentar} />
    ) : (
      <EstadoCarga texto="Cargando tu perfil…" />
    );
  }

  const { estudiante } = c;
  const delCurso = c.unidades.filter((u) => u.curso === estudiante.curso);
  const iniciadas = delCurso.filter((u) => u.estrellas > 0).length;
  const dominadas = delCurso.filter((u) => u.estrellas === 3).length;

  const dato = (valor: string, texto: string) => (
    <View className="flex-1 items-center gap-0.5 rounded-[18px] bg-white px-2 py-3">
      <Text className={`font-nunito-black text-primario ${g ? 'text-3xl' : 'text-2xl'}`}>
        {valor}
      </Text>
      <Text
        className={`text-center font-nunito-bold text-apagado-oscuro ${g ? 'text-base' : 'text-xs'}`}
      >
        {texto}
      </Text>
    </View>
  );

  return (
    <PantallaEstudiante>
      <TituloPantalla titulo="Mi perfil" />
      <View className="flex-row items-center gap-4 rounded-[22px] bg-white px-4 py-4">
        <View
          className={`items-center justify-center rounded-full bg-primario ${
            g ? 'h-24 w-24' : 'h-[72px] w-[72px]'
          }`}
        >
          <Text className={`font-nunito-black text-white ${g ? 'text-5xl' : 'text-4xl'}`}>
            {estudiante.alias.charAt(0).toUpperCase()}
          </Text>
        </View>
        <View className="flex-1">
          <Text className={`font-nunito-black text-tinta ${g ? 'text-3xl' : 'text-2xl'}`}>
            {estudiante.alias}
          </Text>
          <Text className={`font-nunito-bold text-lila ${g ? 'text-lg' : 'text-sm'}`}>
            {estudiante.curso}° básico
          </Text>
        </View>
      </View>

      <View className="flex-row gap-3">
        {dato(`⭐ ${conPuntoDeMiles(estudiante.puntajeTotal)}`, 'puntos')}
        {dato(`${iniciadas}/${delCurso.length}`, 'unidades empezadas')}
        {dato(`${dominadas}/${delCurso.length}`, 'unidades dominadas')}
      </View>

      <View className="gap-2">
        <Text
          className={`px-1 font-nunito-black uppercase tracking-wide text-seccion ${
            g ? 'text-base' : 'text-[13px]'
          }`}
        >
          Mi avance · {estudiante.curso}° básico
        </Text>
        <View className="rounded-[20px] bg-white px-4 py-1">
          {delCurso.map((u, i) => (
            <View
              key={u.id}
              className={`flex-row items-center gap-3 py-3 ${i > 0 ? 'border-t border-divisor' : ''}`}
            >
              <Text
                className={`flex-1 font-nunito-extrabold text-tinta-media ${g ? 'text-lg' : 'text-sm'}`}
              >
                {c.leccion(u.id)?.titulo ?? u.descripcion}
              </Text>
              <Estrellas cantidad={u.estrellas} grande={g} />
            </View>
          ))}
        </View>
      </View>

      <Pressable
        accessibilityRole="button"
        onPress={() => cerrar().then(() => router.replace('/'))}
        className="items-center rounded-2xl border-2 border-borde bg-white py-3 active:border-primario-claro active:bg-lila-fondo"
      >
        <Text className={`font-nunito-extrabold text-primario ${g ? 'text-lg' : 'text-base'}`}>
          Cambiar de perfil
        </Text>
      </Pressable>
    </PantallaEstudiante>
  );
}
