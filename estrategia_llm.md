# Estrategia de Integración con el LLM (Fase II, tarea 27)

**Proyecto:** Tutor inteligente basado en IA para el aprendizaje de matemáticas — eje de Números, 4°–6° básico.
**Documento:** Estrategia completa de integración con el LLM: modelo y sustitutos, operaciones del Adaptador con sus parámetros, prompts de generación y triaje, política de datos hacia el proveedor, resiliencia y plan de calibración. Consolida lo que los diseños anteriores delegaron aquí: prompt de generación (`modelo_dominio.md` §4.3), redacción y versionado de prompts pedagógicos (`modelo_pedagogico.md` §4), parámetros de llamada (`stack_tecnologico.md` §6).

**Decisiones tomadas con el equipo:** GPT-5.4 nano con snapshot congelado como modelo principal (decisión del 23-jul-2026, reemplaza al GPT-4o mini del anteproyecto por obsolescencia sobrevenida — ver §2 y reconciliación en el informe TT1); prompts escritos en español; el tutor solo recibe contexto del ejercicio actual (sin memoria de sesión); el alias del estudiante nunca viaja al proveedor (se inserta localmente).

---

## 1. Qué hace y qué no hace el LLM (síntesis normativa)

| El LLM **sí** | El LLM **nunca** |
|---|---|
| genera ejercicios verbales pre-verificados (F5) | corrige respuestas (AD-2: corrector programático) |
| explica errores y guía sin revelar (F2) | es juez final de calidad (pipeline capa 4 humana) |
| reformula pistas pre-generadas y narra la explicación guiada | se llama al servir un ejercicio (F1: banco, ≤2 s) |
| hace triaje clasificatorio en el pipeline (capa 3) | genera el refuerzo de respuestas correctas (plantillas locales) |
| | produce SVG (la representación es paramétrica, dibujada por código) |
| | recibe datos personales, ni siquiera el alias (RNF-S3) |

## 2. Modelo

- **Principal: GPT-5.4 nano con snapshot congelado** (el identificador exacto del snapshot se fija al configurar el entorno, Fase III tarea 36, y vive en configuración — un solo lugar). Precio ~US$0,20 / 1,25 por millón de tokens (julio 2026, verificar contra la página oficial) y **reproducibilidad**: la validación de TT2 se ejecuta contra una versión que no cambia entre calibración y medición. Reemplaza al GPT-4o mini seleccionado en el anteproyecto (obsolescencia sobrevenida durante TT1); cambio pendiente de ratificación con el profesor guía.
- Antecedente del cambio: GPT-4o mini sigue disponible en la API sin fecha de retiro anunciada, pero fue retirado de ChatGPT (feb 2026) y de Azure AI Foundry (mar 2026), y GPT-4.1 mini — su sustituto documentado originalmente — también quedó *legacy*. Ante ese cuadro se optó por saltar directamente a la generación vigente en lugar de encadenar modelos en retirada.
- **Sustitutos documentados** (el Adaptador AD-4 + prompts externos hacen del cambio una edición de configuración; precios de julio 2026 según agregadores públicos — verificar contra la página oficial de OpenAI al configurar):
  - **GPT-5.4 mini** (~US$0,75/4,50): escalón superior del mismo proveedor si nano no alcanza los umbrales; exige re-estimar el presupuesto (podría exceder el tope en el mes de validación).
  - **Gemini Flash-Lite** (~US$0,10/0,40): sustituto de **otro proveedor**, prueba concreta de RNF-M3.
- **Validación del modelo**: la prueba piloto de la calibración (tarea 58) mide la tasa real de GPT-5.4 nano sobre el conjunto de referencia antes de la generación masiva del banco; si no alcanza los umbrales, se escala a GPT-5.4 mini (re-estimando presupuesto) y, como salida de proveedor, a Gemini Flash-Lite.
- Presupuesto y contabilidad de tokens: definidos en `stack_tecnologico.md` §4 (tope US$5/mes, alerta 80%, corte 100% → F6).

## 3. Operaciones del Adaptador

Interfaz única hacia el proveedor (AD-4). Parámetros iniciales — se calibran en la tarea 58:

