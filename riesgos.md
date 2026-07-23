# Análisis de Riesgos del Proyecto (Fase II, tarea 28)

**Proyecto:** Tutor inteligente basado en IA para el aprendizaje de matemáticas — eje de Números, 4°–6° básico.
**Documento:** Identificación y evaluación de riesgos para TT1→TT2, con mitigación (preventiva, ya incorporada al diseño cuando corresponde) y contingencia (reactiva). Escala cualitativa: probabilidad e impacto **B**ajo / **M**edio / **A**lto; exposición = combinación de ambos. Los riesgos con mitigación "por diseño" citan el documento donde ya quedó resuelta.

---

## 1. Riesgos técnicos — LLM y contenido

| ID | Riesgo | Prob. | Imp. | Exposición |
|---|---|---|---|---|
| R1 | **Obsolescencia de GPT-4o mini**: es *legacy* desde enero 2026; OpenAI podría anunciar su retiro durante TT2 | M | M | **Media** |
| R2 | **Calidad de generación insuficiente**: la calibración no alcanza los umbrales (descartes ≫20%, corrección <95% contra gold) | M | A | **Alta** |
| R3 | **Revelación de respuestas**: el tutor entrega la solución ante insistencia del estudiante | B | A | **Media** |
| R4 | **Deriva del proveedor**: cambios de API, precios o comportamiento del modelo entre calibración y validación | M | M | **Media** |
| R5 | **Caída de OpenAI** durante una demo o la validación | M | B | **Baja** |
| R6 | **Defectos del corrector**: un falso "incorrecto" (parsing, equivalencias) frustra al estudiante y contamina el índice de dominio | M | A | **Alta** |

- **R1** — Mitigación por diseño: snapshot congelado + Adaptador único + prompts externos hacen del cambio de modelo una edición de configuración; sustitutos ya evaluados (GPT-4.1 mini, Gemini Flash-Lite) en `estrategia_llm.md` §2. Contingencia: migrar y re-ejecutar la calibración (tarea 58) contra el mismo gold standard — el esfuerzo es acotado y medible.
- **R2** — Es el riesgo central del proyecto (la tesis afirma que un LLM puede generar contenido educativo confiable). Mitigación por diseño: pipeline de 4 capas + doble pasada en fracciones (`modelo_dominio.md` §8), 71% del banco paramétrico sin LLM (AD-9), calibración temprana con versiones trazables. Contingencia escalonada: (1) upgrade a GPT-4.1 mini; (2) subir la proporción paramétrica y reducir los verbales por unidad; (3) último recurso: completar a mano los verbales de las unidades más débiles — el esquema del ejercicio es idéntico sea quien sea el autor.
- **R3** — Mitigación por diseño: doble capa (system prompt + filtro determinista de salida, `modelo_pedagogico.md` §6) — la revelación literal queda en ~0; queda el residuo de "guiar de más", que se mide en la validación adversarial (tareas 70–72). Contingencia: endurecer plantillas de pistas y bajar temperatura.
- **R4** — Mitigación: snapshot fija el comportamiento; el tope de costo (US$5) con corte automático acota cualquier cambio de precios; el registro por `versionPrompt` + versión de modelo permite atribuir cambios de calidad. Contingencia: RNF-M3 — sustituir proveedor vía Adaptador.
- **R5** — Mitigación por diseño: F6 degradación (`arquitectura.md`) — pistas pre-generadas, plantillas locales, corrección y dashboard nunca dependen del LLM; **el sistema se puede demostrar completo en modo degradado**. Contingencia: ninguna necesaria; es un escenario ensayable (y conviene mostrarlo como fortaleza en la defensa).
- **R6** — Mitigación por diseño: aritmética exacta nativa (`Fraction`/`Decimal`, razón de elegir Python en `stack_tecnologico.md` §3), políticas de equivalencia explícitas por formato, errores de formato no cuentan como intento. Contingencia: los casos gold + pruebas unitarias del corrector (tarea 52) son la red; ante un falso incorrecto en producción de prueba, el ejercicio se retira del banco (`estado: retirado`) sin tocar código.

## 2. Riesgos de gestión y equipo

| ID | Riesgo | Prob. | Imp. | Exposición |
|---|---|---|---|---|
| R7 | **Capacidad del equipo (2 personas)**: las Fases IV–V concentran implementación + pruebas + validación en un semestre | A | A | **Alta** |
| R8 | **Corrimiento de alcance**: tentación de sumar Anillo 2, chat libre, respuesta abierta, más gamificación | M | M | **Media** |
| R9 | **Retroalimentación tardía** del profesor guía en hitos clave | B | M | **Baja** |

