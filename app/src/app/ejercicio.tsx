import { useQueryClient } from '@tanstack/react-query';
import { router, useLocalSearchParams } from 'expo-router';
import { useCallback, useEffect, useRef, useState } from 'react';
import { Keyboard, Pressable, ScrollView, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import Svg, { Path } from 'react-native-svg';

import { api, type EjercicioServido, ErrorApi } from '@/api/cliente';
import { BotonAccion } from '@/components/BotonAccion';
import { BotonPrimario } from '@/components/BotonPrimario';
import { CampoRespuesta } from '@/components/CampoRespuesta';
import { EnunciadoResaltado } from '@/components/EnunciadoResaltado';
import { GloboOctavio } from '@/components/GloboOctavio';
import { Octavio } from '@/components/Octavio';
import { RepresentacionFraccion } from '@/components/RepresentacionFraccion';
import { useDistribucion } from '@/hooks/useDistribucion';
import { Protegida } from '@/sesion/Protegida';
import { useSesion } from '@/sesion/SesionContext';
import { useConsulta } from '@/sesion/useConsulta';

const MENSAJE_INICIAL = 'Lee con calma y escribe tu respuesta. ¡Tú puedes!';

const conPuntoDeMiles = (n: number) => String(n).replace(/\B(?=(\d{3})+(?!\d))/g, '.');

type Estado = 'cargando' | 'respondiendo' | 'correcta' | 'guiada' | 'sin-ejercicios';

type Representacion = {
  tipo: string;
  parametros: { denominador: number; partesDestacadas: number[] };
};

// Ejercicio con Octavio (CU-3, CU-4, CU-11, CU-13; mockup "Ejercicio Estudiante").
// El servidor sirve el ejercicio (F1), corrige (F2), entrega las pistas (F3) y actualiza el
// índice de dominio; la app nunca conoce la respuesta ni la solución (RF-D3, AD-1).
function PantallaEjercicio() {
  const { unidad } = useLocalSearchParams<{ unidad: string }>();
  const { dosColumnas, esTablet: g } = useDistribucion();
  const { sesion, cerrar } = useSesion();
  const token = sesion!.token;
  const clienteConsultas = useQueryClient();
  const perfil = useConsulta('perfil-estudiante', api.perfilEstudiante);

  const [ejercicio, setEjercicio] = useState<EjercicioServido | null>(null);
  const [estado, setEstado] = useState<Estado>('cargando');
  const [numerador, setNumerador] = useState('');
  const [denominador, setDenominador] = useState('');
  const [mensaje, setMensaje] = useState(MENSAJE_INICIAL);
  const [pistasRestantes, setPistasRestantes] = useState(0);
  const [ofreceJuntos, setOfreceJuntos] = useState(false);
  const [puedeNoEntiendo, setPuedeNoEntiendo] = useState(false);
  const [pasos, setPasos] = useState<string[]>([]);
  const [pasoGuiado, setPasoGuiado] = useState(0);
  const [analogo, setAnalogo] = useState<EjercicioServido | null>(null);
  const [seguidas, setSeguidas] = useState(0);
  const [ocupado, setOcupado] = useState(false);
  const inicio = useRef(0); // se fija al mostrar cada ejercicio

  // Errores de red o de sesión: se muestran en el globo de Octavio; con 401 vuelve al acceso.
  const conManejo = useCallback(
    async (accion: () => Promise<void>) => {
      setOcupado(true);
      try {
        await accion();
      } catch (e) {
        if (e instanceof ErrorApi && e.estado === 401) {
          await cerrar();
          return;
        }
        setMensaje(e instanceof ErrorApi ? e.message : 'Algo salió mal. Intenta otra vez.');
      } finally {
        setOcupado(false);
      }
    },
    [cerrar],
  );

  const mostrar = useCallback((nuevo: EjercicioServido, mensajeInicial = MENSAJE_INICIAL) => {
    setEjercicio(nuevo);
    setEstado('respondiendo');
    setNumerador('');
    setDenominador('');
    setMensaje(mensajeInicial);
    setPistasRestantes(nuevo.pistasRestantes);
    setOfreceJuntos(false);
    setPuedeNoEntiendo(false);
    setPasos([]);
    setPasoGuiado(0);
    setAnalogo(null);
    inicio.current = Date.now();
  }, []);

  // Servir un ejercicio de la unidad; también es "Otro ejercicio" (sin penalizar).
  const servir = useCallback(
    () =>
      conManejo(async () => {
        try {
          mostrar(await api.servirEjercicio(token, unidad));
        } catch (e) {
          if (e instanceof ErrorApi && e.estado === 404) {
            setEstado('sin-ejercicios');
            setMensaje(e.message);
            return;
          }
          throw e;
        }
      }),
    [conManejo, mostrar, token, unidad],
  );

  // Primer ejercicio al abrir la pantalla. El estado cambia recién cuando responde el servidor,
  // y se ignora la respuesta si la pantalla ya se cerró.
  useEffect(() => {
    let activa = true;
    api
      .servirEjercicio(token, unidad)
      .then((nuevo) => activa && mostrar(nuevo))
      .catch((e) => {
        if (!activa) return;
        if (e instanceof ErrorApi && e.estado === 401) cerrar();
        setEstado('sin-ejercicios');
        setMensaje(e instanceof ErrorApi ? e.message : 'Algo salió mal. Intenta otra vez.');
      });
    return () => {
      activa = false;
    };
  }, [token, unidad, mostrar, cerrar]);

  const actualizarProgreso = () => {
    clienteConsultas.invalidateQueries({ queryKey: ['perfil-estudiante'] });
    clienteConsultas.invalidateQueries({ queryKey: ['unidades'] });
  };

  const responder = () => {
    if (!ejercicio) return;
    if (estado === 'correcta') {
      servir();
      return;
    }
    Keyboard.dismiss();
    const respuesta =
      ejercicio.formatoRespuesta === 'fraccion' ? `${numerador}/${denominador}` : numerador;
    const segundos = Math.round((Date.now() - inicio.current) / 1000);
    conManejo(async () => {
      const r = await api.responder(token, ejercicio.servidoId, respuesta, segundos);
      setMensaje(r.mensaje);
      if (r.resultado === 'formato_invalido') return; // no cuenta como intento
      setPuedeNoEntiendo(r.resultado === 'incorrecta');
      setOfreceJuntos(r.ofreceResolverJuntos);
      setSeguidas((s) => (r.resultado === 'correcta' ? s + 1 : 0));
      if (r.resultado === 'correcta') setEstado('correcta');
      actualizarProgreso();
    });
  };

  const pedirPista = () =>
    ejercicio &&
    conManejo(async () => {
      const pista = await api.pedirPista(token, ejercicio.servidoId);
      setMensaje(pista.mensaje);
      setPistasRestantes(pista.pistasRestantes);
      setPuedeNoEntiendo(true);
    });

  const noEntiendo = () =>
    ejercicio &&
    conManejo(async () => {
      setMensaje((await api.noEntiendo(token, ejercicio.servidoId)).mensaje);
    });

  const resolverJuntos = () =>
    ejercicio &&
    conManejo(async () => {
      Keyboard.dismiss();
      const guiada = await api.resolverJuntos(token, ejercicio.servidoId);
      setPasos(guiada.pasos);
      setPasoGuiado(0);
      setAnalogo(guiada.analogo ?? null);
      setMensaje(guiada.pasos[0]);
      setEstado('guiada');
      actualizarProgreso();
    });

  const siguientePaso = () => {
    const siguiente = pasoGuiado + 1;
    setPasoGuiado(siguiente);
    setMensaje(pasos[siguiente]);
  };

  const probarParecido = () => {
    if (analogo) mostrar(analogo, '¡Ahora prueba este, que es parecido!');
    else servir();
  };

  if (estado === 'cargando' || estado === 'sin-ejercicios' || !ejercicio) {
    return (
      <SafeAreaView className="flex-1 items-center justify-center gap-4 bg-panel p-6">
        <Octavio tamano={g ? 120 : 88} conVarita />
        <Text
          className={`text-center font-nunito-bold text-apagado-oscuro ${g ? 'text-lg' : 'text-base'}`}
        >
          {estado === 'cargando' ? 'Octavio está eligiendo un ejercicio…' : mensaje}
        </Text>
        {estado !== 'cargando' && (
          <Pressable
            onPress={() => router.back()}
            className="rounded-full bg-primario px-6 py-3 active:bg-primario-oscuro"
          >
            <Text className="font-nunito-black text-white">Volver</Text>
          </Pressable>
        )}
      </SafeAreaView>
    );
  }

  const representacion = ejercicio.representacion as Representacion | null;
  const ultimoPaso = pasoGuiado === pasos.length - 1;

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
            {ejercicio.unidadDescripcion}
          </Text>
          <Text className={`font-nunito-bold text-lila ${g ? 'text-sm' : 'text-[11px]'}`}>
            Unidad {ejercicio.unidadId}
          </Text>
        </View>
        {perfil.data && (
          <View className="rounded-full bg-white px-3 py-1.5">
            <Text className={`font-nunito-black text-ambar ${g ? 'text-lg' : 'text-[13px]'}`}>
              ⭐ {conPuntoDeMiles(perfil.data.puntajeTotal)}
            </Text>
          </View>
        )}
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
        {representacion?.tipo === 'fraccion-circulo' && (
          <RepresentacionFraccion
            denominador={representacion.parametros.denominador}
            partesDestacadas={representacion.parametros.partesDestacadas}
            tamano={g ? 200 : 128}
          />
        )}
        <CampoRespuesta
          formato={ejercicio.formatoRespuesta === 'fraccion' ? 'fraccion' : 'numerico'}
          numerador={numerador}
          denominador={denominador}
          onCambio={(n, d) => {
            setNumerador(n);
            setDenominador(d);
          }}
          onEnviar={responder}
          deshabilitado={estado !== 'respondiendo' || ocupado}
          grande={g}
        />
      </View>
      {estado !== 'guiada' && (
        <BotonPrimario
          titulo={estado === 'correcta' ? 'Siguiente ejercicio →' : 'Responder'}
          onPress={responder}
          deshabilitado={ocupado}
          grande={g}
        />
      )}
    </View>
  );

  const tutor = (
    <GloboOctavio mensaje={ocupado ? 'Octavio está pensando…' : mensaje} grande={g}>
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
      {ofreceJuntos && (
        <BotonAccion
          texto="🤝 ¿Lo resolvemos juntos?"
          onPress={resolverJuntos}
          deshabilitado={ocupado}
          destacado
          grande={g}
        />
      )}
      <BotonAccion
        texto={`💡 Pista (quedan ${pistasRestantes})`}
        onPress={pedirPista}
        deshabilitado={pistasRestantes === 0 || ocupado}
        grande={g}
      />
      <BotonAccion
        texto="🤔 No entiendo"
        onPress={noEntiendo}
        deshabilitado={!puedeNoEntiendo || ocupado}
        grande={g}
      />
      <BotonAccion texto="↻ Otro ejercicio" onPress={servir} deshabilitado={ocupado} grande={g} />
    </View>
  );

  return (
    <SafeAreaView className="flex-1 bg-panel">
      {dosColumnas ? (
        <View className={`flex-1 flex-row ${g ? 'gap-8 px-8 pt-4' : 'gap-4 px-4 pt-2'}`}>
          <View className="flex-1">
            <ScrollView contentContainerClassName="gap-3 pb-4" keyboardShouldPersistTaps="handled">
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

export default function Ejercicio() {
  return (
    <Protegida rol="estudiante">
      <PantallaEjercicio />
    </Protegida>
  );
}
