// Cómo se dice en voz alta un texto escrito con la convención chilena (4.205; 0,5; 24 : 6; 3/4).
// Sin esto, la voz del teléfono lee los signos a su manera ("cuatro punto doscientos cinco").

const PARTES: Record<number, string> = {
  2: 'medio',
  3: 'tercio',
  4: 'cuarto',
  5: 'quinto',
  6: 'sexto',
  7: 'séptimo',
  8: 'octavo',
  9: 'noveno',
  10: 'décimo',
  12: 'doceavo',
  100: 'centésimo',
};

function fraccion(numerador: string, denominador: string) {
  const parte = PARTES[Number(denominador)];
  if (!parte) return `${numerador} sobre ${denominador}`;
  return Number(numerador) === 1 ? `un ${parte}` : `${numerador} ${parte}s`;
}

// Los ceros a la izquierda se dicen: 2,05 es "2 coma cero 5".
const decimales = (cifras: string) =>
  cifras.replace(/^0+(?=\d)/, (ceros) => 'cero '.repeat(ceros.length));

export function hablado(texto: string) {
  return texto
    .replace(/\u00A0/g, ' ')
    .replace(/[«»]/g, '')
    .replace(/\d{1,3}(?:\.\d{3})+(?!\d)/g, (n) => n.replace(/\./g, ''))
    .replace(/\$(\d+)/g, '$1 pesos')
    .replace(/(\d+) (\d+)\/(\d+)/g, (_, e: string, n: string, d: string) => {
      return `${Number(e) === 1 ? 'un entero' : `${e} enteros`} y ${fraccion(n, d)}`;
    })
    .replace(/(\d+)\/(\d+)/g, (_, n: string, d: string) => fraccion(n, d))
    .replace(/(\d+),(\d+)/g, (_, e: string, c: string) => `${e} coma ${decimales(c)}`)
    .replace(/([Dd]ivid(?:e|ir|es) \d+) : /g, '$1 en ')
    .replace(/ : /g, ' dividido en ')
    .replace(/(\d) km\b/g, '$1 kilómetros')
    .replace(/(\d) m\b/g, '$1 metros')
    .replace(/ ?× ?/g, ' por ')
    .replace(/ ?\+ ?/g, ' más ')
    .replace(/ ?− ?/g, ' menos ')
    .replace(/ ?= ?/g, ' es igual a ')
    .replace(/ ?< ?/g, ' es menor que ')
    .replace(/ ?> ?/g, ' es mayor que ')
    .replace(/ ?[→·;] ?/g, ', ');
}
