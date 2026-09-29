import Svg, { Circle, Ellipse, Line, Path, Text as SvgText } from 'react-native-svg';

// Octavio, el pulpo morado mago (mockups/Lamina Personaje Octavio). Dibujado con SVG
// para que se vea nítido en cualquier densidad de pantalla.
type Props = {
  tamano?: number;
  guino?: boolean;
  conVarita?: boolean;
  // Variante del tutor en el ejercicio: dos varitas, mejillas y destellos (mockup "Ejercicio").
  tutor?: boolean;
};

const MORADO = '#7C3AED';
const CUERPO = '#8B5CF6';
const SOMBRERO = '#312E81';
const DORADO = '#FBBF24';

const DESTELLO = 'M0,-6 L1.8,-1.8 L6,0 L1.8,1.8 L0,6 L-1.8,1.8 L-6,0 L-1.8,-1.8 Z';
const ESTRELLA =
  'M0,-9 L2.7,-2.8 L9,-2.8 L4,1.1 L5.6,7.8 L0,3.9 L-5.6,7.8 L-4,1.1 L-9,-2.8 L-2.7,-2.8 Z';

const TENTACULOS = [
  'M62 142 Q34 132 30 104',
  'M138 142 Q166 132 170 104',
  'M72 160 Q66 196 48 198',
  'M90 166 Q90 204 74 208',
  'M110 166 Q110 204 126 208',
  'M128 160 Q134 196 152 198',
];

const SIMBOLOS = [
  { x: 100, y: 44, s: '÷' },
  { x: 91, y: 62, s: '+' },
  { x: 112, y: 62, s: '×' },
  { x: 101, y: 78, s: '−' },
];

export function Octavio({ tamano = 56, guino = false, conVarita = false, tutor = false }: Props) {
  return (
    <Svg width={tamano * 0.93} height={tamano} viewBox="0 0 200 214" accessibilityLabel="Octavio">
      {(conVarita || tutor) && <Path d={DESTELLO} transform="translate(170,118)" fill={DORADO} />}
      {tutor && (
        <>
          <Path d={DESTELLO} transform="translate(178,150) scale(0.83)" fill={DORADO} />
          <Path d={DESTELLO} transform="translate(22,140) scale(0.83)" fill={DORADO} />
        </>
      )}
      {TENTACULOS.map((d) => (
        <Path key={d} d={d} fill="none" stroke={MORADO} strokeWidth={13} strokeLinecap="round" />
      ))}
      {(conVarita || tutor) && (
        <>
          <Line
            x1={36}
            y1={114}
            x2={20}
            y2={88}
            stroke="#92400E"
            strokeWidth={5}
            strokeLinecap="round"
          />
          <Path d={ESTRELLA} transform="translate(18,80)" fill={DORADO} />
        </>
      )}
      {tutor && (
        <>
          <Line
            x1={164}
            y1={114}
            x2={180}
            y2={88}
            stroke="#92400E"
            strokeWidth={5}
            strokeLinecap="round"
          />
          <Path d={ESTRELLA} transform="translate(182,80)" fill={DORADO} />
        </>
      )}
      <Ellipse cx={100} cy={122} rx={52} ry={48} fill={CUERPO} />
      <Path d="M100 8 L138 82 L62 82 Z" fill={SOMBRERO} />
      {SIMBOLOS.map(({ x, y, s }) => (
        <SvgText
          key={s}
          x={x}
          y={y}
          textAnchor="middle"
          fontSize={13}
          fontWeight="900"
          fill={DORADO}
        >
          {s}
        </SvgText>
      ))}
      <Ellipse cx={100} cy={82} rx={58} ry={13} fill={SOMBRERO} />
      <Circle cx={84} cy={116} r={13} fill="#FFFFFF" />
      <Circle cx={116} cy={116} r={13} fill="#FFFFFF" />
      <Circle cx={86} cy={118} r={6} fill={SOMBRERO} />
      <Circle cx={88.5} cy={115.5} r={2.4} fill="#FFFFFF" />
      {guino ? (
        <Path
          d="M108 116 Q116 122 124 116"
          fill="none"
          stroke={SOMBRERO}
          strokeWidth={4}
          strokeLinecap="round"
        />
      ) : (
        <>
          <Circle cx={114} cy={118} r={6} fill={SOMBRERO} />
          <Circle cx={116.5} cy={115.5} r={2.4} fill="#FFFFFF" />
        </>
      )}
      <Path
        d="M88 140 Q100 150 112 140"
        fill="none"
        stroke={SOMBRERO}
        strokeWidth={4}
        strokeLinecap="round"
      />
      {tutor && (
        <>
          <Circle cx={72} cy={136} r={6} fill="#FB7185" opacity={0.45} />
          <Circle cx={128} cy={136} r={6} fill="#FB7185" opacity={0.45} />
        </>
      )}
    </Svg>
  );
}
