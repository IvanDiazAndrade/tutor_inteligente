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

// Pestaña Lecciones, nivel 1 (RF-D9, CU-2): una tarjeta por lección de su curso con un resumen
// de 1–2 líneas, sus estrellas y su etiqueta (RF-E5, RF-G2), y arriba la unidad que sugiere
// Octavio. Las de cursos anteriores se abren aparte. Estrellas, etiquetas y sugerencia las
// calcula el servidor. Cada tarjeta abre la unidad, con la lección y sus ejercicios en pestañas.
export default function ListaLecciones() {
  const { dosColumnas, esTablet } = useDistribucion();
  const [verAnteriores, setVerAnteriores] = useState(false);
  const c = useContenidoEstudiante();

  if (!c.listo) {
    return c.error ? (
      <EstadoCarga texto={c.error.message} onReintentar={c.reintentar} />
    ) : (
      <EstadoCarga texto="Octavio está preparando tus lecciones…" />
    );
  }

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
            resumen={l.resumen}
            lineasResumen={2}
            onPress={() => router.push(`/estudiante/lecciones/${l.unidadId}`)}
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
        titulo="Lecciones"
        subtitulo={`${c.estudiante.curso}° básico · Lee la lección y después practica`}
      />
      {sugerida && leccionSugerida && (
        <SugerenciaOctavio
          nombre={leccionSugerida.titulo}
          etiqueta={sugerida.etiqueta === 'repasar' ? 'repasar' : undefined}
          onPracticar={() =>
            sugerida.conEjercicios
              ? router.push({ pathname: '/ejercicio', params: { unidad: sugerida.id } })
              : router.push({
                  pathname: '/estudiante/lecciones/[unidad]',
                  params: { unidad: sugerida.id, vista: 'ejercicios' },
                })
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
              ? 'Ocultar lecciones de cursos anteriores'
              : 'Ver lecciones de cursos anteriores'
          }
          onPress={() => setVerAnteriores((v) => !v)}
        />
      )}
      {verAnteriores && tarjetas(c.anteriores)}
    </PantallaEstudiante>
  );
}
