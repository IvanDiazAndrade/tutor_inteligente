# Arquitectura General del Sistema (Fase II, tarea 21)

**Proyecto:** Tutor inteligente basado en IA para el aprendizaje de matemáticas — eje de Números, 4°–6° básico.
**Documento:** Diseño de arquitectura general, derivado de la especificación de requerimientos (`requisitos.md`, 33 RF + 20 RNF). Preliminar: los diagramas UML detallados corresponden a la Fase III (tareas 37–41); aquí se fijan la estructura, los componentes y las decisiones que esos diagramas deberán respetar.

---

## 1. De los requisitos a la arquitectura

La arquitectura no parte de una tecnología sino de cuatro restricciones que imponen los requisitos; todo lo demás se deriva de ellas:

1. **La solución de referencia no puede llegar al cliente** (RF-D3) y el tutor no puede revelarla ni bajo insistencia (RF-P3, RNF-P2) → toda la lógica pedagógica, la corrección y las llamadas al LLM deben vivir en el **servidor**; el cliente solo presenta. Esto obliga a un estilo **cliente-servidor** y descarta cualquier evaluación en el navegador.

2. **Abrir un ejercicio debe tomar ≤2 s y no depender de la API del LLM** (RNF-R2), pero generar un ejercicio con LLM toma varios segundos y debe verificarse antes de servirse (RNF-P1, RF-D6) → la generación tiene que estar **desacoplada del uso**: un proceso asíncrono llena un **banco persistido de ejercicios verificados**, y el flujo del estudiante solo lee de ese banco. Este banco es además el mecanismo que hace posible el gold standard del objetivo general.

3. **El sistema debe seguir operando si OpenAI cae** (RNF-R3), **sin enviar datos personales al proveedor** (RNF-S3), **con costo controlado** (RNF-C1) **y con prompts editables sin recompilar** (RNF-M1) y **proveedor sustituible** (RNF-M3) → todas las llamadas al LLM deben pasar por **un único punto de salida** (adaptador) que concentra plantillas, filtro de datos, reintentos, degradación y contabilidad de tokens.

4. **Dos usuarios con necesidades opuestas comparten los mismos datos**: un niño de 9–12 años que resuelve ejercicios (RNF-U1) y un adulto de competencia digital básica que consulta progreso (RNF-U2, RF-DA) → **una sola fuente de datos de desempeño** (los intentos y el índice de dominio) y **dos vistas por rol** sobre ella (RF-A2), en vez de dos aplicaciones.

Con esas cuatro restricciones, la forma general queda determinada:

```
┌─────────────────────────────┐
│   CLIENTE (navegador)       │      SPA web responsiva (RNF-U4)
│  ┌──────────┐ ┌──────────┐  │
│  │ Vista    │ │ Vista    │  │      dos vistas por rol (RF-A2)
│  │Estudiante│ │Apoderado │  │
│  └──────────┘ └──────────┘  │
└──────────────┬──────────────┘
               │ HTTPS / JSON (RNF-S5)
┌──────────────▼──────────────────────────────────────┐
│   SERVIDOR DE APLICACIÓN (API REST)                  │
│                                                      │
│  ┌────────────┐  ┌──────────────┐  ┌─────────────┐   │
│  │ Auth y     │  │ Orquestador  │  │ Servicio    │   │
│  │ roles (JWT)│  │ pedagógico   │  │ dashboard   │   │
│  └────────────┘  │  (tutor)     │  └─────────────┘   │
│  ┌────────────┐  └──────┬───────┘  ┌─────────────┐   │
│  │ Catálogo   │         │          │ Gamificación│   │
│  │ curricular │  ┌──────▼───────┐  └─────────────┘   │
│  └────────────┘  │ Motor        │  ┌─────────────┐   │
│  ┌────────────┐  │ adaptativo   │  │ Generador y │   │
│  │ Adaptador  │  │ (modelo del  │  │ banco de    │   │
│  │ LLM        │  │  estudiante) │  │ ejercicios  │   │
│  └─────┬──────┘  └──────────────┘  └─────────────┘   │
└────────┼─────────────────────────────────┬──────────┘
         │ HTTPS (solo contenido           │ SQL
         │ matemático, RNF-S3)             │
┌────────▼─────────┐            ┌──────────▼──────────┐
│  API OpenAI      │            │  Base de datos      │
│  GPT-4o mini     │            │  relacional         │
└──────────────────┘            └─────────────────────┘
```

Las tecnologías concretas (framework del frontend, lenguaje del backend, motor de base de datos, hosting) se justifican y fijan en la **tarea 26**; esta arquitectura solo exige: navegador como cliente (RNF-U4), API sobre HTTPS (RNF-S5) y base de datos con agregaciones eficientes para el dashboard (RF-DA1–DA3).

---

