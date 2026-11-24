// Separa un texto en frases y le da a cada una su entonación, para que Octavio no suene plano: la
// voz del teléfono lee todo parejo si recibe el texto de una vez.
export type FraseEntonada = { frase: string; tono: number; velocidad: number };

export function entonar(texto: string): FraseEntonada[] {
  // Corta al final de cada frase, y antes de «¿» o «¡» ("después de repartir, ¿sobró algo?").
  const frases = (texto.match(/[¿¡]?[^.!?¿¡…]+[.!?…]*/g) ?? [])
    .map((f) => f.trim())
    .filter((f) => /[\p{L}\d]/u.test(f));
  let explicaciones = 0;
  return frases.map((frase) => {
    if (/\?[.]?$/.test(frase)) return { frase, tono: 1.3, velocidad: 0.95 }; // sube
    if (/!$/.test(frase)) return { frase, tono: 1.1, velocidad: 1.08 }; // con entusiasmo
    // Las explicaciones alternan apenas el tono, como al contar algo paso a paso.
    return { frase, tono: explicaciones++ % 2 === 0 ? 1.02 : 0.94, velocidad: 1 };
  });
}
