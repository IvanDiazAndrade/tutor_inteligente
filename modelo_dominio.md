# Modelo del Dominio (Fase II, tarea 23)

**Proyecto:** Tutor inteligente basado en IA para el aprendizaje de matemáticas — eje de Números, 4°–6° básico.
**Documento:** Diseño preliminar del modelo del dominio del ITS: catálogo curricular, esquema del ejercicio, corrector programático, catálogo de plantillas de generación, dimensionamiento del banco y pipeline de verificación. Deriva de `requisitos.md` (RF-D1–D8, RNF-P1–P3) y de `arquitectura.md` (§2 mapeo ITS, §3 "Catálogo curricular" y "Generador y banco", AD-2/AD-3/AD-9).

**Decisiones de alcance tomadas con el equipo para este documento:** unidad = OA completo (24 unidades); formatos de respuesta numérico, fracción y ordenar/comparar (sin selección múltiple ni respuesta abierta); fracciones equivalentes aceptadas por defecto con refuerzo de la forma simplificada; representación pictórica SVG para fracciones y decimales; banco inicial 3 niveles × 5 ejercicios por unidad; corrector acepta coma y punto decimal (muestra siempre coma); gold standard de 2 ejercicios por OA.

---

## 1. Catálogo curricular

La unidad mínima del dominio es el **OA completo** (RF-D1): 24 unidades para el Anillo 1 (4°: OA 1–3, 5–9 · 5°: OA 1, 3–7, 9–13 · 6°: OA 2, 5–8, según `curriculo_4a6_matematica.md`). Cada unidad es una fila de datos, sin lógica (RNF-M2):

| Atributo | Contenido | Uso |
|---|---|---|
| `oaCodigo` | ej. `4B-OA9` | clave del índice de dominio (`DominioOA`) |
| `oaTextoOficial` | redacción completa de las Bases Curriculares | va íntegro en el prompt de generación (RF-D2, hallazgo EDUMATH) |
| `descripcionCiudadana` | ej. "Sumar y restar fracciones con el mismo denominador" | skill meters del dashboard (RF-DA2) |
| `curso`, `basal`, `anillo`, `orden` | 4/5/6, ✅/◻️, 1/2, posición sugerida | navegación y priorización |
| `rangoNumerico` | límites de operandos del OA (ej. 4B-OA1: 0–10 000; 4B-OA8: denominadores {2,3,4,5,6,8,10,12,100}) | generador paramétrico y capa 2 del pipeline |
| `subtema` (opcional) | etiqueta libre dentro del OA (ej. "recta numérica") | refinar reportes sin cambiar el modelo |

Agregar el Anillo 2 (RF-D8) es insertar filas: razón y porcentaje (6B-OA3/OA4) entran con plantillas nuevas pero sin cambio de esquema.

---

## 2. Esquema del ejercicio

Todo ejercicio — paramétrico o LLM — persiste en el banco con la misma estructura (RF-D3, RF-D5). Esquema JSON de referencia (el DDL exacto se fija en Fase III, tarea 41):

```json
{
  "id": "uuid",
  "unidadId": "4B-OA9",
  "nivelDificultad": 2,
  "fuente": "llm",
  "estado": "activo",
  "enunciado": "Pedro tiene 1/4 de pizza y su hermana le regala 2/4 más. ¿Qué fracción de pizza tiene ahora?",
  "representacion": {
    "tipo": "fraccion-circulo",
    "parametros": { "denominador": 4, "partesDestacadas": [1, 2] }
  },
  "formatoRespuesta": "fraccion",
  "respuestaFinal": "3/4",
  "reglaValidacion": { "aceptaEquivalentes": true },
  "solucionReferencia": [
    "Los denominadores ya son iguales (4), así que no hay que cambiarlos.",
    "Se suman solo los numeradores: 1 + 2 = 3.",
    "El resultado es 3/4 de pizza."
  ],
  "erroresComunes": [
    {
      "respuesta": "3/8",
      "causa": "sumó también los denominadores",
      "retroalimentacion": "Cuando los denominadores son iguales, se mantienen: solo se suman los numeradores."
    }
  ],
  "pistas": [
    "Fíjate en los denominadores. ¿Son iguales o distintos?",
    "Cuando los denominadores son iguales, se mantienen. Solo trabajas con los de arriba.",
    "Suma solo los numeradores: 1 + 2. El denominador sigue siendo 4."
  ],
  "metadatos": { "plantillaId": null, "loteGeneracion": "2026-08-L3", "versionPrompt": "gen-v1.2" }
}
```

