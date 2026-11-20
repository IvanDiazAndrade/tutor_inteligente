import { TextInput, type TextInputProps } from 'react-native';

// Campo de texto con el estilo de los mockups (borde lila, esquinas redondeadas).
export function CampoTexto(props: TextInputProps) {
  return (
    <TextInput
      placeholderTextColor="#9A91BC"
      // En horizontal Android abre el teclado a pantalla completa y tapa el formulario.
      disableFullscreenUI
      className="h-12 rounded-2xl border-[1.5px] border-borde bg-white px-4 font-nunito-bold text-sm text-tinta-media focus:border-primario-claro"
      {...props}
    />
  );
}
