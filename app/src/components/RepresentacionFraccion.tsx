import Svg, { Circle, Line, Path } from 'react-native-svg';

type Props = { denominador: number; partesDestacadas: number[]; tamano?: number };

const COLORES = ['#8B5CF6', '#FBBF24'];

// Representación pictórica paramétrica "fraccion-circulo" (modelo_dominio.md §6, COPISI):
// un círculo en `denominador` partes; cada grupo de partesDestacadas va en un color.
export function RepresentacionFraccion({ denominador, partesDestacadas, tamano = 128 }: Props) {
  const r = 80;
  const c = 90;
  const punto = (i: number) => {
    const angulo = (i / denominador) * 2 * Math.PI - Math.PI / 2;
    return { x: c + r * Math.cos(angulo), y: c + r * Math.sin(angulo) };
  };

  const colorDe: (string | undefined)[] = [];
  partesDestacadas.forEach((cantidad, grupo) => {
    for (let k = 0; k < cantidad; k++) colorDe.push(COLORES[grupo % COLORES.length]);
  });

  return (
    <Svg
      width={tamano}
      height={tamano}
      viewBox="0 0 180 180"
      accessibilityLabel={`Círculo dividido en ${denominador} partes iguales`}
    >
      <Circle cx={c} cy={c} r={r} fill="#FFFFFF" />
      {Array.from({ length: denominador }, (_, i) => {
        const color = colorDe[i];
        if (!color) return null;
        const a = punto(i);
        const b = punto(i + 1);
        const arcoGrande = denominador === 1 ? 1 : 0;
        return (
          <Path
            key={i}
            d={`M${c} ${c} L${a.x} ${a.y} A${r} ${r} 0 ${arcoGrande} 1 ${b.x} ${b.y} Z`}
            fill={color}
          />
        );
      })}
      <Circle cx={c} cy={c} r={r} fill="none" stroke="#6D28D9" strokeWidth={2.5} />
      {denominador > 1 &&
        Array.from({ length: denominador }, (_, i) => {
          const p = punto(i);
          return (
            <Line key={i} x1={c} y1={c} x2={p.x} y2={p.y} stroke="#6D28D9" strokeWidth={2.5} />
          );
        })}
    </Svg>
  );
}
