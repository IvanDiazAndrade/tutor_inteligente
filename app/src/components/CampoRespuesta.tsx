import { useEffect, useImperativeHandle, useState } from 'react';
import { Animated, Pressable, Text, View } from 'react-native';

import { RespuestaComparar } from '@/components/RespuestaComparar';
import { RespuestaOrdenar } from '@/components/RespuestaOrdenar';
import type { Tecla } from '@/components/TecladoMatematico';

// Lo que la pantalla puede hacer con el campo: reenviarle lo que se toca en el teclado.
export type ControlCampo = { tecla: (tecla: Tecla) => void };

type Formato = 'fraccion' | 'numerico' | 'ordenar' | 'comparar';

type Props = {
  formato: Formato;
  entradaMixta?: boolean; // agrega una casilla para el entero del número mixto
  valores?: string[]; // los que hay que ordenar o comparar
  onCambio: (respuesta: string) => void; // respuesta como la espera el corrector; vacía si falta
  deshabilitado?: boolean;
  grande?: boolean;
  ref?: React.Ref<ControlCampo>;
  editando?: boolean; // el teclado está abierto: se marca la casilla activa con el cursor
  onEditar?: () => void; // se tocó una casilla: hay que abrir el teclado
};

// Los formatos que se escriben con el teclado matemático (los otros se responden tocando).
export const usaTeclado = (formato: Formato) => formato === 'numerico' || formato === 'fraccion';

// Elegir <, = o >, con los dos valores a la vista.
function CampoComparar({ valores = [], onCambio, deshabilitado, grande }: Props) {
  const [elegido, setElegido] = useState('');
  return (
    <RespuestaComparar
      izquierda={valores[0] ?? ''}
      derecha={valores[1] ?? ''}
      simbolo={elegido}
      onCambio={(simbolo) => {
        setElegido(simbolo);
        onCambio(simbolo);
      }}
      deshabilitado={deshabilitado}
      grande={grande}
    />
  );
}

// Ordenar: se tocan los valores en el orden pedido.
function CampoOrdenar({ valores = [], onCambio, deshabilitado, grande }: Props) {
  const [orden, setOrden] = useState<string[]>([]);
  return (
    <RespuestaOrdenar
      valores={valores}
      seleccion={orden}
      onCambio={(nuevo) => {
        setOrden(nuevo);
        // Como lo lee el corrector: "1/4; 0,5; 1 1/2". Vacía hasta que estén todos.
        onCambio(nuevo.length === valores.length ? nuevo.join('; ') : '');
      }}
      deshabilitado={deshabilitado}
      grande={grande}
    />
  );
}

// Casillas guiadas: cada parte de la respuesta tiene su casilla (entero, numerador y
// denominador, o un solo número) y el teclado escribe en la que está activa.
type Casilla = { etiqueta: string; largo: number; decimal?: boolean };

const NUMERO: Casilla[] = [{ etiqueta: 'Tu respuesta', largo: 13, decimal: true }];
const FRACCION: Casilla[] = [
  { etiqueta: 'Numerador, el número de arriba', largo: 4 },
  { etiqueta: 'Denominador, el número de abajo', largo: 4 },
];
const MIXTO: Casilla[] = [{ etiqueta: 'Número entero', largo: 4 }, ...FRACCION];

type Escrito = { valores: string[]; activa: number };

function aplicar({ valores, activa }: Escrito, tecla: Tecla, casillas: Casilla[]): Escrito {
  const ultima = casillas.length - 1;
  if (tecla === 'anterior') return { valores, activa: Math.max(0, activa - 1) };
  if (tecla === 'siguiente') return { valores, activa: Math.min(ultima, activa + 1) };
  const valor = valores[activa];
  // Borrar en una casilla vacía vuelve a la anterior, como en una calculadora.
  if (tecla === 'borrar' && !valor) return { valores, activa: Math.max(0, activa - 1) };
  let nuevo = valor;
  if (tecla === 'borrar') nuevo = valor.slice(0, -1);
  else if (tecla === ',') {
    if (!casillas[activa].decimal || valor.includes(',')) return { valores, activa };
    nuevo = (valor || '0') + ',';
  } else if (valor.length < casillas[activa].largo) {
    nuevo = valor === '0' ? tecla : valor + tecla; // sin ceros a la izquierda
  }
  return { valores: valores.map((v, i) => (i === activa ? nuevo : v)), activa };
}

// Respuesta como la espera el corrector: "0,75", "3/4" o "2 1/3"; vacía si no hay nada escrito.
function armar(valores: string[], formato: Formato, mixto: boolean) {
  if (formato === 'numerico') return valores[0];
  const [entero, numerador, denominador] = mixto ? valores : ['', ...valores];
  const fraccion = numerador || denominador ? `${numerador}/${denominador}` : '';
  return [entero, fraccion].filter(Boolean).join(' '); // un entero solo ("4") también vale
}

