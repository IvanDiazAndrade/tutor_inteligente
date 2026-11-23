import { Pressable, Text, View } from 'react-native';

// Lo que puede enviar el teclado: un dígito, la coma, borrar o moverse entre casillas.
export type Tecla =
  | '0'
  | '1'
  | '2'
  | '3'
  | '4'
  | '5'
  | '6'
  | '7'
  | '8'
  | '9'
  | ','
  | 'borrar'
  | 'anterior'
  | 'siguiente';

type Props = {
  onTecla: (tecla: Tecla) => void;
  decimal: boolean; // muestra la coma (respuestas numéricas)
  variasCasillas: boolean; // muestra las flechas para pasar de una casilla a otra (fracciones)
  deshabilitado?: boolean;
  grande?: boolean;
  compacto?: boolean; // teléfono en horizontal: hay poca altura
};

const FILAS: Tecla[][] = [
  ['7', '8', '9'],
  ['4', '5', '6'],
  ['1', '2', '3'],
  [',', '0', 'borrar'],
];

const ETIQUETAS: Partial<Record<Tecla, string>> = {
  ',': 'Coma',
  borrar: 'Borrar',
  anterior: 'Casilla anterior',
  siguiente: 'Casilla siguiente',
};
const SIMBOLOS: Partial<Record<Tecla, string>> = { borrar: '⌫', anterior: '◀', siguiente: '▶' };

// Teclado matemático propio, en lugar del teclado del sistema (RNF-U1): solo las teclas que
// piden los ejercicios, grandes y con el estilo de la app. Escribe en la casilla activa del
// campo de respuesta.
export function TecladoMatematico({
  onTecla,
  decimal,
  variasCasillas,
  deshabilitado = false,
  grande = false,
  compacto = false,
}: Props) {
  const alto = grande ? 'h-16' : compacto ? 'h-10' : 'h-12';
  const texto = grande ? 'text-3xl' : compacto ? 'text-xl' : 'text-2xl';

  const tecla = (t: Tecla, clase = '') => (
    <Pressable
      key={t}
      accessibilityRole="button"
      accessibilityLabel={ETIQUETAS[t] ?? t}
      accessibilityState={{ disabled: deshabilitado }}
      disabled={deshabilitado}
      onPress={() => onTecla(t)}
      className={`flex-1 items-center justify-center rounded-xl border-b-[3px] disabled:opacity-50 ${
        t === 'borrar' || t === 'anterior' || t === 'siguiente'
          ? 'border-lila-suave bg-lila-fondo active:bg-lila-suave'
          : 'border-borde bg-white active:bg-fondo'
      } ${clase}`}
    >
      <Text
        className={`font-nunito-black ${texto} ${
          t === 'borrar' || t === 'anterior' || t === 'siguiente'
            ? 'text-primario'
            : 'text-tinta-tecla'
        }`}
      >
        {SIMBOLOS[t] ?? t}
      </Text>
    </Pressable>
  );

  return (
    <View
      className={`w-full flex-row self-center ${grande ? 'max-w-[560px] gap-2' : 'gap-1.5'}`}
      accessibilityLabel="Teclado para escribir la respuesta"
    >
      <View className={`flex-[3] ${grande ? 'gap-2' : 'gap-1.5'}`}>
        {FILAS.map((fila, i) => (
          <View key={i} className={`flex-row ${alto} ${grande ? 'gap-2' : 'gap-1.5'}`}>
            {fila.map((t) =>
              t === ',' && !decimal ? <View key="sin-coma" className="flex-1" /> : tecla(t),
            )}
          </View>
        ))}
      </View>
      {variasCasillas && (
        <View className={`flex-1 ${grande ? 'gap-2' : 'gap-1.5'}`}>
          {tecla('anterior')}
          {tecla('siguiente')}
        </View>
      )}
    </View>
  );
}
