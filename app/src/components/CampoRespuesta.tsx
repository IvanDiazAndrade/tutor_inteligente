import { useRef } from 'react';
import { TextInput, View } from 'react-native';

type Props = {
  formato: 'fraccion' | 'numerico';
  numerador: string;
  denominador: string;
  onCambio: (numerador: string, denominador: string) => void;
  onEnviar: () => void;
  deshabilitado?: boolean;
  grande?: boolean;
  // Número mixto: una casilla más, a la izquierda, para la parte entera (opcional).
  mixto?: boolean;
  entero?: string;
  onEntero?: (entero: string) => void;
};

// Casilla de respuesta con el teclado numérico del sistema (RF-D7). En las de fracción van solo
// dígitos; en la numérica también la coma decimal y el punto de miles (0,75 o 81.500.000), que
// el corrector acepta (modelo_dominio.md §3.1).
function Casilla({
  valor,
  onCambio,
  etiqueta,
  deshabilitado,
  grande,
  ancho,
  onEnviar,
  ref,
  decimal = false,
}: {
  valor: string;
  onCambio: (v: string) => void;
  etiqueta: string;
  deshabilitado: boolean;
  grande: boolean;
  ancho: string;
  onEnviar?: () => void;
  ref?: React.Ref<TextInput>;
  decimal?: boolean;
}) {
  // Una respuesta larga achica la letra para que quepa en la casilla.
  const largo = valor.length > 6;
  return (
    <TextInput
      ref={ref}
      accessibilityLabel={etiqueta}
      value={valor}
      onChangeText={(v) =>
        onCambio(
          decimal ? v.replace(/[^\d.,]/g, '').slice(0, 12) : v.replace(/\D/g, '').slice(0, 4),
        )
      }
      // "numeric" trae la coma y el punto; "number-pad", solo dígitos.
      keyboardType={decimal ? 'numeric' : 'number-pad'}
      // En horizontal Android abre el teclado a pantalla completa y tapa el ejercicio.
      disableFullscreenUI
      placeholder="?"
      placeholderTextColor="#A78BFA"
      editable={!deshabilitado}
      returnKeyType={onEnviar ? 'done' : 'next'}
      onSubmitEditing={onEnviar}
      // Android agrega relleno vertical propio: sin esto el "?" queda descentrado.
      style={{ paddingVertical: 0, textAlignVertical: 'center' }}
      className={`rounded-2xl border-[2.5px] border-lila-suave bg-fondo text-center font-nunito-black text-tinta focus:border-primario ${ancho} ${
        grande
          ? `h-20 ${largo ? 'text-3xl' : 'text-4xl'}`
          : `h-16 ${largo ? 'text-2xl' : 'text-[32px]'}`
      }`}
    />
  );
}

// Campo de respuesta según el formato del ejercicio: fracción (numerador sobre denominador)
// o número. El formato "ordenar/comparar" se agrega cuando haya un ejercicio de ese tipo.
export function CampoRespuesta({
  formato,
  numerador,
  denominador,
  onCambio,
  onEnviar,
  deshabilitado = false,
  grande = false,
  mixto = false,
  entero = '',
  onEntero,
}: Props) {
  const arriba = useRef<TextInput>(null);
  const abajo = useRef<TextInput>(null);

  if (formato === 'numerico') {
    return (
      <Casilla
        valor={numerador}
        onCambio={(v) => onCambio(v, '')}
        etiqueta="Tu respuesta"
        deshabilitado={deshabilitado}
        grande={grande}
        // Más ancha que las de fracción: hay respuestas como 81.500.000 o 30,543.
        ancho={grande ? 'w-72' : 'w-56'}
        onEnviar={onEnviar}
        decimal
      />
    );
  }

  const fraccion = (
    <View className="items-center gap-2">
      <Casilla
        ref={arriba}
        valor={numerador}
        onCambio={(v) => onCambio(v, denominador)}
        etiqueta="Numerador, el número de arriba"
        deshabilitado={deshabilitado}
        grande={grande}
        ancho={grande ? 'w-28' : 'w-[88px]'}
        onEnviar={() => abajo.current?.focus()}
      />
      <View className={`h-[5px] rounded-full bg-primario ${grande ? 'w-32' : 'w-[92px]'}`} />
      <Casilla
        ref={abajo}
        valor={denominador}
        onCambio={(v) => onCambio(numerador, v)}
        etiqueta="Denominador, el número de abajo"
        deshabilitado={deshabilitado}
        grande={grande}
        ancho={grande ? 'w-28' : 'w-[88px]'}
        onEnviar={onEnviar}
      />
    </View>
  );

  if (!mixto) return fraccion;
  return (
    <View className="flex-row items-center gap-3">
      <Casilla
        valor={entero}
        onCambio={(v) => onEntero?.(v)}
        etiqueta="Parte entera del número mixto (si no hay, déjala vacía)"
        deshabilitado={deshabilitado}
        grande={grande}
        ancho={grande ? 'w-28' : 'w-[88px]'}
        onEnviar={() => arriba.current?.focus()}
      />
      {fraccion}
    </View>
  );
}
