import { useEffect, useImperativeHandle, useState } from 'react';
import { Animated, Pressable, Text, View } from 'react-native';

import type { Tecla } from '@/components/TecladoMatematico';

// Lo que la pantalla puede hacer con el campo: reenviarle lo que se toca en el teclado.
export type ControlCampo = { tecla: (tecla: Tecla) => void };

type Formato = 'fraccion' | 'numerico' | 'ordenar' | 'comparar';

type Props = {
  formato: Formato;
  entradaMixta?: boolean; // agrega una casilla para el entero del número mixto
  valores?: string[]; // los valores que hay que ordenar (formato "ordenar")
  onCambio: (respuesta: string) => void; // respuesta como la espera el corrector; vacía si falta
  deshabilitado?: boolean;
  grande?: boolean;
  ref?: React.Ref<ControlCampo>;
  editando?: boolean; // el teclado está abierto: se marca la casilla activa con el cursor
  onEditar?: () => void; // se tocó una casilla: hay que abrir el teclado
};

// Los formatos que se escriben con el teclado matemático (los otros se responden tocando).
export const usaTeclado = (formato: Formato) => formato === 'numerico' || formato === 'fraccion';

const SIGNOS = ['<', '=', '>'];

// Elegir <, = o >.
function CampoComparar({ onCambio, deshabilitado, grande }: Props) {
  const [elegido, setElegido] = useState('');
  return (
    <View className="flex-row justify-center gap-3" accessibilityRole="radiogroup">
      {SIGNOS.map((signo) => (
        <Pressable
          key={signo}
          accessibilityRole="radio"
          accessibilityLabel={signo === '<' ? 'Menor que' : signo === '>' ? 'Mayor que' : 'Igual a'}
          accessibilityState={{ selected: elegido === signo, disabled: deshabilitado }}
          disabled={deshabilitado}
          onPress={() => {
            setElegido(signo);
            onCambio(signo);
          }}
          className={`items-center justify-center rounded-2xl border-[2.5px] ${
            elegido === signo ? 'border-primario bg-primario' : 'border-lila-suave bg-fondo'
          } ${grande ? 'h-20 w-20' : 'h-14 w-14'}`}
        >
          <Text
            className={`font-nunito-black ${elegido === signo ? 'text-white' : 'text-tinta'} ${
              grande ? 'text-4xl' : 'text-[26px]'
            }`}
          >
            {signo}
          </Text>
        </Pressable>
      ))}
    </View>
  );
}

// Ordenar: se tocan los valores en orden; tocar uno ya elegido lo devuelve.
function CampoOrdenar({ valores = [], onCambio, deshabilitado, grande }: Props) {
  const [orden, setOrden] = useState<string[]>([]);
  const cambiar = (nuevo: string[]) => {
    setOrden(nuevo);
    onCambio(nuevo.length === valores.length ? nuevo.join('; ') : '');
  };
  const ficha = (valor: string, elegida: boolean, posicion?: number) => (
    <Pressable
      key={valor}
      accessibilityRole="button"
      accessibilityLabel={
        elegida ? `Posición ${posicion}: ${valor}. Tocar para quitar` : `Elegir ${valor}`
      }
      disabled={deshabilitado}
      onPress={() => cambiar(elegida ? orden.filter((v) => v !== valor) : [...orden, valor])}
      className={`min-h-12 flex-row items-center justify-center gap-2 rounded-2xl border-[2.5px] px-3 py-2 ${
        elegida ? 'border-primario bg-lila-fondo' : 'border-lila-suave bg-fondo'
      }`}
    >
      {elegida && (
        <Text className={`font-nunito-black text-primario ${grande ? 'text-lg' : 'text-sm'}`}>
          {posicion}.
        </Text>
      )}
      <Text className={`font-nunito-black text-tinta ${grande ? 'text-2xl' : 'text-lg'}`}>
        {valor}
      </Text>
    </Pressable>
  );
  return (
    <View className="w-full gap-3">
      <View className="gap-1.5">
        <Text className={`font-nunito-bold text-lila ${grande ? 'text-base' : 'text-xs'}`}>
          Toca de menor a mayor:
        </Text>
        <View className="min-h-12 flex-row flex-wrap gap-2">
          {valores.filter((v) => !orden.includes(v)).map((v) => ficha(v, false))}
        </View>
      </View>
      <View className="gap-1.5">
        <Text className={`font-nunito-bold text-lila ${grande ? 'text-base' : 'text-xs'}`}>
          Tu orden:
        </Text>
        <View className="min-h-12 flex-row flex-wrap gap-2">
          {orden.map((v, i) => ficha(v, true, i + 1))}
        </View>
      </View>
    </View>
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
        grande ? 'h-20' : 'h-14'
      } ${marcada ? 'border-primario' : 'border-lila-suave'}`}
    >
      {valor ? (
        <Text
          numberOfLines={1}
          adjustsFontSizeToFit
          className={`font-nunito-black text-tinta ${grande ? 'text-4xl' : 'text-[26px]'}`}
        >
          {casilla.decimal ? conMiles(valor) : valor}
        </Text>
      ) : (
        !marcada && (
          <Text className={`font-nunito-black text-lila ${grande ? 'text-4xl' : 'text-[26px]'}`}>
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

  if (formato === 'numerico') return caja(0, grande ? 'w-80' : 'w-52');

  const anchoFraccion = grande ? 'w-28' : 'w-[74px]';
  const primera = entradaMixta ? 1 : 0;
  return (
    <View className="flex-row items-center gap-3">
      {entradaMixta && caja(0, anchoFraccion)}
      <View className="items-center gap-2">
        {caja(primera, anchoFraccion)}
        <View className={`h-[5px] rounded-full bg-primario ${grande ? 'w-32' : 'w-[78px]'}`} />
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