| Operación | Cuándo | Temp. | Salida | Contexto que viaja | Fallback (F6) |
|---|---|---|---|---|---|
| `generarEjercicio` | lote asíncrono (F5) | 0,9 | **structured output** con el esquema JSON del ejercicio (incluye `pistas[3]`) | texto oficial del OA + curso + nivel + restricciones de forma + 1 ejemplo gold del OA | el lote se pospone; el banco sigue sirviendo |
| `generarEjercicio` (2ª pasada fracciones, RF-D6) | tras la 1ª pasada | 0,9 | ídem | mismo prompt, generación independiente | — (comparación programática de `respuestaFinal`) |
| `triajeEjercicio` | pipeline capa 3 | 0,0 | structured output `{veredicto: ok\|dudoso, razones[]}` | ejercicio completo + rúbrica | sin triaje: todo va a revisión humana |
| `generarRetroalimentacion` | respuesta incorrecta (F2) | 0,4 | texto ≤3 frases | ejercicio + solución de referencia + respuesta del niño + patrón detectado + intentos/pistas **de este ejercicio** + banda/racha | plantilla local + `retroalimentacion` del patrón |
| `generarPista` | pista o "no entiendo" | 0,4 | texto ≤2 frases | pista pre-generada a reformular + banda + qué pistas ya vio | la pista almacenada, tal cual |
| `narrarExplicacionGuiada` | RF-P7 aceptada | 0,3 | pasos narrados uno a uno | pasos de `solucionReferencia` + banda | pasos renderizados tal cual |

Notas transversales: **sin memoria de sesión** — cada llamada es autocontenida con el ejercicio actual (barato, sin estado, coherente con la interacción estructurada); **todas** las salidas dirigidas al estudiante pasan el **filtro de no revelación** (`modelo_pedagogico.md` §6) antes de enviarse; `max_tokens` acotado por operación (≈700 generación, ≈120 mensajes del tutor).

## 4. Política de datos hacia el proveedor (RNF-S3, Ley 21.719)

| Viaja a OpenAI | Nunca viaja |
|---|---|
| contenido matemático: enunciados, soluciones, respuestas numéricas del estudiante | alias o nombre (el LLM escribe con el marcador `{nombre}`; el orquestador lo sustituye **en el servidor** después del filtro) |
| curso escolar (4°/5°/6°) y texto del OA — necesarios para adecuar lenguaje | identificadores internos (ids de usuario/estudiante/sesión) |
| banda de dominio y racha como variables pedagógicas ("Empezando", "2 seguidas") | correo del apoderado, PIN, cualquier campo de las entidades `Usuario`/`Estudiante` |
| | historial más allá del ejercicio actual |

Regla operativa: el Adaptador expone funciones que **solo aceptan estos campos** — la minimización se garantiza por la firma de la interfaz, no por disciplina. Además: API de OpenAI con retención estándar sin entrenamiento sobre datos de clientes; datos sintéticos durante todo TT1/TT2 (sin menores reales).

## 5. Resiliencia

- **Timeout por llamada: 8 s** (deja margen dentro del ≤10 s p90 de RNF-R1 contando el filtro y la red del cliente).
- **Reintentos: 2**, con backoff (0,5 s → 2 s), solo ante errores transitorios (timeout, 429, 5xx); nunca ante contenido filtrado (eso va directo a fallback local).
- **Circuit breaker**: 5 fallos consecutivos → el Adaptador se declara degradado por 60 s y todas las operaciones usan su fallback (F6); reintento de sondeo al expirar. La práctica **nunca se interrumpe**: por diseño, cada operación tiene fallback local (tabla §3).
- Registro por llamada: operación, tokens in/out, latencia, resultado, `versionPrompt` — alimenta la contabilidad (RNF-C1) y el análisis de calidad por versión.

## 6. Prompts (borradores normativos; versionados en `/prompts`)

En **español** (auditables por el equipo, publicables en anexos, sin fugas de inglés hacia el niño). El system prompt del tutor ya está redactado en `modelo_pedagogico.md` §4.1; aquí los dos que faltaban:

### 6.1 Generación de ejercicio verbal (`gen-ejercicio.jinja`, esquema forzado por structured output)

