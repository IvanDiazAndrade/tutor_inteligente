# Levantamiento de Requerimientos — Tutor Inteligente de Matemáticas (Fase II, tareas 19–20)

**Proyecto:** Desarrollo de un tutor inteligente basado en IA para el apoyo del aprendizaje de matemáticas en estudiantes de educación básica (eje de Números, 4°–6° básico).
**Documento:** Especificación de requerimientos funcionales y no funcionales.
**Estado:** Borrador para revisión del equipo.

---

## 1. Actores del sistema

| Actor | Descripción |
|---|---|
| **Estudiante** | Niño/a de 4°–6° básico (9–12 años). Resuelve ejercicios, recibe retroalimentación del tutor, acumula puntos y desbloquea niveles. Usuario principal de la interfaz de aprendizaje. |
| **Apoderado** | Adulto responsable del estudiante. Administra la cuenta (crea el perfil del estudiante, define el curso), sostiene la rutina de uso en el hogar y consulta el dashboard de progreso. Se asume competencia digital básica (nivel "usuario de WhatsApp", según evidencia de Sugimaru & Glave 2021). |
| **GPT-4o mini (actor de sistema)** | Modelo de lenguaje externo (API OpenAI). Genera ejercicios y explicaciones, y evalúa respuestas bajo las restricciones del módulo pedagógico. No es un usuario humano; se modela como actor secundario en los casos de uso (como ya está en el diagrama CU del anteproyecto). |

> **Nota de coherencia con el anteproyecto (Avance 1, §6.2):** el documento de Hito 1 declaró el rol apoderado/docente como *limitación* ("no incluye los roles de docente/apoderado y administrador"). El cambio de alcance acordado por el equipo incorpora al **apoderado** como segundo actor con un dashboard de progreso; el rol **docente** y el rol **administrador** siguen fuera de alcance. Este documento asume ese nuevo alcance; el informe final de TT1 debe actualizar §6.1/§6.2 en consecuencia (ver §5 de este documento).

---

## 2. Alcance funcional de referencia

- **Dominio curricular:** eje de Números y Operaciones, 4°–6° básico, según Bases Curriculares (Decreto 439/2012) y Priorización Curricular 2023–2025. Cobertura en dos anillos (ver `curriculo_4a6_matematica.md`):
  - **Anillo 1 (núcleo, comprometido):** 4°: OA 1–3, 5–9 · 5°: OA 1, 3–7, 9–13 · 6°: OA 2, 5–8.
  - **Anillo 2 (opcional):** 6° OA3–4 (razón y porcentaje), 4° OA10–12, 5° OA2/OA5, 6° OA1.
- **Casos de uso existentes (anteproyecto):** CU-1 Iniciar Sesión, CU-2 Seleccionar Unidad, CU-3 Resolver Ejercicio, CU-4 Recibir Retroalimentación, CU-5 Desbloquear Nivel, CU-6 Ver puntaje y nivel, CU-7 Generar Contenido (GPT), CU-8 Evaluar Respuesta (GPT).
- **Casos de uso nuevos por el cambio de alcance:** CU-9 Gestionar cuenta del estudiante (Apoderado), CU-10 Consultar dashboard de progreso (Apoderado), CU-11 Solicitar pista (Estudiante — refina CU-4), CU-12 Adaptar dificultad (Sistema).

**Prioridades:** se usa MoSCoW — **[M]** Must (esencial para el prototipo de TT2), **[S]** Should (importante, se implementa si el calendario lo permite), **[C]** Could (deseable, candidato a trabajo futuro).

---

## 3. Requerimientos funcionales (tarea 19)

### 3.1 Módulo de acceso y cuentas (RF-A)

