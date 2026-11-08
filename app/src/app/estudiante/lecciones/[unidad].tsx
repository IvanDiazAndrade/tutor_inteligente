import { router, useLocalSearchParams } from 'expo-router';
import { View } from 'react-native';

import { BotonPrimario } from '@/components/BotonPrimario';
import {
  EncabezadoDetalle,
  EstadoCarga,
  PantallaEstudiante,
  Rejilla,
  volverALista,
} from '@/components/PantallaEstudiante';
import { TarjetaLista } from '@/components/TarjetaLista';
import { useDistribucion } from '@/hooks/useDistribucion';
import { nombreLeccion, useContenidoEstudiante } from '@/sesion/useContenidoEstudiante';

// Pestaña Lecciones, nivel 2: la lección dividida en partes, cada una con lo básico del
// subtema y un ejemplo. Al final, un botón lleva a sus ejercicios.
export default function DetalleLeccion() {
  const { unidad } = useLocalSearchParams<{ unidad: string }>();
  const { esTablet } = useDistribucion();
  const c = useContenidoEstudiante();
  const volver = () => volverALista('/estudiante/lecciones');

  if (!c.listo) {
    return c.error ? (
      <EstadoCarga texto={c.error.message} onReintentar={c.reintentar} />
    ) : (
      <EstadoCarga texto="Abriendo la lección…" />
    );
  }
  const leccion = c.leccion(unidad);
  if (!leccion) return <EstadoCarga texto="No encontramos esta lección." />;

  return (
    <PantallaEstudiante>
      <EncabezadoDetalle
        antetitulo={nombreLeccion(leccion, c.estudiante.curso)}
        titulo={leccion.titulo}
        alVolver={volver}
      />
      <Rejilla>
        {leccion.partes.map((p, i) => (
          <TarjetaLista
            key={p.titulo}
            antetitulo={`Parte ${i + 1}`}
            titulo={p.titulo}
            resumen={p.explicacion}
            grande={esTablet}
          />
        ))}
      </Rejilla>
      <View className={`mt-1 ${esTablet ? 'w-full max-w-[420px] self-center' : ''}`}>
        <BotonPrimario
          titulo="Practicar esta lección"
          onPress={() => router.navigate(`/estudiante/ejercicios/${leccion.unidadId}`)}
          grande={esTablet}
        />
      </View>
    </PantallaEstudiante>
  );
}
