import { router } from 'expo-router';
import { Pressable, Text } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

// Marcador del panel del apoderado: se construye en un paso posterior de la tarea 42.
export default function PanelApoderado() {
  return (
    <SafeAreaView className="flex-1 items-center justify-center gap-4 bg-fondo p-6">
      <Text className="font-nunito-black text-2xl text-tinta">Panel del apoderado</Text>
      <Text className="text-center font-nunito-bold text-base text-apagado-oscuro">
        Aquí irá el resumen semanal y el progreso por unidad (pantalla posterior del prototipo).
      </Text>
      <Pressable
        onPress={() => router.replace('/')}
        className="rounded-full bg-primario px-6 py-3 active:bg-primario-oscuro"
      >
        <Text className="font-nunito-black text-white">Cerrar sesión</Text>
      </Pressable>
    </SafeAreaView>
  );
}