// Se muestra con punto de miles (convención chilena): 12500 -> 12.500. Al corrector va sin él.
const conMiles = (valor: string) => {
  const [entero, decimales] = valor.split(',');
  const conPuntos = entero.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
  return decimales === undefined ? conPuntos : `${conPuntos},${decimales}`;
};

function Cursor({ grande }: { grande: boolean }) {
  const [opacidad] = useState(() => new Animated.Value(1));
  useEffect(() => {
    const parpadeo = Animated.loop(
      Animated.sequence([
        Animated.timing(opacidad, { toValue: 0, duration: 500, delay: 300, useNativeDriver: true }),
        Animated.timing(opacidad, { toValue: 1, duration: 200, useNativeDriver: true }),
      ]),
    );
    parpadeo.start();
    return () => parpadeo.stop();
  }, [opacidad]);
  return (
    <Animated.View
      style={{ opacity: opacidad }}
      className={`ml-0.5 w-[3px] rounded-full bg-primario ${grande ? 'h-10' : 'h-7'}`}
    />
  );
}

function CajaCasilla({
  casilla,
  valor,
  activa,
  onPress,
  deshabilitado,
  grande,
  ancho,
}: {
  casilla: Casilla;
  valor: string;
  activa: boolean;
  onPress: () => void;
  deshabilitado: boolean;
  grande: boolean;
  ancho: string;
}) {
  const marcada = activa && !deshabilitado;
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityLabel={`${casilla.etiqueta}: ${valor || 'vacía'}`}
      accessibilityState={{ selected: marcada, disabled: deshabilitado }}
      disabled={deshabilitado}
      onPress={onPress}
      className={`flex-row items-center justify-center rounded-2xl border-[2.5px] bg-fondo px-2 ${ancho} ${
        grande ? 'h-20' : 'h-16'
      } ${marcada ? 'border-primario' : 'border-lila-suave'}`}
    >
      {valor ? (
        <Text
          numberOfLines={1}
          adjustsFontSizeToFit
          className={`font-nunito-black text-tinta ${grande ? 'text-4xl' : 'text-[32px]'}`}
        >
          {casilla.decimal ? conMiles(valor) : valor}
        </Text>
      ) : (
        !marcada && (
          <Text className={`font-nunito-black text-lila ${grande ? 'text-4xl' : 'text-[32px]'}`}>
            ?
          </Text>
        )
      )}
      {marcada && <Cursor grande={grande} />}
    </Pressable>
  );
}

function CampoCasillas({
  formato,
  entradaMixta = false,
  onCambio,
  deshabilitado = false,
  grande = false,
  ref,
  editando = true,
  onEditar,
}: Props) {
  const casillas = formato === 'numerico' ? NUMERO : entradaMixta ? MIXTO : FRACCION;
  const [escrito, setEscrito] = useState<Escrito>({ valores: casillas.map(() => ''), activa: 0 });

  useImperativeHandle(ref, () => ({ tecla: (t) => setEscrito((e) => aplicar(e, t, casillas)) }), [
    casillas,
  ]);
  useEffect(() => {
    onCambio(armar(escrito.valores, formato, entradaMixta));
  }, [escrito.valores, formato, entradaMixta, onCambio]);

  const caja = (i: number, ancho: string) => (
    <CajaCasilla
      casilla={casillas[i]}
      valor={escrito.valores[i]}
      activa={editando && escrito.activa === i}
      onPress={() => {
        setEscrito((e) => ({ ...e, activa: i }));
        onEditar?.();
      }}
      deshabilitado={deshabilitado}
      grande={grande}
      ancho={ancho}
    />
  );

  if (formato === 'numerico') return caja(0, grande ? 'w-80' : 'w-56');

  const anchoFraccion = grande ? 'w-28' : 'w-[88px]';
  const primera = entradaMixta ? 1 : 0;
  return (
    <View className="flex-row items-center gap-3">
      {entradaMixta && caja(0, anchoFraccion)}
      <View className="items-center gap-2">
        {caja(primera, anchoFraccion)}
        <View className={`h-[5px] rounded-full bg-primario ${grande ? 'w-32' : 'w-[92px]'}`} />
        {caja(primera + 1, anchoFraccion)}
      </View>
    </View>
  );
}

// Campo de respuesta según el formato del ejercicio (RF-D7). Guarda lo escrito y avisa a la
// pantalla la respuesta ya armada; para vaciarlo entre ejercicios, cambiar su `key`.
export function CampoRespuesta(props: Props) {
  if (props.formato === 'comparar') return <CampoComparar {...props} />;
  if (props.formato === 'ordenar') return <CampoOrdenar {...props} />;
  return <CampoCasillas {...props} />;
}