## 2. Mapeo a la arquitectura clásica de un ITS

El objetivo específico 3 del anteproyecto pide definir los módulos principales del ITS (estudiante, dominio, pedagógico, interfaz) y sus mecanismos de comunicación. Su ubicación en esta arquitectura:

| Módulo ITS | Componente(s) | Requisitos que lo definen | Diseño detallado |
|---|---|---|---|
| **Modelo del dominio** | Catálogo curricular + Generador y banco de ejercicios | RF-D1–D8 | tarea 23 |
| **Modelo del estudiante** | Motor adaptativo (índice de dominio por OA + historial de intentos) | RF-E1–E5 | tarea 22 |
| **Modelo pedagógico** | Orquestador pedagógico (plantillas, guardas, política de intentos) | RF-P1–P7 | tarea 24 |
| **Interfaz** | SPA con vista estudiante y vista apoderado (OLM con skill meters) | RF-A2, RF-E5, RF-G, RF-DA, RNF-U | tarea 25 |

El LLM **no es un módulo del ITS**: es un recurso de generación de lenguaje al servicio del modelo pedagógico y del dominio, siempre invocado a través del Adaptador y condicionado por las plantillas del orquestador. Esta separación es lo que distingue al sistema de "un chat con GPT", y es la traducción arquitectónica de las guardas de RF-P2–P4.

---

## 3. Componentes del servidor

| Componente | Responsabilidad | Requisitos |
|---|---|---|
| **Auth y roles** | Registro del apoderado (titular de la cuenta), login por rol con JWT y expiración, acceso del estudiante por perfil + PIN. | RF-A1–A5, RNF-S1 |
| **Catálogo curricular** | Unidades↔OA como datos (texto oficial del OA, curso, basal/complementario, anillo). Sin lógica: agregar Anillo 2 u otro curso es agregar filas. | RF-D1, RF-D8, RNF-M2 |
| **Generador y banco de ejercicios** | Dos fuentes de ejercicios hacia un banco común: **(a) generador paramétrico** (código propio): ejercicios de cálculo directo, comparación, ordenamiento y representaciones pictóricas (SVG) sorteando operandos dentro del rango numérico del OA — correctos por construcción, costo de API cero, errores comunes predefinidos por plantilla; **(b) generador LLM**: problemas verbales y de contexto, pre-generados de forma asíncrona (prompt con texto oficial del OA, RF-D2) y sometidos al pipeline de verificación de 4 capas (aritmética exacta → chequeos curriculares/forma → LLM de triaje → revisión humana). Todo ejercicio persiste enunciado + solución de referencia paso a paso + errores comunes (RF-D3) y sigue el ciclo de vida `borrador → verificado → activo / descartado` (RF-D5). | RF-D2–D7, RNF-P1, RNF-R2 |
| **Motor adaptativo** (modelo del estudiante) | Registra cada intento (RF-E1); actualiza el índice de dominio por OA (RF-E2); decide el nivel del siguiente ejercicio dentro de 3 niveles por unidad (RF-E3); diagnóstico inicial en frío (RF-E4). | RF-E1–E5 |
| **Orquestador pedagógico** (tutor) | Corrige **programáticamente** las respuestas (los formatos de RF-D7 lo permiten); arma los prompts de retroalimentación y pistas inyectando solución de referencia y errores comunes con guardas de no revelación y tono alentador (RF-P2–P6, RNF-P4); aplica la política de N intentos fallidos (RF-P7). Único componente que decide *qué* se le pide al LLM. | RF-P1–P7, RNF-P2 |
| **Gamificación** | Puntos ponderados por dificultad con descuento por pistas; niveles por unidad ligados al índice de dominio; **sin ningún estado social** (no existen tablas de ranking en el modelo de datos: RF-G3 se cumple por construcción). | RF-G1–G4 |
| **Servicio dashboard** | Agregaciones sobre intentos e índices de dominio: resumen semanal (RF-DA1), skill meters por OA con descripción ciudadana (RF-DA2), unidades más difíciles (RF-DA3), sugerencias por reglas (RF-DA5). **Nunca llama al LLM**: indicadores deterministas, auditables e inmediatos. | RF-DA1–DA7 |
| **Adaptador LLM** | Única puerta hacia OpenAI: interfaz propia (`generarEjercicio`, `generarRetroalimentacion`, `generarPista`); plantillas versionadas fuera del código (RNF-M1); filtro que garantiza que solo viaja contenido matemático (RNF-S3); reintentos, timeout y señal de degradación (RNF-R3); registro de tokens y costo por sesión (RNF-C1); proveedor sustituible (RNF-M3). | RNF-M1, M3, S3, C1, R3 |

---

## 4. Modelo de datos (entidades principales)

Derivado directamente de qué exigen registrar los requisitos:

| Entidad | Atributos clave | Requisito que la exige |
|---|---|---|
| `Usuario` (apoderado) | id, email, hash contraseña (bcrypt), rol | RF-A1, RNF-S1 |
| `Estudiante` | id, apoderadoId, alias, curso, PIN, puntajeTotal — **sin datos identificatorios** | RF-A1, A3, A5, RNF-S2 |
| `Unidad` | id, oaCodigo, oaTextoOficial, basal/complementario, anillo, curso, orden | RF-D1, RNF-M2 |
| `Ejercicio` | id, unidadId, nivelDificultad, enunciado, formatoRespuesta, respuestaFinal, solucionReferencia (pasos), erroresComunes[] {patrón, retroalimentación}, estado | RF-D3, D5, D7 |
| `Intento` | id, estudianteId, ejercicioId, respuesta, esCorrecta, pistasUsadas, tiempoSegundos, fecha | RF-E1 |
| `DominioOA` | estudianteId, oaCodigo, índice 0–1, nivelActual (1–3), rachaCorrectas, intentosEnUnidad, fechaUltimoIntento | RF-E2, E3 |
| `Sesion` | id, estudianteId, inicio, fin, puntajeObtenido | RF-DA1 (tiempo de uso) |

Notas de diseño: el "progreso" que ven estudiante y apoderado **se deriva por consulta** de `Intento` + `DominioOA` (una sola fuente de verdad, sin duplicación que pueda inconsistarse); el LLM no aparece en el modelo de datos — es infraestructura, no dominio.

---

## 5. Flujos principales

**F1 — Servir ejercicio:** estudiante elige unidad → el motor adaptativo consulta `DominioOA` y fija el nivel (RF-E3) → el banco entrega un ejercicio `activo` no visto de ese nivel → al cliente viaja solo enunciado y formato de respuesta. **Sin llamada al LLM** (RNF-R2: apertura ≤2 s).

**F2 — Evaluar respuesta:** el orquestador corrige programáticamente contra `respuestaFinal` → si es correcta: gamificación asigna puntaje y se muestra un refuerzo desde plantillas locales — **la ruta correcta no llama al LLM** (RF-P1, RNF-C1; decisión de la tarea 24); si es incorrecta: prompt con solución de referencia + errores comunes + respuesta del estudiante + guardas → el LLM genera retroalimentación guiada sin revelar la respuesta (RF-P2, RNF-P4) → el motor registra el `Intento` y actualiza `DominioOA`.

**F3 — Pedir pista:** el orquestador lleva el contador de pistas del intento y solicita la pista incremental mínima, condicionada a la solución de referencia (RF-P3); gamificación aplica el descuento (RF-G1).

**F4 — Dashboard del apoderado:** el servicio dashboard responde agregaciones (resumen semanal, skill meters, unidades difíciles, sugerencias por reglas) desde la base de datos; respuesta inmediata, sin LLM (RF-DA, AD-6).

**F5 — Reposición del banco (asíncrono):** un proceso periódico detecta unidad×nivel con stock bajo. Ejercicios numéricos puros → generador paramétrico (inmediato, sin revisión: correctos por construcción una vez aprobada la plantilla). Problemas verbales → lotes vía Adaptador LLM que pasan el pipeline de 4 capas: (1) verificación aritmética exacta con doble pasada en fracciones (RF-D6), (2) chequeos curriculares y de forma (rangos numéricos del OA, legibilidad, vocabulario), (3) LLM de triaje con rúbrica que aprueba o marca dudosos, (4) revisión humana como compuerta final a `activo` (RNF-P1, P3). La revisión humana queda así confinada a los problemas verbales, con el LLM de triaje usado solo como filtro previo — nunca como juez final, por su falta de confiabilidad documentada (Maurya; BEA 2025).

**F6 — Degradación:** si el Adaptador declara indisponible a OpenAI, F2 y F3 responden con plantillas locales (correcto/incorrecto + pasos de la solución de referencia como explicación estática) y aviso en la interfaz (RNF-R3). F1 y F4 no dependen del LLM por diseño, así que no se ven afectados.

---

## 6. Decisiones arquitectónicas (registro)

