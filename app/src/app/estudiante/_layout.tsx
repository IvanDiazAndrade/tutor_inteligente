import { Tabs } from 'expo-router';
import type { ColorValue } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import Svg, { Circle, Path } from 'react-native-svg';

import { useDistribucion } from '@/hooks/useDistribucion';
import { Protegida } from '@/sesion/Protegida';

const ACTIVO = '#6D28D9';
const INACTIVO = '#9A91BC';

// Íconos de la barra inferior: rellenos en la pestaña activa y en contorno en las demás.
type PropsIcono = { color: ColorValue; tamano: number; relleno: boolean };

function IconoLecciones({ color, tamano, relleno }: PropsIcono) {
  return (
    <Svg width={tamano} height={tamano} viewBox="0 0 24 24">
      <Path
        d="M12 6.5 C9.5 4.8 6.3 4.4 3 5 V19 C6.3 18.4 9.5 18.8 12 20.5 C14.5 18.8 17.7 18.4 21 19 V5 C17.7 4.4 14.5 4.8 12 6.5 Z"
        fill={relleno ? color : 'none'}
        stroke={color}
        strokeWidth={2}
        strokeLinejoin="round"
      />
      <Path
        d="M12 6.5 V20.5"
        stroke={relleno ? '#FFFFFF' : color}
        strokeWidth={2}
        strokeLinecap="round"
      />
    </Svg>
  );
}

function IconoEjercicios({ color, tamano, relleno }: PropsIcono) {
  return (
    <Svg width={tamano} height={tamano} viewBox="0 0 24 24">
      <Path
        d="M15.5 4.5 L19.5 8.5 L9 19 L4 20 L5 15 Z"
        fill={relleno ? color : 'none'}
        stroke={color}
        strokeWidth={2}
        strokeLinejoin="round"
      />
      <Path
        d="M13 7 L17 11"
        stroke={relleno ? '#FFFFFF' : color}
        strokeWidth={2}
        strokeLinecap="round"
      />
    </Svg>
  );
}

function IconoPerfil({ color, tamano, relleno }: PropsIcono) {
  return (
    <Svg width={tamano} height={tamano} viewBox="0 0 24 24">
      <Circle cx={12} cy={8} r={4} fill={relleno ? color : 'none'} stroke={color} strokeWidth={2} />
      <Path
        d="M4 20.5 C4 16.2 7.6 13.8 12 13.8 C16.4 13.8 20 16.2 20 20.5 Z"
        fill={relleno ? color : 'none'}
        stroke={color}
        strokeWidth={2}
        strokeLinejoin="round"
      />
    </Svg>
  );
}

// Navegación del estudiante (RNF-U1, actualización 2-nov-2026): tres pestañas fijas abajo,
// Lecciones, Ejercicios y Perfil. Lecciones y Ejercicios tienen dos niveles: lista y detalle.
// Solo con una sesión de estudiante; sin ella vuelve a la pantalla de acceso.
export default function LayoutEstudiante() {
  const { bottom } = useSafeAreaInsets();
  const { esTablet } = useDistribucion();
  // En tablet la barra crece para que los niños la toquen y lean con facilidad (RNF-U1).
  const icono = esTablet ? 34 : 26;
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
            fontSize: esTablet ? 17 : 12,
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
          name="lecciones"
          options={{
            title: 'Lecciones',
            tabBarIcon: ({ color, focused }) => (
              <IconoLecciones color={color} tamano={icono} relleno={focused} />
            ),
          }}
        />
        <Tabs.Screen
          name="ejercicios"
          options={{
            title: 'Ejercicios',
            tabBarIcon: ({ color, focused }) => (
              <IconoEjercicios color={color} tamano={icono} relleno={focused} />
            ),
          }}
        />
        <Tabs.Screen
          name="perfil"
          options={{
            title: 'Perfil',
            tabBarIcon: ({ color, focused }) => (
              <IconoPerfil color={color} tamano={icono} relleno={focused} />
            ),
          }}
        />
      </Tabs>
    </Protegida>
  );
}