Notas de diseño:

- **`fuente`** ∈ {`parametrica`, `llm`, `gold`}. Los `gold` (§7) nunca entran en rotación.
- **`estado`** sigue el ciclo de AD-3: `borrador → verificado → activo | descartado` (+ `retirado` para sacar de rotación sin borrar historial de intentos).
- **`solucionReferencia`** y **`respuestaFinal` nunca viajan al cliente** (RF-D3, AD-1); alimentan al corrector y a los prompts de retroalimentación/pistas.
- **`erroresComunes`** se usa **solo para diagnóstico y retroalimentación** (RF-P2): si la respuesta incorrecta coincide con un patrón, el prompt de retroalimentación recibe la causa probable. Sin selección múltiple, no se usan como distractores. En plantillas paramétricas los patrones son fórmulas (ej. para a/d + b/d: el patrón "(a+b)/2d" detecta la suma de denominadores para cualquier valor de los parámetros).
- **`pistas[3]`** se generan y verifican **junto con el ejercicio** (decisión de la tarea 24): pista 1 = estrategia, 2 = primer paso, 3 = a un paso del final. Pasan el pipeline y el filtro de no revelación en frío; en operación normal el LLM puede reformularlas según el estudiante, y en degradación (F6) se sirven tal cual — las pistas funcionan aunque OpenAI no responda.
- **`representacion`** es opcional y **paramétrica, no una imagen**: guarda tipo + parámetros y el cliente la dibuja como SVG (§6). Así el LLM nunca genera gráficos, solo puede *pedirlos* indicando parámetros que la capa 2 valida.
- **`metadatos.versionPrompt`** permite auditar qué versión de la plantilla de generación produjo cada ejercicio (RNF-M1) y correlacionar calidad por versión.

---

## 3. Formatos de respuesta y corrector programático

Tres formatos, todos validables por código (RF-D7, AD-2). El corrector es una función pura `corregir(respuestaCruda, ejercicio) → {esCorrecta, patronErrorDetectado?}`.

### 3.1 Normalización de entrada (común)

1. Recortar espacios, colapsar espacios internos, ignorar el símbolo `$` y la palabra "pesos" en respuestas de dinero.
2. **Separador de miles:** se elimina el punto solo cuando el patrón es de miles (grupos de exactamente 3 dígitos: `1.000`, `12.500`). 
3. **Separador decimal:** coma y punto se aceptan por igual (`0,5` ≡ `0.5`); la ambigüedad con el punto de miles se resuelve con el formato esperado del ejercicio (si la respuesta esperada es entera, `1.500` se lee como mil quinientos; si es decimal con hasta 3 posiciones, `1.5` se lee como un coma cinco). **El sistema siempre muestra con coma** (convención chilena, RF-P6).
4. Ceros no significativos se ignoran: `0,50` ≡ `0,5` ≡ `,5`.

### 3.2 Políticas por formato

| Formato | Entrada | Comparación | Regla de equivalencia |
|---|---|---|---|
| `numerico` | campo con teclado numérico | igualdad exacta tras normalizar; **aritmética entera escalada, nunca floats** (0,1 + 0,2 debe dar exactamente 0,3) | ejercicios de estimación/redondeo declaran el valor redondeado esperado como respuesta canónica (no hay tolerancia ±: el OA pide redondear, no aproximar libremente) |
| `fraccion` | entrada `a/b` o número mixto `c a/b` | equivalencia por producto cruzado con enteros (a·d = b·c); mixtos se convierten a impropia antes de comparar | `aceptaEquivalentes: true` **por defecto**: 6/8 cuenta como 3/4, y la retroalimentación agrega "¡Bien! También puedes escribirla como 3/4". `false` solo donde la forma ES el objetivo: 5B-OA7 (simplificar/amplificar) y 6B-OA5 (convertir impropia ↔ mixto) |
| `ordenar` / `comparar` | ordenar 3–5 valores presentados (arrastrar o numerar); o elegir `<`, `=`, `>` | igualdad exacta con la secuencia/símbolo canónico | el generador garantiza valores distintos (sin empates) salvo que el ejercicio evalúe justamente la igualdad (ej. 6/8 vs 3/4 → `=`) |

Casos rechazados con mensaje de formato (no cuentan como intento fallido): denominador 0, texto no parseable, fracción donde se espera decimal si el ejercicio lo exige.

---

## 4. Catálogo de plantillas por unidad