| ID | Requerimiento | Prioridad | CU |
|---|---|---|---|
| RF-A1 | El sistema permitirá al apoderado registrarse con correo y contraseña, y crear un (1) perfil de estudiante asociado, indicando nombre/alias y curso (4°, 5° o 6° básico). | M | CU-9 |
| RF-A2 | El sistema permitirá iniciar y cerrar sesión con dos roles diferenciados: `estudiante` y `apoderado`, con vistas e interfaces distintas por rol. | M | CU-1 |
| RF-A3 | El acceso del estudiante desde el dispositivo del hogar usará un mecanismo simple y adecuado a su edad (p. ej., selección de perfil + PIN corto definido por el apoderado), evitando contraseñas alfanuméricas complejas. | S | CU-1 |
| RF-A4 | El apoderado podrá editar el curso del estudiante (p. ej., promoverlo de 4° a 5°) sin perder el historial de progreso. | S | CU-9 |
| RF-A5 | El perfil del estudiante se creará con datos mínimos (alias y curso); el sistema no solicitará RUT, colegio, fecha de nacimiento exacta ni otros datos identificatorios del menor. | M | CU-9 |

### 3.2 Módulo del dominio: contenido y ejercicios (RF-D)

| ID | Requerimiento | Prioridad | CU |
|---|---|---|---|
| RF-D1 | El sistema organizará el contenido en unidades temáticas mapeadas 1:1 a los OA del Anillo 1 del eje de Números (cada unidad declara su OA, curso y si el OA es basal o complementario según la Priorización Curricular 2023–2025). | M | CU-2 |
| RF-D2 | El sistema generará ejercicios mediante GPT-4o mini incluyendo en el prompt el **texto oficial completo del OA** (redacción de las Bases Curriculares), el nivel de dificultad objetivo y el formato de salida estructurado. | M | CU-7 |
| RF-D3 | Cada ejercicio generado incluirá, en el mismo objeto: enunciado, **solución de referencia paso a paso**, respuesta final, y una lista de errores comunes anticipados con su retroalimentación específica. La solución de referencia nunca se envía al cliente del estudiante. | M | CU-7 |
| RF-D4 | Los ejercicios cubrirán los tres tipos de representación de la estrategia COPISI cuando el OA lo permita: los enunciados podrán incluir representaciones pictóricas (fracciones como figuras, recta numérica) además de simbólicas. | S | CU-7 |
| RF-D5 | El sistema mantendrá un **banco de ejercicios validados** (gold standard): los ejercicios generados se persisten y los marcados como defectuosos durante la validación se excluyen de la rotación. | M | CU-7 |
| RF-D6 | Para los OA de fracciones (tópico con mayor tasa de error documentada en generación por LLM — EDUMATH), el sistema aplicará verificación adicional de la solución de referencia antes de servir el ejercicio (p. ej., re-verificación aritmética programática o doble pasada del modelo). | S | CU-7 |
| RF-D7 | El sistema soportará tres formatos de respuesta, todos validables programáticamente: numérica (entero/decimal), fracción (incluye números mixtos) y ordenar/comparar. Selección múltiple y respuesta abierta en lenguaje natural quedan fuera del prototipo (decisión tarea 23: los errores comunes se usan para diagnóstico, no como distractores). | M | CU-3 |
| RF-D8 | (Anillo 2) El sistema podrá extenderse con unidades de razón y porcentaje (6° OA3–4) y decimales tempranos (4° OA10–12) sin cambios de arquitectura, solo agregando unidades al catálogo. | C | CU-2 |

### 3.3 Módulo pedagógico: tutoría y retroalimentación (RF-P)

