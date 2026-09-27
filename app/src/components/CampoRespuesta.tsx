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
};

// Casilla para una cifra: teclado numérico del sistema, solo dígitos (RF-D7).
function Casilla({
  valor,
  onCambio,
  etiqueta,
  deshabilitado,
  grande,
  ancho,
  onEnviar,
  ref,
}: {
  valor: string;
  onCambio: (v: string) => void;
  etiqueta: string;
  deshabilitado: boolean;
  grande: boolean;
  ancho: string;
  onEnviar?: () => void;
  ref?: React.Ref<TextInput>;
}) {
  return (
    <TextInput
      ref={ref}
      accessibilityLabel={etiqueta}
      value={valor}
      onChangeText={(v) => onCambio(v.replace(/\D/g, '').slice(0, 4))}
      keyboardType="number-pad"
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
}: Props) {
  const abajo = useRef<TextInput>(null);

  if (formato === 'numerico') {
    return (
      <Casilla
        valor={numerador}
        onCambio={(v) => onCambio(v, '')}
        etiqueta="Tu respuesta"
        deshabilitado={deshabilitado}
        grande={grande}
        ancho={grande ? 'w-44' : 'w-32'}
        onEnviar={onEnviar}
      />
    );
  }

  return (
    <View className="items-center gap-2">
      <Casilla
        valor={numerador}
        onCambio={(v) => onCambio(v, denominador)}
        etiqueta="Numerador, el número de arriba"
        deshabilitado={deshabilitado}
        grande={grande}
        ancho={grande ? 'w-28' : 'w-[74px]'}
        onEnviar={() => abajo.current?.focus()}
      />
      <View className={`h-[5px] rounded-full bg-primario ${grande ? 'w-32' : 'w-[78px]'}`} />
      <Casilla
        ref={abajo}
        valor={denominador}
        onCambio={(v) => onCambio(numerador, v)}
        etiqueta="Denominador, el número de abajo"
        deshabilitado={deshabilitado}
        grande={grande}
        ancho={grande ? 'w-28' : 'w-[74px]'}
        onEnviar={onEnviar}
      />
    </View>
  );
}