Cobertura de las 24 unidades del Anillo 1. **Fuente** P = paramétrica (correcta por construcción, sin revisión humana una vez aprobada la plantilla), LLM = problemas verbales vía pipeline (§8), P+LLM = mixta (lo numérico paramétrico, los problemas del OA vía LLM).

| Unidad | Contenido resumido | Plantillas paramétricas | Fuente | Formatos | Pictórico |
|---|---|---|---|---|---|
| 4B-OA1 | números hasta 10 000 | valor posicional, componer/descomponer, ubicar en recta, comparar/ordenar | P | numérico, ordenar/comparar | recta numérica |
| 4B-OA2 | cálculo mental ×/÷ hasta 10·10 | tablas directas e inversas, doblar/dividir por 2 | P | numérico | — |
| 4B-OA3 | + y − hasta 1 000 | operaciones con/sin reserva, hasta 4 sumandos, estimación | P+LLM | numérico | — |
| 4B-OA5 | mult. 3d × 1d | algoritmo, distributiva, estimación | P+LLM | numérico | — |
| 4B-OA6 | div. 2d ÷ 1d | cociente exacto, relación ×/÷ | P+LLM | numérico | — |
| 4B-OA7 | problemas con dinero | — (montos realistas en pesos los fija la capa 2) | LLM | numérico | — |
| 4B-OA8 | concepto de fracción | parte de un todo, ubicar en recta, comparar/ordenar (den. {2,3,4,5,6,8,10,12,100}) | P | fracción, ordenar/comparar | círculo/barra, recta |
| 4B-OA9 | + y − fracciones igual denominador | suma/resta con den. iguales | P+LLM | fracción | círculo/barra |
| 5B-OA1 | naturales hasta 1 000 millones | valor posicional, forma expandida, aproximar, comparar/ordenar | P | numérico, ordenar/comparar | — |
| 5B-OA3 | mult. 2d × 2d | algoritmo, estimación | P+LLM | numérico | — |
| 5B-OA4 | div. 3d ÷ 1d con resto | cociente y resto; interpretación del resto en contexto | P+LLM | numérico | — |
| 5B-OA5 | operatoria combinada | expresiones con paréntesis y prioridad, resultado entero garantizado | P | numérico | — |
| 5B-OA6 | problemas 4 operaciones (dinero) | — | LLM | numérico | — |
| 5B-OA7 | fracciones propias, equivalencia | simplificar, amplificar, comparar igual/distinto den. (`aceptaEquivalentes: false` en simplificar/amplificar) | P | fracción, comparar | círculo/barra |
| 5B-OA9 | + y − fracciones den. ≤ 12 | distinto denominador, amplificando/simplificando | P+LLM | fracción | círculo/barra |
| 5B-OA10 | fracción → decimal (den. 2,4,5,10) | conversión directa e inversa | P | numérico, fracción | cuadrícula decimal |
| 5B-OA11 | comparar/ordenar decimales a la milésima | comparar pares, ordenar 3–5 decimales | P | ordenar/comparar | recta numérica |
| 5B-OA12 | + y − decimales a la milésima | operaciones por valor posicional | P+LLM | numérico | — |
| 5B-OA13 | problemas con fracciones o decimales | — | LLM | numérico, fracción | — |
| 6B-OA2 | 4 operaciones en problemas | — | LLM | numérico | — |
| 6B-OA5 | impropias ↔ mixtos, recta | conversión en ambos sentidos (`aceptaEquivalentes: false`), ubicar en recta | P | fracción | recta numérica |
| 6B-OA6 | + y − propias/impropias/mixtos | operatoria con den. hasta 2 dígitos | P+LLM | fracción | — |
| 6B-OA7 | × y ÷ de decimales | por natural de 1 dígito, por múltiplos de 10, hasta la milésima | P | numérico | — |
| 6B-OA8 | problemas con fracciones y decimales | — | LLM | numérico, fracción | — |

Resumen: **9 unidades solo paramétricas, 10 mixtas, 5 solo LLM.** Los niveles de dificultad no cambian la plantilla sino sus **parámetros**: nivel 1 = rango reducido y un paso; nivel 2 = rango completo del OA; nivel 3 = rango completo + paso adicional o contexto (la definición exacta por plantilla queda en cada ficha de plantilla, Fase IV, tarea 57).

### 4.1 Ejemplar A — plantilla paramétrica numérica: `5B-OA4-div-resto`

