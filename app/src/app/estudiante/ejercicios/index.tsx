import { router } from 'expo-router';
import { useState } from 'react';

import type { LeccionEstudiante } from '@/api/cliente';
import { Estrellas } from '@/components/Estrellas';
import { Etiqueta } from '@/components/Etiqueta';
import {
  Enlace,
  EstadoCarga,
  PantallaEstudiante,
  Rejilla,
  TituloPantalla,
} from '@/components/PantallaEstudiante';
import { SugerenciaOctavio } from '@/components/SugerenciaOctavio';
import { TarjetaLista } from '@/components/TarjetaLista';
import { useDistribucion } from '@/hooks/useDistribucion';
import { nombreLeccion, useContenidoEstudiante } from '@/sesion/useContenidoEstudiante';

// Pestaña Ejercicios, nivel 1 (CU-2): un grupo de ejercicios por lección, con sus estrellas y
// etiqueta (RF-E5, RF-G2), y arriba la unidad que sugiere Octavio. Misma estructura que
// Lecciones. Estrellas, etiquetas y sugerencia las calcula el servidor.
export default function ListaEjercicios() {
  const { dosColumnas, esTablet } = useDistribucion();
  const [verAnteriores, setVerAnteriores] = useState(false);
  const c = useContenidoEstudiante();

  if (!c.listo) {
    return c.error ? (
      <EstadoCarga texto={c.error.message} onReintentar={c.reintentar} />
    ) : (
      <EstadoCarga texto="Octavio está preparando tus ejercicios…" />
    );
  }

  const abrir = (unidadId: string) => router.push(`/estudiante/ejercicios/${unidadId}`);
  const sugerida = c.unidades.find((u) => u.sugerida);
  const leccionSugerida = sugerida && c.leccion(sugerida.id);

  const tarjetas = (lista: LeccionEstudiante[]) => (
    <Rejilla>
      {lista.map((l) => {
        const u = c.porUnidad.get(l.unidadId);
        return (
          <TarjetaLista
            key={l.unidadId}
            antetitulo={nombreLeccion(l, c.estudiante.curso)}
            titulo={l.titulo}
            resumen={`${l.partes.length} ejercicios: ${l.partes.map((p) => p.titulo).join(' · ')}`}
            lineasResumen={2}
            onPress={() => abrir(l.unidadId)}
            grande={esTablet}
            pie={
              u?.conEjercicios ? (
                <>
                  <Estrellas cantidad={u.estrellas} grande={esTablet} />
                  {u.etiqueta && <Etiqueta tipo={u.etiqueta} grande={esTablet} />}
                </>
              ) : (
                <Etiqueta tipo="pronto" grande={esTablet} />
              )
            }
          />
        );
      })}
    </Rejilla>
  );

  return (
    <PantallaEstudiante>
      <TituloPantalla
        titulo="Ejercicios"
        subtitulo={`${c.estudiante.curso}° básico · Elige qué quieres practicar`}
      />
      {sugerida && leccionSugerida && (
        <SugerenciaOctavio
          nombre={leccionSugerida.titulo}
          etiqueta={sugerida.etiqueta === 'repasar' ? 'repasar' : undefined}
          onPracticar={() =>
            sugerida.conEjercicios
              ? router.push({ pathname: '/ejercicio', params: { unidad: sugerida.id } })
              : abrir(sugerida.id)
          }
          grande={esTablet}
          apilada={dosColumnas && !esTablet}
        />
      )}
      {tarjetas(c.delCurso)}
      {c.anteriores.length > 0 && (
        <Enlace
          texto={
            verAnteriores
              ? 'Ocultar ejercicios de cursos anteriores'
              : 'Ver ejercicios de cursos anteriores'
          }
          onPress={() => setVerAnteriores((v) => !v)}
        />
      )}
      {verAnteriores && tarjetas(c.anteriores)}
    </PantallaEstudiante>
  );
}