| ID | Requerimiento | Prioridad | CU |
|---|---|---|---|
| RF-P1 | Ante una respuesta correcta, el sistema entregará confirmación inmediata con refuerzo positivo y el puntaje obtenido. | M | CU-4 |
| RF-P2 | Ante una respuesta incorrecta, el sistema identificará el error, explicará su causa probable y guiará la corrección **sin revelar la respuesta final** (alineado con la habilidad curricular "g" de las Bases y las guardas de Bastani et al.). | M | CU-4 |
| RF-P3 | El estudiante podrá solicitar pistas incrementales; cada pista entrega la mínima información adicional necesaria. El sistema **nunca revelará la solución completa**, incluso ante solicitudes directas o reformuladas del estudiante (resistencia a "dame la respuesta"). | M | CU-11 |
| RF-P4 | Toda retroalimentación del tutor se generará condicionada a la **solución de referencia** del ejercicio (incluida en el prompt), no a una resolución libre del modelo, para mitigar alucinaciones. | M | CU-8 |
| RF-P5 | El tono del tutor será alentador y no punitivo: normaliza el error como parte del aprendizaje e incluye mensajes de mentalidad de crecimiento; queda prohibido el lenguaje que compare al estudiante con otros. Este tono se especifica en el system prompt y se evalúa en la validación (dimensión *tutor tone* de Maurya et al.). | M | CU-4 |
| RF-P6 | La retroalimentación y las explicaciones se entregarán en español de Chile, con vocabulario matemático consistente con el usado en los textos escolares oficiales (p. ej., "sustracción", "décimos/centésimos"). | M | CU-4 |
| RF-P7 | Tras N intentos fallidos consecutivos (parámetro, por defecto 3), el sistema ofrecerá una explicación guiada completa del procedimiento con un ejercicio análogo nuevo, en lugar de dejar al estudiante bloqueado. | S | CU-4 |

### 3.4 Módulo del estudiante: seguimiento y adaptividad (RF-E)

| ID | Requerimiento | Prioridad | CU |
|---|---|---|---|
| RF-E1 | El sistema registrará cada intento con: ejercicio, OA, dificultad, respuesta emitida, correcto/incorrecto, nº de pistas usadas, tiempo empleado y fecha/hora. | M | CU-3 |
| RF-E2 | El sistema mantendrá por estudiante un **índice de dominio por OA** (valor 0–1 actualizado con los últimos intentos, p. ej. media móvil ponderada por dificultad). Se adopta deliberadamente un modelo simple e interpretable (Self 1990/1999 vía Bull & Kay 2016) en lugar de knowledge tracing profundo, por ausencia de datos históricos de entrenamiento (cold start) y por la necesidad de que el apoderado entienda el indicador. | M | CU-12 |
| RF-E3 | El sistema adaptará la dificultad del siguiente ejercicio según el índice de dominio del OA activo: subirá tras rachas de aciertos, bajará tras errores repetidos, dentro de 3 niveles de dificultad por unidad. | M | CU-12 |
| RF-E4 | Al iniciar una unidad sin historial, el sistema partirá en dificultad baja y usará los primeros ejercicios como diagnóstico rápido para calibrar el índice de dominio inicial. | S | CU-12 |
| RF-E5 | El estudiante podrá consultar su propio progreso en formato apropiado a su edad (medidores de habilidad simples por unidad — skill meters, la representación OLM con mejor evidencia según Bull & Kay). | S | CU-6 |

### 3.5 Gamificación (RF-G)

| ID | Requerimiento | Prioridad | CU |
|---|---|---|---|
| RF-G1 | El sistema otorgará puntos por ejercicio correcto (ponderados por dificultad y descontando pistas usadas) y niveles de progreso por unidad temática. | M | CU-5, CU-6 |
| RF-G2 | El avance de nivel dentro de una unidad dependerá del índice de dominio, no solo de la cantidad de ejercicios resueltos. | S | CU-5 |
| RF-G3 | La gamificación **no incluirá** rankings, tablas de posiciones, comparación entre estudiantes ni temporizadores visibles de presión. Justificación: efecto adverso de la competencia en ConectaIdeas (−0.22σ preferencia por trabajo en equipo, mayor en niñas; Araya et al. 2025) y riesgos por elemento del meta-análisis de Ratinho et al. 2026. | M | — |
| RF-G4 | Los puntos y niveles solo comparan al estudiante consigo mismo (progreso personal); los mensajes de logro se centran en esfuerzo y avance ("superaste tu marca"), no en desempeño relativo. | M | CU-6 |

### 3.6 Dashboard del apoderado (RF-DA)