- **Parámetros:** divisor `d ∈ [2,9]`, cociente `q`, resto `r ∈ [0, d-1]`; dividendo `D = q·d + r` (3 dígitos → `q` se sortea para que `D ∈ [100, 999]`).
- **Niveles:** N1: `r = 0` y `d ∈ [2,5]` · N2: `r > 0` · N3: `r > 0` y la pregunta pide el resto o el cociente según variante.
- **Enunciado (plantilla fija):** "Calcula {D} : {d}. ¿Cuál es el cociente?" / variante N3: "...¿Cuál es el resto?".
- **Solución de referencia (generada por código):** pasos del algoritmo con los valores instanciados.
- **Errores comunes (fórmulas):** `q+1` ("siguió dividiendo de más"), `q` cuando se pedía `r` ("confundió cociente con resto"), `D−q·d` mal calculado.
- Correcta por construcción: `D` se construye desde `q` y `r`, nunca al revés.

### 4.2 Ejemplar B — plantilla paramétrica pictórica: `4B-OA9-suma-igual-den`

- **Parámetros:** denominador `d ∈ {2,3,4,5,6,8,10,12}`, numeradores `a, b ≥ 1` con `a + b ≤ d` (resultado propio).
- **Niveles:** N1: `d ≤ 4` con pictórico siempre · N2: cualquier `d`, pictórico en la mitad de los casos · N3: resta `a/d − b/d` o suma con resultado igual a 1.
- **Representación:** `{tipo: "fraccion-circulo", parametros: {denominador: d, partesDestacadas: [a, b]}}` — el cliente pinta `a` partes de un color y `b` de otro.
- **Errores comunes (fórmulas):** `(a+b)/2d` (sumó denominadores), `(a+b)` (ignoró el denominador), `a·b/d` (multiplicó numeradores).
- **Validación:** `aceptaEquivalentes: true` → si el resultado es 2/4 y el estudiante escribe 1/2, es correcta y se refuerza la equivalencia.

### 4.3 Ejemplar C — generación LLM: `4B-OA7-problema-dinero`

- **Prompt de generación** (estructura; redacción completa en tarea 27): texto oficial del OA (RF-D2) + nivel objetivo + contexto obligatorio chileno (pesos, montos realistas para un niño: $100–$10 000) + formato de salida = el JSON de §2 + 1 ejemplo gold del mismo OA como few-shot.
- **Restricciones que verifica la capa 2:** montos dentro del rango del OA y múltiplos de 10, enunciado ≤ 60 palabras, vocabulario de los textos escolares (RF-P6), una sola respuesta posible.
- **Niveles:** N1: una operación · N2: dos operaciones (compra + vuelto) · N3: no rutinario (información sobrante o pregunta inversa).
- Pasa el pipeline completo de §8 antes de llegar a `activo`.

---

## 5. Dimensionamiento del banco

| Parámetro | Valor | Justificación |
|---|---|---|
| Stock activo objetivo | **5 ejercicios por unidad × nivel** → 24 × 3 × 5 = **360** | variedad suficiente para no repetir en una sesión; dimensionado en AD-3/AD-9 |
| Mezcla estimada | ~255 paramétricos (71%) / ~105 verbales LLM (29%) | 9 unidades P completas + parte numérica de las 10 mixtas |
| Tasa de descarte esperada (LLM) | 10–20% | EDUMATH reporta ~7% defectuosos solo por matemática; se agrega margen por forma y adecuación |
| Revisión humana inicial | ~105 verbales × 1–2 min ≈ **2–3,5 h** (equipo) | solo problemas verbales; lo paramétrico se aprueba por plantilla (una vez) |
| Umbral de reposición | stock `activo` de una celda unidad×nivel < 5 | F5 de la arquitectura |
| Lote de reposición LLM | 10–20 ejercicios → 15–30 min de revisión | mantiene la revisión en sesiones cortas |

---

## 6. Representación pictórica (COPISI)

Tres tipos de figura, **generadas por código como SVG desde parámetros** (RF-D4; la priorización curricular promueve la progresión concreto → pictórico → simbólico):

| Tipo | Parámetros | Unidades que lo usan |
|---|---|---|
| `fraccion-circulo` / `fraccion-barra` | denominador, partes destacadas (1 o 2 colores) | 4B-OA8, 4B-OA9, 5B-OA7, 5B-OA9 |
| `recta-numerica` | rango [min, max], marcas, punto(s) a ubicar o ubicados | 4B-OA1, 4B-OA8, 5B-OA11, 6B-OA5 |
| `cuadricula-decimal` | cuadrícula 10×10, celdas pintadas (décimos/centésimos) | 5B-OA10 |

