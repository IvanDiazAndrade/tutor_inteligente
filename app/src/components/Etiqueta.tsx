import { Text, View } from 'react-native';

export type TipoEtiqueta = 'dominada' | 'repasar' | 'nueva';

const ESTILOS: Record<TipoEtiqueta, { caja: string; texto: string; contenido: string }> = {
  dominada: { caja: 'bg-exito-fondo', texto: 'text-exito', contenido: '🏅 ¡Dominada!' },
  repasar: { caja: 'bg-repasar-fondo', texto: 'text-repasar', contenido: '¡A repasar!' },
  nueva: {
    caja: 'border-[1.5px] border-nueva-borde bg-fondo',
    texto: 'text-primario',
    contenido: '✨ ¡Nueva!',
  },
};

// Etiqueta redondeada de estado de una unidad. Encuadre de avance, nunca de castigo (RF-DA6):
// "repasar" es una invitación, no una alerta.
export function Etiqueta({ tipo, grande = false }: { tipo: TipoEtiqueta; grande?: boolean }) {
  const estilo = ESTILOS[tipo];
  return (
    <View className={`self-start rounded-full px-3 py-1 ${estilo.caja}`}>
      <Text className={`font-nunito-black ${grande ? 'text-sm' : 'text-xs'} ${estilo.texto}`}>
        {estilo.contenido}
      </Text>
    </View>
  );
}
