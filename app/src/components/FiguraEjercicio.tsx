import Svg, { Circle, Line, Rect, Text as TextoSvg } from 'react-native-svg';

import { RepresentacionFraccion } from '@/components/RepresentacionFraccion';

const MORADO = '#6D28D9';
const MORADO_CLARO = '#8B5CF6';
const AMBAR = '#F59E0B';

// Representación del ejercicio, tal como la guarda el banco (modelo_dominio.md §6).
export type Representacion =
  | { tipo: 'fraccion-circulo'; parametros: { denominador: number; partesDestacadas: number[] } }
  | {
      tipo: 'recta-numerica';
      parametros: { minimo: number; maximo: number; divisiones: number; punto: number };
    }
  | { tipo: 'cuadricula-decimal'; parametros: { pintadas: number } }
  | { tipo: 'valores-ordenar'; parametros: { valores: string[] } };

// Recta numérica: marcas iguales, los enteros con número y un punto en la marca pedida.
function RectaNumerica({
  minimo,
  maximo,
  divisiones,
  punto,
  ancho,
}: {
  minimo: number;
  maximo: number;
  divisiones: number;
  punto: number;
  ancho: number;
}) {
  const margen = 18;
  const y = 36;
  const paso = (ancho - margen * 2) / divisiones;
  const x = (i: number) => margen + i * paso;
  const marcasPorEntero = divisiones / (maximo - minimo);
  return (
    <Svg
      width={ancho}
      height={70}
      accessibilityLabel={`Recta numérica de ${minimo} a ${maximo}, dividida en ${divisiones} partes iguales, con un punto marcado`}
    >
      <Line x1={margen} y1={y} x2={ancho - margen} y2={y} stroke={MORADO} strokeWidth={3} />
      {Array.from({ length: divisiones + 1 }, (_, i) => {
        const esEntero = i % marcasPorEntero === 0;
        return (
          <Line
            key={i}
            x1={x(i)}
            y1={y - (esEntero ? 11 : 7)}
            x2={x(i)}
            y2={y + (esEntero ? 11 : 7)}
            stroke={MORADO}
            strokeWidth={esEntero ? 3 : 2}
          />
        );
      })}
      {Array.from({ length: maximo - minimo + 1 }, (_, i) => (
        <TextoSvg
          key={i}
          x={x(i * marcasPorEntero)}
          y={y + 30}
          fontSize={16}
          fontWeight="bold"
          fill={MORADO}
          textAnchor="middle"
        >
          {minimo + i}
        </TextoSvg>
      ))}
      <Circle cx={x(punto)} cy={y} r={8} fill={AMBAR} stroke="#FFFFFF" strokeWidth={2} />
    </Svg>
  );
}

// Cuadrícula de 10 × 10: cada celda es un centésimo; se pinta por filas.
function CuadriculaDecimal({ pintadas, tamano }: { pintadas: number; tamano: number }) {
  const celda = (tamano - 4) / 10;
  return (
    <Svg
      width={tamano}
      height={tamano}
      accessibilityLabel={`Cuadrícula de 100 cuadrados con ${pintadas} pintados`}
    >
      {Array.from({ length: 100 }, (_, i) => (
        <Rect
          key={i}
          x={2 + (i % 10) * celda}
          y={2 + Math.floor(i / 10) * celda}
          width={celda}
          height={celda}
          fill={i < pintadas ? MORADO_CLARO : '#FFFFFF'}
          stroke={MORADO}
          strokeWidth={1}
        />
      ))}
    </Svg>
  );
}

// Dibuja la figura del ejercicio. Los valores de "ordenar" no son figura: los muestra el campo.
export function FiguraEjercicio({
  representacion,
  grande,
}: {
  representacion: Representacion | null;
  grande: boolean;
}) {
  if (representacion?.tipo === 'fraccion-circulo') {
    return <RepresentacionFraccion {...representacion.parametros} tamano={grande ? 200 : 128} />;
  }
  if (representacion?.tipo === 'recta-numerica') {
    return <RectaNumerica {...representacion.parametros} ancho={grande ? 520 : 280} />;
  }
  if (representacion?.tipo === 'cuadricula-decimal') {
    return <CuadriculaDecimal {...representacion.parametros} tamano={grande ? 200 : 128} />;
  }
  return null;
}