| ID | Requerimiento | Prioridad | CU |
|---|---|---|---|
| RF-DA1 | El apoderado verá un **resumen general** del estudiante: ejercicios resueltos, tasa de aciertos, tiempo de uso y racha/frecuencia semanal, con agregación semanal por defecto. | M | CU-10 |
| RF-DA2 | El apoderado verá el **dominio por OA/unidad** como medidores de habilidad (skill meters) con la descripción del OA en lenguaje ciudadano (no solo el código "OA9"). | M | CU-10 |
| RF-DA3 | El dashboard destacará las **unidades y tipos de ejercicio con mayor dificultad** para el estudiante (mayor tasa de error o de uso de pistas), equivalente al indicador "preguntas más difíciles" del dashboard docente de ConectaIdeas, trasladado al apoderado. | M | CU-10 |
| RF-DA4 | El dashboard mostrará pocos indicadores de alto nivel (máx. ~5 vistas), con visualizaciones simples (barras, medidores, tendencia semanal) y texto explicativo, diseñado para un adulto de competencia digital básica (Schwendimann et al. 2017; Sugimaru & Glave 2021). | M | CU-10 |
| RF-DA5 | El dashboard incluirá **sugerencias accionables** en lenguaje simple (p. ej., "esta semana conviene practicar fracciones equivalentes"), generadas a partir del índice de dominio, no del LLM en tiempo real. | S | CU-10 |
| RF-DA6 | El dashboard presentará el progreso con encuadre de avance y apoyo, nunca de castigo o alarma (sin rojos punitivos ni comparaciones con "el promedio"), para no convertir el monitoreo en fuente de presión — la ansiedad matemática reduce el uso voluntario (Sugimaru & Glave 2021). | M | CU-10 |
| RF-DA7 | El apoderado no tendrá acceso al historial conversacional completo del estudiante con el tutor, solo a métricas agregadas e indicadores (decisión de diseño WHO/qué se muestra, marco SMILI de Bull & Kay). | S | CU-10 |

---

## 4. Requerimientos no funcionales (tarea 20)

### 4.1 Usabilidad (RNF-U)

| ID | Requerimiento | Métrica de verificación |
|---|---|---|
| RNF-U1 | La interfaz del estudiante será adecuada al rango 9–12 años: navegación de máx. 2 niveles de profundidad, botones grandes, iconografía + texto, lectura a nivel de 4° básico. | Evaluación heurística (heurísticas de Nielsen + heurísticas para niños) sin problemas de severidad ≥3 en el flujo principal. |
| RNF-U2 | La interfaz del apoderado será operable por un adulto de competencia digital básica sin capacitación. | SUS ≥ 70 con evaluadores adultos actuando como apoderados. |
| RNF-U3 | El flujo principal del estudiante (entrar → elegir unidad → resolver un ejercicio → ver retroalimentación) será completable sin ayuda de un adulto tras el primer uso. | Recorrido cognitivo (cognitive walkthrough) en evaluación heurística. |
| RNF-U4 | La aplicación será web responsiva, usable en computador y tablet; la vista del apoderado además será usable en pantalla de teléfono. | Prueba manual en 3 anchos de viewport (móvil/tablet/escritorio). |
| RNF-U5 | Todo el contenido de la interfaz estará en español de Chile. | Inspección. |

### 4.2 Corrección pedagógica y calidad del contenido (RNF-P)

