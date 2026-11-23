import type { ReactNode } from 'react';
import { Text, View } from 'react-native';

import { Octavio } from '@/components/Octavio';

type Props = { mensaje: string; grande?: boolean; children?: ReactNode };

// Operación en columnas que trae una pista después de su frase (backend: dominio/columnas.py),
// con letra de ancho fijo para que las columnas queden alineadas, como en el cuaderno.
// - Suma y resta: marcas (reservas o canjes, en ámbar), números, raya y resultado (en morado).
// - División: "dividendo : divisor = cociente" (cociente en morado) y debajo las restas.
const MONO = { fontFamily: 'monospace', fontWeight: 'bold' } as const;

function OperacionEnColumnas({ bloque, grande }: { bloque: string; grande: boolean }) {
  const lineas = bloque.split('\n');
  const ultima = lineas.length - 1;
  const esDivision = lineas[0].includes(' : ') && lineas[0].includes('=');
  const tamano = grande ? 'text-2xl leading-8' : 'text-lg leading-6';

  const linea = (texto: string, i: number) => {
    const contenido = texto.trimStart();
    // La raya con caracteres se ve cortada en tramos: se dibuja una línea continua del mismo
    // ancho (los caracteres quedan invisibles solo para medirla), con su sangría.
    if (contenido.startsWith('─')) {
      return (
        <View key={i} className="flex-row">
          <Text style={MONO} className={`${tamano} text-transparent`}>
            {texto.slice(0, texto.length - contenido.length)}
          </Text>
          <View className="justify-center">
            <Text style={MONO} className={`${tamano} text-transparent`}>
              {contenido}
            </Text>
            <View className="absolute left-0 right-0 h-[3px] rounded-full bg-tinta" />
          </View>
        </View>
      );
    }
    if (esDivision && i === 0) {
      const [operacion, cociente] = texto.split('=');
      return (
        <Text key={i} style={MONO} className={`${tamano} text-tinta`}>
          {operacion}=<Text className="text-primario">{cociente}</Text>
        </Text>
      );
    }
    const color = esDivision
      ? 'text-tinta'
      : i === 0
        ? 'text-ambar'
        : i === ultima
          ? 'text-primario'
          : 'text-tinta';
    return (
      <Text key={i} style={MONO} className={`${tamano} ${color}`}>
        {texto || ' '}
      </Text>
    );
  };

  return (
    <View
      accessible
      accessibilityLabel={`Operación escrita: ${lineas
        .filter((l) => l.trim() && !l.trim().startsWith('─'))
        .map((l) => l.replace(/\s+/g, ''))
        .join(', ')}`}
      className={`self-start rounded-xl bg-fondo ${grande ? 'px-5 py-3' : 'px-3.5 py-2'}`}
    >
      {lineas.map(linea)}
    </View>
  );
}

// Zona del tutor: Octavio con su globo de diálogo (mockup "Ejercicio Estudiante").
// Los botones propios del momento (p. ej. "Siguiente →") van como children dentro del globo.
export function GloboOctavio({ mensaje, grande = false, children }: Props) {
  const corte = mensaje.indexOf('\n');
  const frase = corte < 0 ? mensaje : mensaje.slice(0, corte);
  const bloque = corte < 0 ? null : mensaje.slice(corte + 1);
  return (
    <View className="flex-row items-end gap-2">
      <Octavio tamano={grande ? 160 : 96} tutor />
      <View
        className={`mb-6 flex-1 gap-3 rounded-[18px] border-2 border-globo bg-white ${
          grande ? 'px-5 py-4' : 'px-3.5 py-3'
        }`}
      >
        <Text
          accessibilityLiveRegion="polite"
          className={`font-nunito-bold text-tinta-tecla ${grande ? 'text-xl leading-7' : 'text-sm leading-5'}`}
        >
          {frase}
        </Text>
        {bloque && <OperacionEnColumnas bloque={bloque} grande={grande} />}
        {children}
      </View>
    </View>
  );
}