- **R7** — El riesgo de gestión dominante. Mitigación: alcance en anillos con Anillo 2 explícitamente opcional (RF-D8 es Could), 33 RF priorizados MoSCoW (22 Must), banco mayoritariamente paramétrico (menos horas de revisión), levantamientos semanales de 30 min (tarea 53) para detectar atraso temprano. Contingencia ordenada por MoSCoW: se recortan Could y Should (p. ej. RF-DA5 sugerencias, RF-D4 pictórico completo, modulación por banda) antes que cualquier Must; el corte se documenta en el informe como decisión de alcance, no como falla.
- **R8** — Mitigación: los 8 documentos de diseño de Fase II registran cada decisión con su alternativa descartada — reabrir una exige argumento nuevo, no entusiasmo. Regla del equipo: nada entra sin salir algo equivalente.
- **R9** — Mitigación: validaciones ya agendadas en el plan (tareas 4, 43, 75, 88); enviar material con antelación a cada reunión. Contingencia: avanzar con supuestos documentados y marcarlos como pendientes de validación.

## 3. Riesgos de validación (TT2)

| ID | Riesgo | Prob. | Imp. | Exposición |
|---|---|---|---|---|
| R10 | **Falta de evaluadores**: no reunir expertos para la heurística ni ~10+ adultos para el SUS | M | M | **Media** |
| R11 | **Umbrales no alcanzados**: SUS <70 o corrección <95% en la medición final | M | A | **Alta** |

- **R10** — Mitigación: URL pública (evaluación remota sin coordinación presencial, `stack_tecnologico.md`); reclutamiento anticipado. Contingencia: heurística con docentes/ayudantes UTEM como expertos de usabilidad; SUS con apoderados del círculo cercano de ambos integrantes (perfil objetivo: adulto no técnico).
- **R11** — Mitigación: los umbrales se persiguen desde el diseño (calibración temprana, filtro determinista, aritmética exacta), y el plan incluye ciclo de mejora + re-ejecución (tareas 76–78). Contingencia metodológica: si tras el ciclo no se alcanza un umbral, **se reporta el valor real con análisis de causas** — el objetivo del TT es validar el método de evaluación, no garantizar el número; un 88% honesto y explicado defiende mejor que un 95% frágil.

## 4. Riesgos legales, éticos y de infraestructura

| ID | Riesgo | Prob. | Imp. | Exposición |
|---|---|---|---|---|
| R12 | **Ley 21.719 / ética con menores**: objeción de la comisión o del comité al tratamiento de datos | B | A | **Media** |
| R13 | **Contenido inapropiado** generado por el LLM llega a un estudiante | B | A | **Media** |
| R14 | **Limitaciones del hosting gratuito** (sleep, cuotas) durante demos o validación | M | B | **Baja** |
| R15 | **Pérdida de trabajo**: repositorio, base de datos o documentos | B | A | **Media** |

- **R12** — Mitigación por diseño: sin menores reales en todo TT1/TT2 (datos sintéticos), minimización garantizada por la firma del Adaptador (`estrategia_llm.md` §4), apoderado como titular de la cuenta, alias sin PII. La postura es conservadora a propósito: más protección de la exigida.
- **R13** — Mitigación por diseño: los ejercicios que llegan al estudiante pasaron compuerta humana (capa 4) o son paramétricos (sin LLM); los mensajes en vivo del tutor están acotados por prompt + filtro y por la interacción estructurada (el niño no puede desviar el tema). Contingencia: `estado: retirado` inmediato + revisión del lote afectado.
- **R14** — Mitigación: plan pagado (~US$7) solo el mes de validación; demos importantes con la instancia "despierta" de antemano. Contingencia: la app también corre local (Docker) para demos presenciales.
- **R15** — Mitigación: monorepo en GitHub (todo lo textual, incluidos prompts y documentos), dumps automáticos de PostgreSQL (Render los incluye), y el banco de ejercicios es regenerable por diseño (pipeline + gold en el repo).

## 5. Mapa de exposición

|  | **Impacto B** | **Impacto M** | **Impacto A** |
|---|---|---|---|
| **Prob. A** | — | — | R7 |
| **Prob. M** | R5, R14 | R1, R4, R8, R10 | **R2, R6, R11** |
| **Prob. B** | — | R9 | R3, R12, R13, R15 |

Los cuatro que exigen seguimiento activo (revisión en cada levantamiento semanal, tarea 53): **R7** (capacidad), **R2** (calidad de generación), **R6** (corrector) y **R11** (umbrales). No es casualidad que los cuatro tengan mitigación estructural ya incorporada: el diseño de la Fase II se construyó alrededor de ellos (AD-2, AD-3, AD-9, pipeline, gold standard, MoSCoW).

## 6. Riesgos aceptados (sin mitigación adicional)

- Dependencia de un proveedor comercial de LLM como supuesto del proyecto (el anteproyecto lo declara; RNF-M3 acota el costo de salida).
- Los parámetros pedagógicos (α, umbrales, pistas) son valores razonados sin validación con estudiantes reales — limitación declarada del alcance (sin menores), explícita en `modelo_estudiante.md` §9.
- El SUS mide la percepción del apoderado, no la del niño (limitación metodológica del anteproyecto, ya documentada).