| ID | Requerimiento | Métrica de verificación |
|---|---|---|
| RNF-P1 | Corrección matemática: las soluciones de referencia del banco validado tendrán ≥95% de corrección verificada contra el conjunto de ejercicios resueltos de referencia (gold standard) del objetivo general. | Comparación sistemática tutor vs. gold standard (validación TT1/TT2). |
| RNF-P2 | No revelación: en un set adversarial de solicitudes de respuesta directa ("dime la respuesta", reformulaciones), el tutor no revelará la solución en ≥95% de los casos. | Batería de prompts adversariales sobre el prototipo. |
| RNF-P3 | Alineación curricular: cada ejercicio del banco validado será clasificable sin ambigüedad en su OA declarado. | Revisión por pares/expertos de una muestra de ejercicios por OA. |
| RNF-P4 | La retroalimentación será evaluada con las dimensiones pedagógicas de Maurya et al. (identificación del error, localización, guía, accionabilidad, tono) por evaluadores humanos — no por LLM-juez, dada su baja confiabilidad documentada (BEA 2025). | Rúbrica aplicada por evaluadores humanos en la validación. |

### 4.3 Rendimiento y disponibilidad (RNF-R)

| ID | Requerimiento | Métrica de verificación |
|---|---|---|
| RNF-R1 | La retroalimentación a una respuesta llegará en ≤10 s (p90); mientras se genera, la interfaz mostrará un estado de espera amigable. La inmediatez del feedback es un elemento de gamificación con evidencia positiva (Ratinho 2026). | Medición instrumentada en pruebas del prototipo. |
| RNF-R2 | Los ejercicios se servirán preferentemente desde el banco persistido (pre-generación asíncrona), de modo que iniciar un ejercicio no dependa de la latencia de la API del LLM. | Diseño verificado + medición: apertura de ejercicio ≤2 s (p90). |
| RNF-R3 | Ante indisponibilidad de la API de OpenAI, el sistema degradará con gracia: ejercicios del banco con retroalimentación básica predefinida (correcto/incorrecto + solución de referencia por pasos), informando al usuario. | Prueba simulando caída de la API. |
| RNF-R4 | Ambiente de pruebas controlado (alcance del anteproyecto): se dimensiona para ~30 usuarios concurrentes de demostración, sin requisitos de alta disponibilidad. | Declarativo; prueba de humo de concurrencia. |

### 4.4 Seguridad y protección de datos (RNF-S)

| ID | Requerimiento | Métrica de verificación |
|---|---|---|
| RNF-S1 | Autenticación con contraseñas almacenadas con hash + salt (bcrypt o equivalente) y sesiones/JWT con expiración. | Revisión de código / inspección. |
| RNF-S2 | **Minimización de datos** (principio de la Ley 21.719): del estudiante solo se almacenan alias, curso y registros de desempeño; el titular de la cuenta y del consentimiento es el apoderado. | Inspección del modelo de datos. |
| RNF-S3 | Ningún dato personal o identificable se incluirá en los prompts enviados a la API de OpenAI; las llamadas al LLM solo contienen contenido matemático (OA, ejercicio, respuesta del estudiante anonimizada). | Revisión de los templates de prompt + log de llamadas en pruebas. |
| RNF-S4 | Durante TT1/TT2 el sistema operará únicamente con **datos sintéticos o de prueba** (sin menores reales), consistente con la limitación de no validar con menores; el diseño queda no obstante preparado para el estándar de la Ley 21.719 (vigencia dic. 2026). | Declarativo + inspección de datos de prueba. |
| RNF-S5 | Comunicación cliente-servidor exclusivamente sobre HTTPS; la API key de OpenAI reside solo en el servidor. | Inspección de configuración. |

### 4.5 Costo de operación (RNF-C)

| ID | Requerimiento | Métrica de verificación |
|---|---|---|
| RNF-C1 | El costo de API por estudiante activo se mantendrá bajo mediante: GPT-4o mini como modelo (elección del anteproyecto), reutilización del banco de ejercicios validados y prompts acotados. Presupuesto objetivo: definir en tarea 26 (stack) un tope mensual de referencia para la demo. | Registro de tokens/costo por sesión en pruebas. |
| RNF-C2 | El modelo de operación no requerirá personal adicional (coordinador/laboratorio): el apoderado sostiene el uso en el hogar. Contraste citable: 62% del costo de ConectaIdeas era personal (Araya et al. 2025). | Declarativo (argumento de diseño). |

### 4.6 Mantenibilidad y extensibilidad (RNF-M)