El LLM nunca produce SVG: si un ejercicio verbal quiere apoyo pictórico, emite `representacion` con tipo y parámetros, y la capa 2 valida que los parámetros sean coherentes con el enunciado (mismo denominador, mismo rango).

---

## 7. Gold standard (resuelto a mano por el equipo)

**2 ejercicios por OA ≈ 48**, escritos y resueltos a mano por el equipo, con roles separados para no contaminar la validación:

- **Set few-shot (1 por OA, ~24):** viaja como ejemplo en el prompt de generación del mismo OA (mejora formato y pertinencia curricular).
- **Set de validación (1 por OA, ~24):** reservado; **nunca aparece en prompts**. Es la base del set de casos de prueba pedagógicos de TT2 (tareas 70–72): contra él se mide la corrección ≥95% (RNF-P1) comparando las soluciones del sistema con las resoluciones humanas.

Ambos se almacenan en el banco con `fuente: "gold"` y quedan **fuera de la rotación** de ejercicios servidos a estudiantes. Esto materializa el "conjunto de ejercicios resueltos (gold standard)" del objetivo general del anteproyecto.

---

## 8. Pipeline de verificación (ejercicios generados por LLM)

Especificación de las 4 capas enunciadas en `arquitectura.md` F5. Solo la capa 4 involucra personas; ninguna capa usa al LLM como juez final (Maurya; BEA 2025):

| Capa | Qué verifica | Cómo | Falla → |
|---|---|---|---|
| **1. Aritmética exacta** | que `respuestaFinal` sea consistente con el enunciado y con cada paso de `solucionReferencia` | recomputación en código con aritmética exacta (fracciones como pares de enteros, decimales como enteros escalados — **nunca floats**). Para OA de fracciones: **doble pasada de generación independiente** (RF-D6); si las dos respuestas difieren → descarte directo | `descartado` |
| **2. Curricular y de forma** | operandos dentro del `rangoNumerico` del OA; formato ∈ soportados; longitud del enunciado (≤ 60 palabras en 4°, ≤ 80 en 5°–6°); vocabulario alineado a los textos oficiales (lista de términos, RF-P6); parámetros pictóricos coherentes; contexto chileno en dinero | reglas en código sobre el JSON | `descartado` |
| **3. Triaje LLM** | claridad del enunciado, coherencia enunciado↔solución, adecuación a la edad, unicidad de la respuesta | segunda llamada con rúbrica fija; **solo clasifica** `ok` / `dudoso` para priorizar la cola humana — no aprueba ni descarta por sí solo (F1≈0.58 como juez, BEA 2025) | marca `dudoso` |
| **4. Compuerta editorial humana** | sentido del enunciado, pertinencia al OA, adecuación cultural/etaria | un integrante del equipo revisa cada verbal (dudosos primero); ~1–2 min por ejercicio | `activo` o `descartado` |

Los ejercicios **paramétricos omiten las capas 1–4 por ejercicio**: la revisión humana se hace **una vez por plantilla** (se aprueba la plantilla y sus rangos por nivel; todo lo que instancia es correcto por construcción, AD-9).

---

## 9. Trazabilidad y puntos abiertos

| Requisito | Dónde se resuelve aquí |
|---|---|
| RF-D1 (unidades ↔ OA) | §1 catálogo curricular |
| RF-D2 (prompt con OA oficial) | §2 metadatos, §4.3, detalle en tarea 27 |
| RF-D3 (ejercicio autocontenido, solución no viaja) | §2 esquema |
| RF-D4 (COPISI pictórico) | §6 |
| RF-D5 (banco validado / gold standard) | §5 y §7 |
| RF-D6 (verificación reforzada en fracciones) | §8 capa 1 (doble pasada) |
| RF-D7 (formatos de respuesta) | §3 |
| RF-D8 (extensión Anillo 2) | §1 |
| RNF-P1, P3 (corrección ≥95%, contenido curricular) | §7 y §8 |
| RNF-C1 (costo) | §5 (71% del banco sin costo de API) |

**Se resuelve en tareas siguientes:** redacción completa de los prompts de generación y triaje (tarea 27); definición exacta de niveles por plantilla y fichas de las ~24 plantillas (Fase IV, tarea 57); cómo consume el motor adaptativo la celda unidad×nivel (tarea 22); DDL de base de datos (Fase III, tarea 41).
