import { router, useLocalSearchParams } from 'expo-router';
import { useState } from 'react';
import { Keyboard, Pressable, ScrollView, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import Svg, { Path } from 'react-native-svg';

import { BotonAccion } from '@/components/BotonAccion';
import { BotonPrimario } from '@/components/BotonPrimario';
import { CampoRespuesta } from '@/components/CampoRespuesta';
import { EnunciadoResaltado } from '@/components/EnunciadoResaltado';
import { GloboOctavio } from '@/components/GloboOctavio';
import { RepresentacionFraccion } from '@/components/RepresentacionFraccion';
import { EJERCICIOS, ejercicioPorId, REFUERZOS } from '@/datos/ejercicios';
import { PUNTOS_EJEMPLO } from '@/datos/ejemplo';
import { useDistribucion } from '@/hooks/useDistribucion';
import { corregir, puntosPor } from '@/modelo/corrector';

const MAX_PISTAS = 3;
const FALLOS_PARA_RESOLVER_JUNTOS = 3; // RF-P7 (parámetro N, por defecto 3)
const MENSAJE_INICIAL = 'Lee con calma y escribe tu respuesta. ¡Tú puedes!';

const conPuntoDeMiles = (n: number) => String(n).replace(/\B(?=(\d{3})+(?!\d))/g, '.');

type Estado = 'respondiendo' | 'correcta' | 'guiada';

// Ejercicio con Octavio (CU-3, CU-4, CU-11, CU-13; mockup "Ejercicio Estudiante").
// Prototipo: corrige en el dispositivo y Octavio usa las plantillas locales del modo sin LLM
// (modelo_pedagogico.md §7). En la Fase IV todo esto lo resuelve el servidor (F2, F3).
export default function Ejercicio() {
  const { unidad } = useLocalSearchParams<{ unidad?: string }>();
  const { dosColumnas, esTablet } = useDistribucion();

  const [ejercicioId, setEjercicioId] = useState(
    () => EJERCICIOS.find((e) => e.unidadId === unidad)?.id ?? EJERCICIOS[0].id,
  );
  const ejercicio = ejercicioPorId(ejercicioId);

  const [numerador, setNumerador] = useState('');
  const [denominador, setDenominador] = useState('');
  const [estado, setEstado] = useState<Estado>('respondiendo');
  const [mensaje, setMensaje] = useState(MENSAJE_INICIAL);
  const [pistasUsadas, setPistasUsadas] = useState(0);
  const [fallos, setFallos] = useState(0);
  const [puedeNoEntiendo, setPuedeNoEntiendo] = useState(false);
  const [pasoGuiado, setPasoGuiado] = useState(0);
  const [seguidas, setSeguidas] = useState(2);
  const [puntos, setPuntos] = useState(PUNTOS_EJEMPLO);
  const [refuerzo, setRefuerzo] = useState(0);

  const cargar = (id: string) => {
    setEjercicioId(id);
    setNumerador('');
    setDenominador('');
    setEstado('respondiendo');
    setMensaje(MENSAJE_INICIAL);
    setPistasUsadas(0);
    setFallos(0);
    setPuedeNoEntiendo(false);
    setPasoGuiado(0);
  };

  // "Otro ejercicio": pasa al siguiente sin penalizar (modelo_pedagogico.md §2).
  const otroEjercicio = () => {
    const i = EJERCICIOS.findIndex((e) => e.id === ejercicio.id);
    cargar(EJERCICIOS[(i + 1) % EJERCICIOS.length].id);
  };

  const responder = () => {
    if (estado === 'correcta') {
      otroEjercicio();
      return;
    }
    Keyboard.dismiss();
    const respuesta =
      ejercicio.formatoRespuesta === 'fraccion' ? `${numerador}/${denominador}` : numerador;
    const resultado = corregir(respuesta, ejercicio);

    if (resultado.tipo === 'formato_invalido') {
      setMensaje(resultado.mensaje); // no cuenta como intento
      return;
    }
    if (resultado.tipo === 'correcta') {
      const ganados = puntosPor(ejercicio.nivel, pistasUsadas);
      const forma = resultado.esFormaCanonica
        ? ''
        : ` También puedes escribirla como ${ejercicio.respuestaFinal}.`;
      setPuntos((p) => p + ganados);
      setSeguidas((s) => s + 1);
      setRefuerzo((r) => r + 1);
      setEstado('correcta');
      setMensaje(`${REFUERZOS[refuerzo % REFUERZOS.length]}${forma} Ganaste ${ganados} puntos.`);
      return;
    }
    // Incorrecta: causa del error común si se detecta; si no, el primer paso (plantilla local).
    const nuevosFallos = fallos + 1;
    setFallos(nuevosFallos);
    setSeguidas(0);
    setPuedeNoEntiendo(true);
    setMensaje(
      resultado.errorComun
        ? `Todavía no es. ${resultado.errorComun.retroalimentacion}`
        : `Todavía no es. Revisa este paso: ${ejercicio.solucionReferencia[0]}`,
    );
  };

  const pedirPista = () => {
    if (pistasUsadas >= MAX_PISTAS) return;
    setMensaje(`Pista ${pistasUsadas + 1}: ${ejercicio.pistas[pistasUsadas]}`);
    setPistasUsadas(pistasUsadas + 1);
    setPuedeNoEntiendo(true);
  };

  const noEntiendo = () => setMensaje(ejercicio.reexplicacion);

  const resolverJuntos = () => {
    Keyboard.dismiss();
    setEstado('guiada');
    setPasoGuiado(0);
    setMensaje(ejercicio.solucionReferencia[0]);
  };

  const siguientePaso = () => {
    const siguiente = pasoGuiado + 1;
    setPasoGuiado(siguiente);
    setMensaje(ejercicio.solucionReferencia[siguiente]);
  };

  const ultimoPaso = pasoGuiado === ejercicio.solucionReferencia.length - 1;
  const probarParecido = () => {
    const i = EJERCICIOS.findIndex((e) => e.id === ejercicio.id);
    cargar(ejercicio.analogoId ?? EJERCICIOS[(i + 1) % EJERCICIOS.length].id);
    setMensaje('¡Ahora prueba este, que es parecido!');
  };

  const g = esTablet;

  const encabezado = (
    <View className="gap-2.5">
      <View className="flex-row items-center gap-2.5">
        <Pressable
          accessibilityRole="button"
          accessibilityLabel="Volver"
          onPress={() => router.back()}
          className={`items-center justify-center rounded-[14px] bg-white active:bg-fondo ${
            g ? 'h-14 w-14' : 'h-10 w-10'
          }`}
        >
          <Svg width={g ? 24 : 18} height={g ? 24 : 18} viewBox="0 0 18 18">
            <Path
              d="M11.5 3.5 L6 9 L11.5 14.5"
              fill="none"
              stroke="#6D28D9"
              strokeWidth={2.6}
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </Svg>
        </Pressable>
        <View className="flex-1">
          <Text className={`font-nunito-extrabold text-tinta ${g ? 'text-xl' : 'text-sm'}`}>
            {ejercicio.unidadNombre}
          </Text>
          <Text className={`font-nunito-bold text-lila ${g ? 'text-sm' : 'text-[11px]'}`}>
            Unidad {ejercicio.unidadId}
          </Text>
        </View>
        <View className="rounded-full bg-white px-3 py-1.5">
          <Text className={`font-nunito-black text-ambar ${g ? 'text-lg' : 'text-[13px]'}`}>
            ⭐ {conPuntoDeMiles(puntos)}
          </Text>
        </View>
      </View>
      <View className="flex-row gap-2">
        <View className="rounded-full border-[1.5px] border-nueva-borde bg-fondo px-3 py-1">
          <Text className={`font-nunito-extrabold text-primario ${g ? 'text-base' : 'text-xs'}`}>
            Nivel {ejercicio.nivel}
          </Text>
        </View>
        {seguidas > 0 && (
          <View className="rounded-full border-[1.5px] border-ambar-borde bg-ambar-fondo px-3 py-1">
            <Text className={`font-nunito-extrabold text-ambar ${g ? 'text-base' : 'text-xs'}`}>
              🔥 {seguidas} {seguidas === 1 ? 'seguida' : 'seguidas'}
            </Text>
          </View>
        )}
      </View>
    </View>
  );

  const tarjeta = (
    <View className={`rounded-[20px] bg-white ${g ? 'gap-6 p-7' : 'gap-3.5 p-[18px]'}`}>
      <EnunciadoResaltado texto={ejercicio.enunciado} grande={g} />
      <View className={`flex-row items-center justify-center ${g ? 'gap-10' : 'gap-[22px]'}`}>
        {ejercicio.representacion && (
          <RepresentacionFraccion
            denominador={ejercicio.representacion.denominador}
            partesDestacadas={ejercicio.representacion.partesDestacadas}
            tamano={g ? 200 : 128}
          />
        )}
        <CampoRespuesta
          formato={ejercicio.formatoRespuesta}
          numerador={numerador}
          denominador={denominador}
          onCambio={(n, d) => {
            setNumerador(n);
            setDenominador(d);
          }}
          onEnviar={responder}
          deshabilitado={estado !== 'respondiendo'}
          grande={g}
        />
      </View>
      {estado !== 'guiada' && (
        <BotonPrimario
          titulo={estado === 'correcta' ? 'Siguiente ejercicio →' : 'Responder'}
          onPress={responder}
          grande={g}
        />
      )}
    </View>
  );

  const tutor = (
    <GloboOctavio mensaje={mensaje} grande={g}>
      {estado === 'guiada' && (
        <View className="flex-row justify-end">
          <BotonAccion
            texto={ultimoPaso ? 'Probar uno parecido →' : 'Siguiente →'}
            onPress={ultimoPaso ? probarParecido : siguientePaso}
            destacado
            grande={g}
          />
        </View>
      )}
    </GloboOctavio>
  );

  const acciones = estado === 'respondiendo' && (
    <View className="flex-row flex-wrap justify-center gap-2">
      {fallos >= FALLOS_PARA_RESOLVER_JUNTOS && (
        <BotonAccion texto="🤝 ¿Lo resolvemos juntos?" onPress={resolverJuntos} destacado grande={g} />
      )}
      <BotonAccion
        texto={`💡 Pista (quedan ${MAX_PISTAS - pistasUsadas})`}
        onPress={pedirPista}
        deshabilitado={pistasUsadas >= MAX_PISTAS}
        grande={g}
      />
      <BotonAccion
        texto="🤔 No entiendo"
        onPress={noEntiendo}
        deshabilitado={!puedeNoEntiendo}
        grande={g}
      />
      <BotonAccion texto="↻ Otro ejercicio" onPress={otroEjercicio} grande={g} />
    </View>
  );

  return (
    <SafeAreaView className="flex-1 bg-panel">
      {dosColumnas ? (
        <View className={`flex-1 flex-row ${g ? 'gap-8 px-8 pt-4' : 'gap-4 px-4 pt-2'}`}>
          <View className="flex-1">
            <ScrollView
              contentContainerClassName="gap-3 pb-4"
              keyboardShouldPersistTaps="handled"
            >
              {encabezado}
              {tarjeta}
            </ScrollView>
          </View>
          <View className="flex-1">
            <ScrollView
              contentContainerClassName={`grow gap-3 pb-4 ${g ? 'justify-center' : 'justify-end'}`}
              keyboardShouldPersistTaps="handled"
            >
              {tutor}
              {acciones}
            </ScrollView>
          </View>
        </View>
      ) : (
        <ScrollView
          contentContainerClassName={`grow gap-3 px-4 pb-4 pt-2 ${
            g ? 'w-full max-w-[760px] self-center gap-6' : ''
          }`}
          keyboardShouldPersistTaps="handled"
        >
          {encabezado}
          {tarjeta}
          {/* En el teléfono Octavio queda abajo, como en el mockup; en tablet, junto al ejercicio. */}
          <View className={g ? 'gap-4' : 'flex-1 justify-end gap-3'}>
            {tutor}
            {acciones}
          </View>
        </ScrollView>
      )}
    </SafeAreaView>
  );
}
