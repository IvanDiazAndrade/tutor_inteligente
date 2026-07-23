# Modelo Pedagógico (Fase II, tarea 24)

**Proyecto:** Tutor inteligente basado en IA para el aprendizaje de matemáticas — eje de Números, 4°–6° básico.
**Documento:** Diseño preliminar del modelo pedagógico del ITS: repertorio de intervenciones del tutor, plantillas de prompts con guardas, andamiaje adaptativo, política de intentos y pistas, y degradación. Deriva de `requisitos.md` (RF-P1–P7, RNF-P2, P4) y de `arquitectura.md` (§3 "Orquestador pedagógico", AD-2: el LLM explica y guía, nunca califica). Usa la **banda y racha** de `modelo_estudiante.md` §6 y la **solución de referencia y errores comunes** de `modelo_dominio.md` §2.

**Decisiones tomadas con el equipo para este documento:** interacción por acciones estructuradas (sin texto libre del estudiante); 3 pistas alineadas a los pasos de la solución; refuerzo positivo por plantillas locales (el LLM se reserva para errores, pistas y explicaciones); explicación guiada ofrecida con botón tras 3 fallos, narrada por el LLM; tutor con personaje-mascota; andamiaje modulado por banda; guarda de no revelación en doble capa (system prompt + filtro programático de salida).

---

## 1. Principios

1. **El tutor guía, no resuelve ni califica** (AD-2, RF-P4): toda intervención del LLM está condicionada a la solución de referencia del ejercicio — nunca resuelve libre. La corrección ya ocurrió en código cuando el tutor habla.
2. **El error es material de trabajo, no falta** (RF-P5; habilidad curricular "g": *identificar un error, explicar su causa y corregirlo*): el tutor nombra la causa probable y acompaña la corrección, sin lenguaje punitivo ni comparativo.
3. **Mínima ayuda suficiente** (RF-P3): cada intervención entrega lo justo para que el siguiente paso lo dé el estudiante.
4. **Nadie queda bloqueado** (RF-P7): la escalera termina en resolver juntos, siempre con salida.
5. **Lo determinizable se determiniza** (extensión de AD-9 al diálogo): refuerzos, avisos y respuestas de emergencia son plantillas locales; el LLM se usa solo donde el lenguaje generado aporta valor irreemplazable.

---

## 2. Interacción estructurada

El estudiante **no escribe prosa al tutor**: interactúa respondiendo el ejercicio y con acciones de botón. Esto acota la superficie de las guardas (RNF-P2), hace el costo por sesión predecible (RNF-C1) y es coherente con RF-DA7 (no hay "conversación" que auditar).

| Acción | Disponible | Qué hace |
|---|---|---|
| **Responder** | siempre | corrección programática → refuerzo o retroalimentación de error |
| **Pedir pista** | hasta 3 por ejercicio | pista incremental (§4.3), descuenta puntos (RF-G1) e índice (−0,15) |
| **No entiendo** | tras una retroalimentación o pista | el LLM re-explica lo mismo con lenguaje más simple y otro enfoque; no revela más pasos (no descuenta: pedir aclaración no es pedir ayuda extra) |
| **Resolvamos juntos** | ofrecida tras 3 fallos (§5); visible también en el menú | explicación guiada completa + ejercicio análogo |
| **Otro ejercicio** | siempre | pasa a otro ejercicio de la celda; el actual queda como intento no terminado (no penaliza el índice: sin respuesta no hay evidencia) |

---

## 3. Repertorio de intervenciones

| Intervención | Quién la produce | Cuándo |
|---|---|---|
| Refuerzo positivo (RF-P1) | **plantilla local** (pool ≈20 mensajes, rotación sin repetición cercana; variantes con logro: "¡3 seguidas!", "¡subiste de nivel!") | respuesta correcta — el caso más frecuente: instantáneo y sin costo de API |
| Retroalimentación de error (RF-P2) | **LLM** (plantilla §4.2) | respuesta incorrecta |
| Pistas 1–3 (RF-P3) | **LLM** (plantilla §4.3) | a pedido |
| Re-explicación ("no entiendo") | **LLM** (misma plantilla, instrucción de simplificar) | a pedido |
| Explicación guiada (RF-P7) | **LLM narrando la solución de referencia** paso a paso, con pausa "siguiente →" entre pasos | aceptada tras 3 fallos |
| Avisos de sistema (degradación, formato inválido) | **plantilla local** | según evento |

