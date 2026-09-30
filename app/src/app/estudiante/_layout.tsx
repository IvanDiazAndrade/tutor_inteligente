import { Tabs } from 'expo-router';
import type { ColorValue } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import Svg, { Path, Rect } from 'react-native-svg';

import { useDistribucion } from '@/hooks/useDistribucion';
import { Protegida } from '@/sesion/Protegida';

const ACTIVO = '#6D28D9';
const INACTIVO = '#B7A8E8';

// Íconos de la barra inferior, tomados del mockup "Home Estudiante".
function IconoInicio({ color, tamano }: { color: ColorValue; tamano: number }) {
  return (
    <Svg width={tamano} height={tamano} viewBox="0 0 24 24">
      <Path d="M4 11 L12 4 L20 11 V20 H14 V15 H10 V20 H4 Z" fill={color} />
    </Svg>
  );
}

function IconoPracticar({ color, tamano }: { color: ColorValue; tamano: number }) {
  return (
    <Svg width={tamano} height={tamano} viewBox="0 0 24 24">
      <Rect x={4} y={5} width={16} height={14} rx={3} fill="none" stroke={color} strokeWidth={2} />
      <Path d="M8 10 H16 M8 14 H13" stroke={color} strokeWidth={2} strokeLinecap="round" />
    </Svg>
  );
}

function IconoLogros({ color, tamano }: { color: ColorValue; tamano: number }) {
  return (
    <Svg width={tamano} height={tamano} viewBox="0 0 24 24">
      <Path
        d="M12 3 L14.4 8.2 L20 8.9 L15.8 12.8 L17 18.5 L12 15.6 L7 18.5 L8.2 12.8 L4 8.9 L9.6 8.2 Z"
        fill="none"
        stroke={color}
        strokeWidth={2}
        strokeLinejoin="round"
      />
    </Svg>
  );
}

// Navegación del estudiante: máximo dos niveles de profundidad (RNF-U1). Solo con una sesión
// de estudiante; sin ella vuelve a la pantalla de acceso.
export default function LayoutEstudiante() {
  const { bottom } = useSafeAreaInsets();
  const { esTablet } = useDistribucion();
  // En tablet la barra crece para que los niños la toquen y lean con facilidad (RNF-U1).
  const icono = esTablet ? 34 : 24;
  const alto = esTablet ? 92 : 64;
  return (
    <Protegida rol="estudiante">
      <Tabs
        screenOptions={{
          headerShown: false,
          tabBarActiveTintColor: ACTIVO,
          tabBarInactiveTintColor: INACTIVO,
          tabBarLabelPosition: 'below-icon',
          tabBarLabelStyle: {
            fontFamily: 'Nunito_900Black',
            fontSize: esTablet ? 17 : 11,
          },
          tabBarStyle: {
            borderTopColor: '#EFE8FF',
            borderTopWidth: 1.5,
            height: alto + bottom,
            paddingTop: esTablet ? 10 : 6,
            paddingBottom: 8 + bottom,
          },
          sceneStyle: { backgroundColor: '#FAF7FF' },
        }}
      >
        <Tabs.Screen
          name="index"
          options={{
            title: 'Inicio',
            tabBarIcon: ({ color }) => <IconoInicio color={color} tamano={icono} />,
          }}
        />
        <Tabs.Screen
          name="practicar"
          options={{
            title: 'Practicar',
            tabBarIcon: ({ color }) => <IconoPracticar color={color} tamano={icono} />,
          }}
        />
        <Tabs.Screen
          name="logros"
          options={{
            title: 'Mis logros',
            tabBarIcon: ({ color }) => <IconoLogros color={color} tamano={icono} />,
          }}
        />
      </Tabs>
    </Protegida>
  );
}