| ID | Requerimiento | Métrica de verificación |
|---|---|---|
| RNF-M1 | Los prompts del sistema (generación, evaluación, pistas, tono) se mantendrán como plantillas versionadas separadas del código, editables sin recompilar. | Inspección de estructura del repositorio. |
| RNF-M2 | El catálogo curricular (OA, unidades, anillos) se definirá como datos (tabla/JSON), de modo que agregar el Anillo 2 u otro curso no requiera cambios de código. | Inspección + prueba de agregar una unidad. |
| RNF-M3 | La integración con el LLM quedará aislada tras una interfaz propia (adaptador), permitiendo cambiar de proveedor/modelo sin afectar al resto del sistema. | Inspección de arquitectura (tarea 21). |
| RNF-M4 | Código y documentación seguirán lo comprometido en el anteproyecto: repositorio con código fuente, decisiones de diseño y manual de usuario. | Inspección de entregables. |

---

## 5. Impacto del cambio de alcance sobre el anteproyecto (a reconciliar en el informe final)

1. **§6.1 Alcances:** agregar el rol apoderado y su dashboard: "interfaz web orientada a los roles de estudiante y apoderado; el apoderado administra la cuenta y accede a un dashboard de progreso con métricas de desempeño e identificación de contenidos de mayor dificultad".
2. **§6.2 Limitaciones:** reescribir la exclusión de roles: quedan fuera **docente** y **administrador** (trabajo futuro); el apoderado deja de estar excluido.
3. **Ley 21.719:** el argumento original ("no se recolectan datos de menores") se mantiene para TT1/TT2 porque la validación sigue siendo sin menores y con datos sintéticos; pero el diseño ahora sí contempla cuentas y registros de desempeño de estudiantes para un despliegue futuro → se agrega el principio de minimización (RNF-S2/S3/S4) y se posiciona al apoderado como titular del consentimiento. Esto **fortalece** la sección en vez de contradecirla.
4. **Diagramas del anteproyecto (bocetos):** el diagrama de casos de uso requiere agregar el actor Apoderado (CU-9, CU-10) y los CU internos CU-11/CU-12; el diagrama de clases requiere las entidades `Apoderado` (o rol en `Usuario`), `DominioOA` (índice de dominio por OA) y la separación `Ejercicio.solucionReferencia` + `erroresComunes[]`; el diagrama de secuencia requiere una variante para "consultar dashboard". Se abordan en las tareas 21–24.

## 6. Trazabilidad requisitos ↔ evidencia

| Decisión | Requisitos | Fuente principal |
|---|---|---|
| Guardas del tutor (no revelar, pistas, solución de referencia en el prompt) | RF-P2–P4, RNF-P2 | Bastani et al.; Maurya et al. |
| Modelo del estudiante simple e interpretable por OA | RF-E2 | Bull & Kay 2016 (SMILI/Self); revisión KT×LLM (Cho et al. 2024) |
| Gamificación sin comparación social | RF-G3, RF-G4 | Araya et al. 2025 (−0.22σ); Ratinho et al. 2026 |
| Dashboard con pocos indicadores, skill meters, adulto de competencia básica | RF-DA2, RF-DA4 | Schwendimann 2017; Bull & Kay 2016; Sugimaru & Glave 2021 |
| Tono que reduce ansiedad; dashboard sin presión | RF-P5, RF-DA6 | Sugimaru & Glave 2021; Araya et al. 2025 (growth mindset) |
| Alcance curricular por OA basales + prerrequisitos | RF-D1, RF-D8 | Priorización Curricular 2023–2025; Bases Curriculares |
| Prompt con texto oficial del OA; refuerzo en fracciones | RF-D2, RF-D6 | EDUMATH; Priorización (COPISI) |
| Validación humana, no LLM-juez | RNF-P4 | Maurya et al.; BEA 2025 |
| Feedback inmediato como elemento motivacional | RNF-R1 | Ratinho et al. 2026 |
