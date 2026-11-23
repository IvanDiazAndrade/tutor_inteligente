import { router } from 'expo-router';
import { useRef, useState } from 'react';
import { Animated, ScrollView, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { BotonPrimario } from '@/components/BotonPrimario';
import { Estrellas } from '@/components/Estrellas';
import { Octavio } from '@/components/Octavio';
import {
  EncabezadoDetalle,
  EstadoCarga,
  Rejilla,
  clasesContenido,
  volverALista,
} from '@/components/PantallaEstudiante';
import { PestanasSuperiores } from '@/components/PestanasSuperiores';
import { TarjetaLista } from '@/components/TarjetaLista';
import { useDistribucion } from '@/hooks/useDistribucion';
import { nombreLeccion, useContenidoEstudiante } from '@/sesion/useContenidoEstudiante';

export type Vista = 'leccion' | 'ejercicios';
const VISTAS: Vista[] = ['leccion', 'ejercicios'];
const TITULOS = ['Lección', 'Ejercicios'];

// Detalle de una unidad: la lección y sus ejercicios en dos pestañas superiores, que se cambian
// tocándolas o deslizando. Parte en "Lección", salvo que se pida otra cosa (p. ej. la sugerencia
// de Octavio cuando la unidad aún no tiene ejercicios).
export function DetalleUnidad({ unidad, inicial }: { unidad: string; inicial: Vista }) {
  const { esTablet: g } = useDistribucion();
  const c = useContenidoEstudiante();
  const [activa, setActiva] = useState(VISTAS.indexOf(inicial));
  const [ancho, setAncho] = useState(0);
  const [desplazamiento] = useState(() => new Animated.Value(0));
  const paginas = useRef<ScrollView>(null);

  if (!c.listo) {
    return c.error ? (
      <EstadoCarga texto={c.error.message} onReintentar={c.reintentar} />
    ) : (
      <EstadoCarga texto="Abriendo la lección…" />
    );
  }
  const leccion = c.leccion(unidad);
  const datos = c.porUnidad.get(unidad);
  if (!leccion || !datos) return <EstadoCarga texto="No encontramos esta lección." />;
  const disponibles = datos.conEjercicios;

  const elegir = (i: number) => {
    setActiva(i);
    paginas.current?.scrollTo({ x: i * ancho, animated: true });
  };

  const paginaLeccion = (
    <>
      <Rejilla>
        {leccion.partes.map((p, i) => (
          <TarjetaLista
            key={p.titulo}
            antetitulo={`Parte ${i + 1}`}
            titulo={p.titulo}
            resumen={p.explicacion}
            grande={g}
          />
        ))}
      </Rejilla>
      <View className={`mt-1 ${g ? 'w-full max-w-[420px] self-center' : ''}`}>
        <BotonPrimario titulo="Ir a los ejercicios →" onPress={() => elegir(1)} grande={g} />
      </View>
    </>
  );

  // Un ejercicio por parte de la lección. Todos abren la práctica adaptativa de la unidad: el
  // servidor elige el ejercicio según el nivel del niño (RF-E3).
  const paginaEjercicios = (
    <>
      {!disponibles && (
        <View className="flex-row items-center gap-3 rounded-[20px] bg-lila-fondo px-4 py-3">
          <Octavio tamano={g ? 64 : 48} guino />
          <Text className={`flex-1 font-nunito-bold text-tinta-media ${g ? 'text-lg' : 'text-sm'}`}>
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
            grande={g}
          />
        ))}
      </Rejilla>
    </>
  );

  return (
    <SafeAreaView edges={['top', 'left', 'right']} className="flex-1 bg-panel">
      <View
        className={`w-full self-center ${g ? 'max-w-[960px] gap-3 px-6 pt-5' : 'max-w-[720px] gap-2 px-4 pt-3'}`}
      >
        <EncabezadoDetalle
          antetitulo={nombreLeccion(leccion, c.estudiante.curso)}
          titulo={leccion.titulo}
          alVolver={volverALista}
          derecha={disponibles && <Estrellas cantidad={datos.estrellas} grande={g} />}
          divisor={false}
        />
        <PestanasSuperiores
          titulos={TITULOS}
          activa={activa}
          onElegir={elegir}
          posicion={
            ancho > 0
              ? desplazamiento.interpolate({ inputRange: [0, ancho], outputRange: [0, 1] })
              : new Animated.Value(activa)
          }
          grande={g}
        />
      </View>
      <View
        className="flex-1"
        onLayout={(e) => {
          // Al medir (o al girar la pantalla) las páginas se vuelven a montar con el nuevo ancho,
          // ya ubicadas en la pestaña activa.
          const nuevo = e.nativeEvent.layout.width;
          setAncho(nuevo);
          desplazamiento.setValue(activa * nuevo);
        }}
      >
        {ancho > 0 && (
          <Animated.ScrollView
            key={ancho}
            ref={paginas}
            horizontal
            pagingEnabled
            contentOffset={{ x: activa * ancho, y: 0 }}
            showsHorizontalScrollIndicator={false}
            scrollEventThrottle={16}
            onScroll={Animated.event([{ nativeEvent: { contentOffset: { x: desplazamiento } } }], {
              useNativeDriver: true,
              listener: (e: {
                nativeEvent: { contentOffset: { x: number }; layoutMeasurement: { width: number } };
              }) => {
                // Mientras cambia el ancho (al girar), Android recoloca el desplazamiento con las
                // páginas aún del tamaño anterior: esas posiciones no son un cambio de pestaña.
                if (Math.round(e.nativeEvent.layoutMeasurement.width) !== Math.round(ancho)) return;
                const i = Math.round(e.nativeEvent.contentOffset.x / ancho);
                if (i !== activa && i >= 0 && i < VISTAS.length) setActiva(i);
              },
            })}
          >
            {[paginaLeccion, paginaEjercicios].map((contenido, i) => (
              <ScrollView
                key={VISTAS[i]}
                style={{ width: ancho }}
                contentContainerClassName={clasesContenido(g)}
              >
                {contenido}
              </ScrollView>
            ))}
          </Animated.ScrollView>
        )}
      </View>
    </SafeAreaView>
  );
}
