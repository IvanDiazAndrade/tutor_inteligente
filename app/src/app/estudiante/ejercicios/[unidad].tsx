import { router, useLocalSearchParams } from 'expo-router';
import { Text, View } from 'react-native';

import { Estrellas } from '@/components/Estrellas';
import { Octavio } from '@/components/Octavio';
import {
  EncabezadoDetalle,
  Enlace,
  EstadoCarga,
  PantallaEstudiante,
  Rejilla,
  volverALista,
} from '@/components/PantallaEstudiante';
import { TarjetaLista } from '@/components/TarjetaLista';
import { useDistribucion } from '@/hooks/useDistribucion';
import { nombreLeccion, useContenidoEstudiante } from '@/sesion/useContenidoEstudiante';

// Pestaña Ejercicios, nivel 2: un ejercicio por parte de la lección. Cada uno abre la práctica
// de la unidad a pantalla completa; el servidor elige el ejercicio según el nivel del niño
// (RF-E3), así que por ahora todas las partes llevan a la misma práctica adaptativa.
export default function DetalleEjercicios() {
  const { unidad } = useLocalSearchParams<{ unidad: string }>();
  const { esTablet } = useDistribucion();
  const c = useContenidoEstudiante();
  const volver = () => volverALista('/estudiante/ejercicios');

  if (!c.listo) {
    return c.error ? (
      <EstadoCarga texto={c.error.message} onReintentar={c.reintentar} />
    ) : (
      <EstadoCarga texto="Abriendo los ejercicios…" />
    );
  }
  const leccion = c.leccion(unidad);
  const datos = c.porUnidad.get(unidad);
  if (!leccion || !datos) return <EstadoCarga texto="No encontramos estos ejercicios." />;
  const disponibles = datos.conEjercicios;

  return (
    <PantallaEstudiante>
      <EncabezadoDetalle
        antetitulo={`Ejercicios · ${nombreLeccion(leccion, c.estudiante.curso)}`}
        titulo={leccion.titulo}
        alVolver={volver}
        derecha={disponibles && <Estrellas cantidad={datos.estrellas} grande={esTablet} />}
      />
      {!disponibles && (
        <View className="flex-row items-center gap-3 rounded-[20px] bg-lila-fondo px-4 py-3">
          <Octavio tamano={esTablet ? 64 : 48} guino />
          <Text
            className={`flex-1 font-nunito-bold text-tinta-media ${esTablet ? 'text-lg' : 'text-sm'}`}
          >
            Octavio todavía está preparando estos ejercicios. Mientras tanto, puedes leer la
            lección.
          </Text>
        </View>
      )}
      <Rejilla>
        {leccion.partes.map((p, i) => (
          <TarjetaLista
            key={p.titulo}
            antetitulo={`Ejercicio ${i + 1}`}
            titulo={p.titulo}
            resumen={p.practica}
            lineasResumen={2}
            deshabilitada={!disponibles}
            onPress={() => router.push({ pathname: '/ejercicio', params: { unidad } })}
            grande={esTablet}
          />
        ))}
      </Rejilla>
      <Enlace
        texto="Leer la lección"
        onPress={() => router.navigate(`/estudiante/lecciones/${unidad}`)}
      />
    </PantallaEstudiante>
  );
}
