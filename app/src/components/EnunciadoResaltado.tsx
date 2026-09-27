import { Text } from 'react-native';

const COLORES = ['text-primario', 'text-ambar'];

// Enunciado del ejercicio con las fracciones resaltadas en los mismos colores de la figura.
export function EnunciadoResaltado({ texto, grande = false }: { texto: string; grande?: boolean }) {
  const partes = texto.split(/(\d+\/\d+)/);
  let fraccion = 0;
  return (
    <Text
      className={`font-nunito-bold text-tinta-media ${grande ? 'text-2xl leading-9' : 'text-base leading-6'}`}
    >
      {partes.map((parte, i) => {
        if (!/^\d+\/\d+$/.test(parte)) return parte;
        const color = COLORES[fraccion++ % COLORES.length];
        return (
          <Text key={i} className={`font-nunito-black ${color}`}>
            {parte}
          </Text>
        );
      })}
    </Text>
  );
}
