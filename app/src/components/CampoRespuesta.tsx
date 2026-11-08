import { useRef, useState } from 'react';
import { Pressable, Text, TextInput, View } from 'react-native';

type Props = {
  formato: 'fraccion' | 'numerico' | 'ordenar' | 'comparar';
  entradaMixta?: boolean; // agrega una casilla para el entero del número mixto
  valores?: string[]; // los valores que hay que ordenar (formato "ordenar")
  onCambio: (respuesta: string) => void; // respuesta como la espera el corrector; vacía si falta
  onEnviar: () => void;
  deshabilitado?: boolean;
  grande?: boolean;
};

const SIGNOS = ['<', '=', '>'];

// Casilla para escribir un número. Los decimales llevan coma o punto: el corrector acepta ambos.
function Casilla({
  valor,
  onCambio,
  etiqueta,
  deshabilitado,
  grande,
  ancho,
  onEnviar,
  decimal = false,
  ref,
}: {
  valor: string;
  onCambio: (v: string) => void;
  etiqueta: string;
  deshabilitado: boolean;
  grande: boolean;
  ancho: string;
  onEnviar?: () => void;
  decimal?: boolean;
  ref?: React.Ref<TextInput>;
}) {
  return (
    <TextInput
      ref={ref}
      accessibilityLabel={etiqueta}
      value={valor}
      onChangeText={(v) =>
        onCambio(
          decimal ? v.replace(/[^\d.,]/g, '').slice(0, 13) : v.replace(/\D/g, '').slice(0, 4),
        )
      }
      keyboardType={decimal ? 'decimal-pad' : 'number-pad'}
      placeholder="?"
      placeholderTextColor="#A78BFA"
      editable={!deshabilitado}
      returnKeyType={onEnviar ? 'done' : 'next'}
      onSubmitEditing={onEnviar}
      // Android agrega relleno vertical propio: sin esto el "?" queda descentrado.
      style={{ paddingVertical: 0, textAlignVertical: 'center' }}
      className={`rounded-2xl border-[2.5px] border-lila-suave bg-fondo text-center font-nunito-black text-tinta focus:border-primario ${ancho} ${
        grande ? 'h-20 text-4xl' : 'h-14 text-[26px]'
      }`}
    />
  );
}

// Elegir <, = o >.
function CampoComparar({ onCambio, deshabilitado, grande }: Omit<Props, 'formato' | 'onEnviar'>) {
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
function CampoOrdenar({
  valores = [],
  onCambio,
  deshabilitado,
  grande,
}: Omit<Props, 'formato' | 'onEnviar'>) {
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

// Fracción: numerador sobre denominador y, si corresponde, el entero del número mixto.
function CampoFraccion({
  entradaMixta,
  onCambio,
  onEnviar,
  deshabilitado = false,
  grande = false,
}: Omit<Props, 'formato'>) {
  const [entero, setEntero] = useState('');
  const [numerador, setNumerador] = useState('');
  const [denominador, setDenominador] = useState('');
  const arriba = useRef<TextInput>(null);
  const abajo = useRef<TextInput>(null);

  // Un entero solo es válido ("4"); sin la fracción completa, el corrector pide completarla.
  const cambiar = (e: string, n: string, d: string) => {
    setEntero(e);
    setNumerador(n);
    setDenominador(d);
    const fraccion = n || d ? `${n}/${d}` : '';
    onCambio([e, fraccion].filter(Boolean).join(' '));
  };
  const anchoFraccion = grande ? 'w-28' : 'w-[74px]';

  return (
    <View className="flex-row items-center gap-3">
      {entradaMixta && (
        <Casilla
          valor={entero}
          onCambio={(v) => cambiar(v, numerador, denominador)}
          etiqueta="Número entero"
          deshabilitado={deshabilitado}
          grande={grande}
          ancho={anchoFraccion}
          onEnviar={() => arriba.current?.focus()}
        />
      )}
      <View className="items-center gap-2">
        <Casilla
          ref={arriba}
          valor={numerador}
          onCambio={(v) => cambiar(entero, v, denominador)}
          etiqueta="Numerador, el número de arriba"
          deshabilitado={deshabilitado}
          grande={grande}
          ancho={anchoFraccion}
          onEnviar={() => abajo.current?.focus()}
        />
        <View className={`h-[5px] rounded-full bg-primario ${grande ? 'w-32' : 'w-[78px]'}`} />
        <Casilla
          ref={abajo}
          valor={denominador}
          onCambio={(v) => cambiar(entero, numerador, v)}
          etiqueta="Denominador, el número de abajo"
          deshabilitado={deshabilitado}
          grande={grande}
          ancho={anchoFraccion}
          onEnviar={onEnviar}
        />
      </View>
    </View>
  );
}

function CampoNumero({
  onCambio,
  onEnviar,
  deshabilitado = false,
  grande = false,
}: Omit<Props, 'formato'>) {
  const [valor, setValor] = useState('');
  return (
    <Casilla
      decimal
      valor={valor}
      onCambio={(v) => {
        setValor(v);
        onCambio(v);
      }}
      etiqueta="Tu respuesta"
      deshabilitado={deshabilitado}
      grande={grande}
      ancho={grande ? 'w-80' : 'w-52'}
      onEnviar={onEnviar}
    />
  );
}

// Campo de respuesta según el formato del ejercicio (RF-D7). Guarda lo escrito y avisa a la
// pantalla la respuesta ya armada; para vaciarlo entre ejercicios, cambiar su `key`.
export function CampoRespuesta({ formato, ...props }: Props) {
  if (formato === 'comparar') return <CampoComparar {...props} />;
  if (formato === 'ordenar') return <CampoOrdenar {...props} />;
  if (formato === 'fraccion') return <CampoFraccion {...props} />;
  return <CampoNumero {...props} />;
}
