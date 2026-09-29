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
        seccion: '#7C6BB8',
        exito: { DEFAULT: '#0E9F6E', fondo: '#D6F5E8' },
        repasar: { DEFAULT: '#BE4459', fondo: '#FFE4E9' },
        ambar: { DEFAULT: '#B45309', fondo: '#FFF7E6', borde: '#FDE7B0' },
        nueva: { borde: '#DDD0FF' },
        divisor: '#EFE8FF',
        globo: '#E9D5FF',
        // Bandas del medidor de dominio (panel del apoderado). Validadas con el script de
        // la guía de visualización: contraste >= 3:1 sobre blanco y separables con daltonismo.
        banda: { dominado: '#059669', practicando: '#8B5CF6', empezando: '#D97706', riel: '#F1ECFC' },
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