| # | Decisión | Alternativa descartada | Justificación |
|---|---|---|---|
| AD-1 | Toda la lógica pedagógica y la solución de referencia viven en el servidor. | Evaluación en el cliente. | RF-D3, RNF-P2; con la solución en el navegador bastaría inspeccionar el tráfico para obtener la respuesta (guardas de Bastani). |
| AD-2 | Corrección programática de respuestas; el LLM solo explica y guía. | LLM como corrector. | GPT sin apoyo comete errores aritméticos/lógicos (Bastani: 51% correcto); RF-D7 hace las respuestas validables sin LLM; menor costo (RNF-C1) y latencia (RNF-R1); el resultado correcto/incorrecto debe ser determinista porque alimenta el índice de dominio y el dashboard. |
| AD-3 | Pre-generación asíncrona + banco persistido con ciclo de vida. | Generación on-demand al pedir cada ejercicio. | RNF-R2, RNF-C1 (reutilización), RNF-P1 (verificar antes de servir); habilita el gold standard del objetivo general. |
| AD-4 | Adaptador LLM único con plantillas versionadas fuera del código. | Llamadas a OpenAI dispersas en los módulos. | RNF-M1/M3; punto único para filtro de PII (RNF-S3), contabilidad de costo (RNF-C1) y degradación (RNF-R3). |
| AD-5 | Modelo del estudiante: índice de dominio simple e interpretable por OA. | Knowledge tracing profundo (DKT/AKT). | Cold start sin datos de entrenamiento; el apoderado debe entender el indicador (RF-DA2, RNF-U2); Cho et al. 2024; Bull & Kay 2016. |
| AD-6 | Dashboard por agregación determinista, sin LLM en tiempo real. | Resúmenes generados por LLM al abrir el dashboard. | RF-DA5; indicadores auditables y reproducibles (Schwendimann); costo y latencia. |
| AD-7 | Base de datos relacional. | NoSQL/documental. | Entidades tabulares con relaciones claras; las agregaciones del dashboard (RF-DA1–DA3) son consultas SQL naturales; motor concreto en tarea 26. |
| AD-8 | Una SPA con dos vistas por rol y backend común. | Aplicaciones separadas estudiante/apoderado. | Una sola fuente de datos de desempeño (§1.4); alcance de prototipo (RNF-R4); JWT por rol ya separa las vistas (RF-A2). |
| AD-9 | Dos fuentes de ejercicios: generador paramétrico (código) para lo numérico/pictórico y LLM solo para problemas verbales. | Generar todo el banco con el LLM. | Misma filosofía de AD-2 aplicada a la generación: lo determinizable se determiniza. Reduce costo de API (RNF-C1), garantiza corrección por construcción en lo numérico (RNF-P1), acota la revisión humana a los problemas verbales y reduce la superficie de error del LLM (mitigación comprometida en las limitaciones del anteproyecto). El LLM queda donde aporta valor irreemplazable: lenguaje natural en enunciados contextualizados, retroalimentación y pistas. |

---

## 7. Relación con los diagramas del anteproyecto

Los bocetos de Fase I (casos de uso CU-1–CU-8, clases, secuencia, despliegue) fueron un ejercicio preliminar previo al levantamiento de requisitos. Esta arquitectura los reemplaza como referencia de diseño; al rehacerlos formalmente en Fase III (tareas 37–41) deben reflejar: el actor Apoderado (CU-9/CU-10) y los casos internos de pista y adaptación (CU-11/CU-12); las entidades `Intento` y `DominioOA`; la corrección programática (el LLM ya no "evalúa respuesta"); la generación de ejercicios fuera del flujo de servir ejercicio (F1/F5); y el LLM como componente de infraestructura tras el Adaptador, no como clase del dominio.

## 8. Puntos abiertos (se resuelven en tareas siguientes)

- ~~Algoritmo exacto del índice de dominio y umbrales de cambio de nivel~~ → **resuelto en `modelo_estudiante.md` (tarea 22)**: promedio móvil exponencial (α 0,3 / 0,5 en sondeo), umbrales 0,8/0,4 con racha de seguridad, sondeo integrado en frío, marca "para repasar" sin decaimiento.
- ~~Esquema JSON del ejercicio, catálogo de plantillas paramétricas por OA y políticas de equivalencia del corrector~~ → **resuelto en `modelo_dominio.md` (tarea 23)**; prompts de generación y triaje → **resuelto en `estrategia_llm.md` (tarea 27)**.
- ~~Plantillas pedagógicas (guardas, tono, pistas, política de intentos)~~ → **resuelto en `modelo_pedagogico.md` (tarea 24)**: interacción estructurada, 3 pistas pre-generadas por ejercicio, refuerzo local, explicación guiada ofrecida tras 3 fallos, andamiaje por banda, filtro de salida de no revelación. Parámetros de llamada, política de datos y prompts de generación/triaje → **resuelto en `estrategia_llm.md` (tarea 27)**.
- ~~Stack concreto y tope de costo mensual~~ → **resuelto en `stack_tecnologico.md` (tarea 26)**: React+TypeScript / Python+FastAPI / PostgreSQL / Render; tope de API US$5/mes con corte automático en el Adaptador.
- ~~Riesgos técnicos derivados~~ → **resuelto en `riesgos.md` (tarea 28)**: 15 riesgos evaluados; los críticos (capacidad del equipo, calidad de generación, corrector, umbrales de validación) con mitigación estructural ya incorporada al diseño.
