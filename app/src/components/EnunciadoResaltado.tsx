import { Text, View } from 'react-native';

// Colores de las fracciones, los mismos de la figura: el texto y la raya de cada una.
const COLORES = [
  { texto: 'text-primario', raya: 'bg-primario' },
  { texto: 'text-ambar', raya: 'bg-ambar' },
];

// Número mixto ("2 3/4") o fracción ("3/4").
const FRACCION = /(\d+ \d+\/\d+|\d+\/\d+)/;

type Pieza =
  { texto: string } | { entero?: string; numerador: string; denominador: string; color: number };

// Separa el enunciado en palabras. Una fracción queda pegada a lo que no tiene espacio entre
// medio ("1/2." o "(3/4"), para que el salto de línea no deje el punto solo al inicio.
function palabras(texto: string): Pieza[][] {
  const resultado: Pieza[][] = [];
  let actual: Pieza[] = [];
  let fracciones = 0;
  for (const trozo of texto.split(FRACCION)) {
    if (FRACCION.test(trozo)) {
      const [entero, fraccion] = trozo.includes(' ') ? trozo.split(' ') : [undefined, trozo];
      const [numerador, denominador] = fraccion.split('/');
      actual.push({ entero, numerador, denominador, color: fracciones++ % COLORES.length });
      continue;
    }
    trozo.split(' ').forEach((parte, i) => {
      if (i > 0 && actual.length) {
        resultado.push(actual);
        actual = [];
      }
      if (parte) actual.push({ texto: parte });
    });
  }
  if (actual.length) resultado.push(actual);
  return resultado;
}

export const cuantasPalabras = (texto: string) => palabras(texto).length;

// Enunciado del ejercicio con las fracciones escritas como en el cuaderno: numerador sobre
// denominador, resaltadas en los mismos colores de la figura. Con `visibles` se muestran solo
// las primeras palabras (la lección las va diciendo); las demás ocupan ya su lugar.
export function EnunciadoResaltado({
  texto,
  grande = false,
  visibles = Infinity,
}: {
  texto: string;
  grande?: boolean;
  visibles?: number;
}) {
  const letra = `font-nunito-bold text-tinta-media ${grande ? 'text-2xl leading-9' : 'text-[22px] leading-8'}`;
  const cifra = `font-nunito-black ${grande ? 'text-2xl leading-8' : 'text-xl leading-6'}`;
  return (
    <View
      accessible
      accessibilityLabel={texto.replace(/(\d+)\/(\d+)/g, '$1 sobre $2')}
      className="flex-row flex-wrap items-center gap-x-1.5 gap-y-1"
    >
      {palabras(texto).map((palabra, i) => (
        <View key={i} className="flex-row items-center" style={{ opacity: i < visibles ? 1 : 0 }}>
          {palabra.map((pieza, j) =>
            'texto' in pieza ? (
              <Text key={j} className={letra}>
                {pieza.texto}
              </Text>
            ) : (
              <View key={j} className={`flex-row items-center ${grande ? 'mx-1' : 'mx-0.5'}`}>
                {pieza.entero && (
                  <Text
                    className={`font-nunito-black ${COLORES[pieza.color].texto} ${
                      grande ? 'mr-1 text-3xl' : 'mr-0.5 text-2xl'
                    }`}
                  >
                    {pieza.entero}
                  </Text>
                )}
                <View className="items-center">
                  <Text className={`${cifra} ${COLORES[pieza.color].texto}`}>
                    {pieza.numerador}
                  </Text>
                  <View
                    className={`self-stretch rounded-full ${grande ? 'h-[3px]' : 'h-[2px]'} ${
                      COLORES[pieza.color].raya
                    }`}
                  />
                  <Text className={`${cifra} ${COLORES[pieza.color].texto}`}>
                    {pieza.denominador}
                  </Text>
                </View>
              </View>
            ),
          )}
        </View>
      ))}
    </View>
  );
}
