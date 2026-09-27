/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{ts,tsx}'],
  presets: [require('nativewind/preset')],
  theme: {
    extend: {
      // Paleta tomada de los mockups (mockups/*.dc.html).
      colors: {
        fondo: '#F5F1FF',
        panel: '#FAF7FF',
        borde: '#E5DCFA',
        primario: { DEFAULT: '#6D28D9', oscuro: '#55219E', claro: '#8B5CF6' },
        lila: { DEFAULT: '#A78BFA', suave: '#C4B5FD', fondo: '#EDE6FC', apagado: '#B7A8E8' },
        tinta: { DEFAULT: '#312E81', media: '#3B3358', tecla: '#4C3D8F' },
        apagado: { DEFAULT: '#9A91BC', oscuro: '#6B6390' },
        dorado: '#FBBF24',
      },
      // En React Native cada peso de una fuente propia es una familia distinta.
      fontFamily: {
        nunito: ['Nunito_600SemiBold'],
        'nunito-bold': ['Nunito_700Bold'],
        'nunito-extrabold': ['Nunito_800ExtraBold'],
        'nunito-black': ['Nunito_900Black'],
      },
    },
  },
  plugins: [],
};
