import { router } from 'expo-router';
import { useState } from 'react';

import type { LeccionEstudiante } from '@/api/cliente';
import {
  Enlace,
  EstadoCarga,
  PantallaEstudiante,
  Rejilla,
  TituloPantalla,
} from '@/components/PantallaEstudiante';
import { TarjetaLista } from '@/components/TarjetaLista';
import { useDistribucion } from '@/hooks/useDistribucion';
import { nombreLeccion, useContenidoEstudiante } from '@/sesion/useContenidoEstudiante';

// Pestaña Lecciones, nivel 1 (RF-D9): una tarjeta por lección de su curso con un resumen de
// 1–2 líneas. Las de cursos anteriores se abren aparte.
export default function ListaLecciones() {
  const { esTablet } = useDistribucion();
  const [verAnteriores, setVerAnteriores] = useState(false);
  const c = useContenidoEstudiante();

  if (!c.listo) {
    return c.error ? (
      <EstadoCarga texto={c.error.message} onReintentar={c.reintentar} />
    ) : (
      <EstadoCarga texto="Octavio está preparando tus lecciones…" />
    );
  }

  const tarjetas = (lista: LeccionEstudiante[]) => (
    <Rejilla>
      {lista.map((l) => (
        <TarjetaLista
          key={l.unidadId}
          antetitulo={nombreLeccion(l, c.estudiante.curso)}
          titulo={l.titulo}
          resumen={l.resumen}
          lineasResumen={2}
          onPress={() => router.push(`/estudiante/lecciones/${l.unidadId}`)}
          grande={esTablet}
        />
      ))}
    </Rejilla>
  );

  return (
    <PantallaEstudiante>
      <TituloPantalla
        titulo="Lecciones"
        subtitulo={`${c.estudiante.curso}° básico · Lee la lección y después practica`}
      />
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