```
Eres un autor de ejercicios de matemática para estudiantes chilenos de {curso}° básico.

OBJETIVO DE APRENDIZAJE (texto oficial de las Bases Curriculares):
«{oaTextoOficial}»

Crea UN problema verbal original, nivel {nivel} de 3, que ejercite exactamente ese
objetivo. Reglas:
- Contexto cotidiano chileno (dinero en pesos con punto de miles, situaciones de
  colegio, feria, cocina, deportes). Enunciado de máximo {maxPalabras} palabras.
- Una sola respuesta correcta, en formato {formatoRespuesta}.
- Números dentro de este rango permitido: {rangoNumerico}.
- solucionReferencia: los pasos del procedimiento, uno por elemento, en lenguaje
  simple para un niño de {curso}° básico.
- erroresComunes: 2 o 3 respuestas incorrectas que un niño daría por un error de
  procedimiento típico, cada una con su causa y una retroalimentación breve que
  NO revele la respuesta correcta.
- pistas: exactamente 3, progresivas: (1) orienta la estrategia sin números del
  ejercicio, (2) señala el primer paso, (3) deja el problema a un paso del final
  SIN decir el resultado.
- Vocabulario de los textos escolares chilenos ("sustracción", "décimos").

EJEMPLO DE REFERENCIA (mismo objetivo, imítalo en formato y calidad, no en contenido):
{ejemploGold}
```

### 6.2 Triaje de calidad (`triaje-ejercicio.jinja`, temperatura 0)

```
Eres un revisor de ejercicios de matemática escolar chilena. NO corriges la
aritmética (ya fue verificada por otro medio). Evalúa el siguiente ejercicio según
esta rúbrica y responde solo el JSON pedido:

1. CLARIDAD: ¿el enunciado se entiende sin ambigüedad a la primera lectura,
   para un niño de {curso}° básico?
2. COHERENCIA: ¿la solución de referencia resuelve exactamente lo que el
   enunciado pregunta, sin pasos de más ni de menos?
3. ADECUACIÓN: ¿contexto y vocabulario apropiados para la edad y para Chile?
4. UNICIDAD: ¿existe una y solo una respuesta correcta posible?

Si las cuatro se cumplen claramente: veredicto "ok". Ante CUALQUIER duda:
veredicto "dudoso" con las razones. Tu clasificación solo ordena la cola de
revisión humana; no apruebas ni rechazas.

EJERCICIO: {ejercicioJson}
```

## 7. Calibración y pruebas (puente a TT2)

- **Tarea 58 (calibración):** iterar cada prompt contra el **gold few-shot** midiendo: tasa de descarte del pipeline por capa, corrección aritmética, calidad de pistas/erroresComunes; ajustar temperatura y redacción. Cada iteración = nueva `versionPrompt` registrada — la calidad es trazable por versión.
- **Tareas 70–72 (validación):** contra el **gold de validación reservado** (que jamás apareció en prompts): ≥95% corrección (RNF-P1), no revelación adversarial ≥95% (RNF-P2, midiendo lo que el filtro determinista no cubre), dimensión de tono (Maurya).
- Si la calibración no alcanza los umbrales con GPT-5.4 nano → se repite con GPT-5.4 mini (§2) y el cambio se documenta en la reconciliación con el anteproyecto.

## 8. Trazabilidad y puntos abiertos

| Requisito | Dónde se resuelve aquí |
|---|---|
| RF-D2 (prompt con OA oficial) | §6.1 |
| RF-P4 (condicionado a solución de referencia) | §3 (contexto por operación) |
| RNF-S3 / Ley 21.719 (solo contenido matemático) | §4 (garantizado por interfaz) |
| RNF-R1/R3 (latencia, degradación) | §5 |
| RNF-M1/M3 (prompts externos, proveedor sustituible) | §2, §6 |
| RNF-C1 (costo) | §2 → `stack_tecnologico.md` §4 |

**Abierto para fases siguientes:** valores definitivos de temperatura/max_tokens y redacción final de prompts tras calibración (tarea 58); snapshot exacto del modelo al configurar el entorno (tarea 36); riesgo de obsolescencia del modelo y deriva del proveedor → tarea 28 (actualizado: el caso GPT-4o mini durante TT1 validó la mitigación del adaptador único).