Nota de arquitectura: esto corrige el flujo F2 de `arquitectura.md`, que asignaba el refuerzo positivo al LLM — queda actualizado: **la ruta de respuesta correcta no llama al LLM**.

---

## 4. Plantillas de prompts

Las plantillas viven versionadas fuera del código (RNF-M1) y se invocan vía el Adaptador LLM. Redacción final y calibración → tarea 27; aquí se fija estructura y contenido normativo.

### 4.1 System prompt del tutor (borrador normativo)

```
Eres «Octavio», un pulpo morado mago, tutor de matemáticas
para niños y niñas de 4° a 6° básico en Chile.

REGLAS INQUEBRANTABLES
1. NUNCA digas la respuesta final del ejercicio, ni en cifras, ni en palabras,
   ni mediante un cálculo que la deje a la vista. Si te la piden directamente
   o con rodeos, anima a intentarlo y ofrece una pista.
2. Basa TODO lo que digas únicamente en la SOLUCIÓN DE REFERENCIA entregada.
   No resuelvas por tu cuenta ni contradigas esos pasos.
3. Habla en español de Chile: tutea, frases cortas (máximo 3 por mensaje),
   vocabulario de los textos escolares (di "sustracción", "décimos",
   "denominador"; los montos de dinero en pesos con punto de miles).
4. Tono: alentador y curioso. Equivocarse es parte de aprender. PROHIBIDO
   comparar con otros niños, retar, ironizar o usar lenguaje de examen
   ("malo", "reprobado", "deberías saber").
5. No hables de temas ajenos al ejercicio actual. Si algo se sale del tema,
   vuelve amablemente al ejercicio.
```

### 4.2 Retroalimentación de error (RF-P2)

Variables inyectadas: enunciado · solución de referencia · respuesta del estudiante · patrón de `erroresComunes` detectado (si hay) · banda · racha reciente · pistas ya usadas.

- **Con patrón detectado:** "Explica en 1–2 frases la causa probable [causa del patrón] sin decir que consultaste una lista, y guía el primer paso correcto."
- **Sin patrón:** "No sabes qué error cometió: no inventes una causa. Señala en qué parte del procedimiento conviene revisar (según el primer paso de la solución de referencia donde su respuesta se vuelve incompatible) y anímalo a intentar de nuevo."

### 4.3 Pistas incrementales (RF-P3)

Tres pistas fijas por ejercicio, ancladas a `solucionReferencia`:

| Pista | Contenido normativo | Ejemplo (1/4 + 2/4) |
|---|---|---|
| 1 | orienta la **estrategia**, sin números del ejercicio | "Fíjate en los denominadores. ¿Son iguales o distintos?" |
| 2 | señala el **primer paso** de la solución de referencia | "Cuando los denominadores son iguales, se mantienen. Solo trabajas con los de arriba." |
| 3 | deja el ejercicio **a un paso del final** | "Suma solo los numeradores: 1 + 2. El denominador sigue siendo 4." |

No existe pista 4: después de la tercera solo queda intentar, y si acumula 3 fallos opera RF-P7 (§5). La pista 3 nunca puede contener la respuesta final — lo verifica el filtro de salida (§6).

---

## 5. Política de intentos: flujo del ejercicio

```
respuesta incorrecta nº1, nº2  → retroalimentación de error (§4.2)
respuesta incorrecta nº3       → además, botón: "¿Quieres que lo resolvamos juntos?"
   ├─ acepta  → explicación guiada: el LLM narra la solución de referencia paso a
   │           paso (pausa entre pasos); el ejercicio original se cierra sin más
   │           penalización (los 3 fallos ya actualizaron el índice) y se sirve un
   │           EJERCICIO ANÁLOGO nuevo de la misma celda, que cuenta normal.
   └─ rechaza → puede seguir intentando; cada nueva fallida re-ofrece el botón.
```

La explicación guiada usa la solución de referencia del ejercicio **original** (el niño ve resuelto lo que lo frustró) y el análogo verifica la transferencia — el par explicación + análogo es la materialización de RF-P7.

### Andamiaje por banda (adaptación más allá del nivel de dificultad)

La banda de `modelo_estudiante.md` §6 se inyecta como variable en todas las plantillas:

| Banda | Comportamiento del tutor |
|---|---|
| **Empezando** | tras el **primer** fallo, además de la retroalimentación, **ofrece** la pista 1 (no espera que la pida; aceptar cuenta como pista usada); explicaciones con un ejemplo cotidiano extra |
| **Practicando** | comportamiento base (§4) |
| **Dominado** | refuerzos y retroalimentaciones más breves; al dominar, invitación al desafío ("¿te atreves con uno difícil?" → celda de nivel superior o unidad sugerida) |

---

## 6. Guardas de no revelación: doble capa (RNF-P2)

1. **Capa preventiva — system prompt** (§4.1, regla 1): las guardas al estilo Bastani et al.
2. **Capa determinista — filtro de salida:** el orquestador inspecciona **cada** texto del LLM antes de enviarlo al cliente. Busca la `respuestaFinal` y sus equivalentes usando el mismo normalizador del corrector (`modelo_dominio.md` §3): cifras con coma o punto, fracciones equivalentes (6/8 si la respuesta es 3/4), y el número en palabras ("tres cuartos"). Si aparece → el mensaje **se descarta y se reemplaza por una pista de plantilla local**, y el evento queda registrado (métrica para la validación de TT2).

La capa 2 convierte la meta ≥95% de RNF-P2 en ~100% para la revelación literal; la validación adversarial de TT2 (tareas 70–74) mide lo que el filtro no puede atrapar (paráfrasis que guían de más). Excepción única: durante la **explicación guiada** (RF-P7) el filtro se relaja a los pasos intermedios pero sigue bloqueando la respuesta final del ejercicio **análogo** activo.

---

## 7. Degradación (F6)

Si el Adaptador declara indisponible a OpenAI, cada intervención tiene fallback local — la sesión nunca se corta:

| Intervención | Fallback local |
|---|---|
| Refuerzo positivo | sin cambio (ya es local) |
| Retroalimentación de error | plantilla: "Todavía no es. Revisa [primer paso de la solución de referencia]" + retroalimentación del patrón de `erroresComunes` si hubo match (texto ya escrito en el ejercicio) |
| Pistas | los textos de las 3 pistas se **pre-generan junto al ejercicio** y se persisten en el banco → las pistas funcionan igual sin LLM |
| Explicación guiada | pasos de `solucionReferencia` renderizados tal cual |
| Aviso | mensaje local: "Octavio está descansando un momento; igual podemos seguir practicando" (RNF-R3) |

Consecuencia de diseño para el banco: **las pistas se generan y verifican junto con el ejercicio** (se agregan al esquema de `modelo_dominio.md` §2 como `pistas[3]`, pasan las capas del pipeline y el filtro de no revelación en frío). En operación normal el LLM puede reformularlas al vuelo con la banda del estudiante; en degradación se sirven tal cual.

---

## 8. Trazabilidad y puntos abiertos

| Requisito | Dónde se resuelve aquí |
|---|---|
| RF-P1 (refuerzo inmediato) | §3 (plantillas locales) |
| RF-P2 (explicar causa sin revelar) | §4.2 + §6 |
| RF-P3 (pistas incrementales, resistencia a "dame la respuesta") | §4.3 + §6 |
| RF-P4 (condicionado a la solución de referencia) | §1, §4.1 regla 2 |
| RF-P5 (tono, mentalidad de crecimiento, sin comparaciones) | §4.1 reglas 4–5 |
| RF-P6 (español de Chile, vocabulario escolar) | §4.1 regla 3 |
| RF-P7 (N intentos → explicación guiada) | §5 |
| RNF-P2 (no revelación ≥95%) | §6 (doble capa) |
| RNF-R3 (degradación) | §7 |
| RNF-C1 (costo) | §2, §3 (correctas y avisos sin LLM; pistas pre-generadas reutilizables) |

**Se resuelve en tareas siguientes:** diseño visual de la mascota (definida: «Octavio», pulpo morado mago con sombrero estampado de símbolos operacionales y varitas en los tentáculos) y ubicación de los botones → tarea 25 (mockups); redacción final y versionado de prompts, few-shots de tono y parámetros de llamada → tarea 27; evaluación del tono (dimensión *tutor tone* de Maurya) y prueba adversarial → tareas 70–74. **Cambios que propagar:** `arquitectura.md` F2 (refuerzo sin LLM) y esquema del ejercicio con `pistas[3]` (`modelo_dominio.md` §2).
