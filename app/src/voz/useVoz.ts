import * as SecureStore from 'expo-secure-store';
import * as Speech from 'expo-speech';
import { useCallback, useEffect, useState } from 'react';
import { AccessibilityInfo, AppState } from 'react-native';

import { entonar } from '@/voz/entonacion';
import { hablado } from '@/voz/hablado';

const CLAVE = 'voz-octavio';

// La voz de Octavio, elegida por el equipo (viene con el «Texto a voz» de Google): un poco aguda,
// porque es un personaje, y algo lenta. En un teléfono que no la tenga se usa otra en español,
// primero las que no necesitan internet y las más cercanas.
const VOZ_DE_OCTAVIO = 'es-us-x-esd-local';
const TONO = 1.2;
const VELOCIDAD = 0.92;
const PREFERIDAS = ['es-CL', 'es-MX', 'es-US', 'es-419', 'es-ES'];

async function elegirVoz() {
  const voces = (await Speech.getAvailableVoicesAsync())
    .map((v) => ({ id: v.identifier, idioma: v.language.replace('_', '-') }))
    .filter((v) => /^(es|spa)\b/i.test(v.idioma));
  const orden = ({ id, idioma }: { id: string; idioma: string }) => {
    if (id === VOZ_DE_OCTAVIO) return -1;
    const i = PREFERIDAS.indexOf(idioma);
    return (/network/i.test(id) ? 100 : 0) + (i < 0 ? PREFERIDAS.length : i);
  };
  return voces.sort((a, b) => orden(a) - orden(b))[0];
}

// Lee un texto con la voz del teléfono (sin costo). Devuelve cómo callarla.
function leer(texto: string, alEmpezar: () => void, alTerminar: (completo: boolean) => void) {
  let vigente = true;
  const terminar = (completo: boolean) => {
    if (vigente) alTerminar(completo);
  };
  const empezar = async () => {
    const voz = await elegirVoz();
    await Speech.stop();
    if (!vigente) return;
    // Frase por frase, cada una con su entonación; el teléfono las encola y las dice seguidas.
    const frases = entonar(hablado(texto));
    if (frases.length === 0) terminar(true);
    frases.forEach(({ frase, tono, velocidad }, i) =>
      Speech.speak(frase, {
        language: voz?.idioma ?? 'es',
        voice: voz?.id,
        rate: VELOCIDAD * velocidad,
        pitch: TONO * tono,
        onStart: () => {
          if (vigente && i === 0) alEmpezar();
        },
        onDone: () => {
          if (i === frases.length - 1) terminar(true);
        },
        onStopped: () => terminar(false),
        onError: () => terminar(false),
      }),
    );
  };
  empezar().catch(() => terminar(false)); // sin voz, el texto igual se lee en pantalla
  return () => {
    vigente = false;
    Speech.stop().catch(() => {});
  };
}

// Voz de Octavio, con un interruptor que se recuerda en el teléfono. Parte encendida, salvo que
// se use un lector de pantalla (ya lee el texto y las dos voces se taparían).
export function useVoz() {
  const [activa, setActiva] = useState<boolean | null>(null); // null: aún no se sabe
  const [hablando, setHablando] = useState(false);

  useEffect(() => {
    let montada = true;
    Promise.all([
      SecureStore.getItemAsync(CLAVE).catch(() => null),
      AccessibilityInfo.isScreenReaderEnabled().catch(() => false),
    ]).then(([guardada, lector]) => {
      if (montada) setActiva(guardada ? guardada === 'si' : !lector);
    });
    // Al salir de la app, Octavio se calla.
    const escucha = AppState.addEventListener('change', (estado) => {
      if (estado !== 'active') Speech.stop().catch(() => {});
    });
    return () => {
      montada = false;
      escucha.remove();
    };
  }, []);

  const alternar = () => {
    const nueva = !activa;
    setActiva(nueva);
    SecureStore.setItemAsync(CLAVE, nueva ? 'si' : 'no').catch(() => {});
  };

  const decir = useCallback((texto: string, alTerminar?: () => void) => {
    const callar = leer(
      texto,
      () => setHablando(true),
      (completo) => {
        setHablando(false);
        if (completo) alTerminar?.();
      },
    );
    return () => {
      callar();
      setHablando(false);
    };
  }, []);

  return { activa, hablando, alternar, decir };
}
