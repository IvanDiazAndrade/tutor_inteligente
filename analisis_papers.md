# Análisis en profundidad de los papers base

Proyecto: Tutor inteligente basado en IA para matemáticas, eje de Números, 4°–6° básico (Chile).
Fecha de análisis: 2026-07-12 (primer lote); actualizado en julio de 2026 con el segundo y tercer lote. Los PDF de respaldo se conservan en el archivo del equipo. Este fichaje registra, para cada fuente, el diseño del estudio, los resultados principales y su relación con las decisiones de diseño del proyecto (trazabilidad evidencia→requisito→diseño).

---

## 1. Vanzo, Pal Chowdhury & Sachan (2024/ACL 2025) — *GPT-4 as a Homework Tutor can Improve Student Engagement and Learning Outcomes* (ETH Zürich)

**Diseño del estudio.** RCT en un liceo técnico italiano: 4 cursos (75 estudiantes, 16–18 años), 8 semanas. El grupo de tratamiento reemplazó las tareas normales de inglés por sesiones interactivas con GPT-4 (`gpt-4-0125-preview`) en una web propia; el control hizo la tarea tradicional. Diseño de prompting en 2 pasos: el profesor entrega un **ejercicio semilla** (propósito + descripción + ejemplo) → GPT genera una **estrategia de tutoría** → ambas se insertan en un **prompt de tutoría** con reglas fijas ("una pregunta a la vez", "nunca des la respuesta", "no avances hasta respuesta correcta", "señala todos los errores").

**Resultados principales.**
- Ganancia global d=0.251 (p=0.314, n.s.); en 3° año (ejercicios objetivos) d=0.603 (p=0.087); en 5° (ensayos abiertos) nulo → el tutor LLM funciona mejor con **ejercicios de respuesta objetiva** (como los del eje de Números).
- Los estudiantes **de menor rendimiento inicial ganaron más** (correlación score inicial vs ganancia R=−0.777 en tratamiento).
- Engagement (palabras escritas) mucho mayor en tratamiento (d=1.421) y correlacionado con aprendizaje → el beneficio parece **mediado por el engagement**.
- **Alucinaciones <1%**: 14 errores en 1549 preguntas, sin insistir en el error. El problema más frecuente fue otro: **reveló la respuesta** en 365/1549 preguntas cuando los estudiantes insistían en obtenerla.
- 32/35 querían seguir usándolo; sin efecto novedad detectable (ratings estables 6 semanas).

**Relación con el proyecto.** Referencia directa para el diseño de prompts del módulo pedagógico; los cuestionarios (SESQ + ARCS, apéndice A) son adaptables para la evaluación; el riesgo principal a mitigar no es tanto la alucinación como la **revelación prematura de respuestas**.

---

## 2. Létourneau et al. (2025) — *A systematic review of AI-driven ITS in K-12 education* (npj Science of Learning)

**Diseño del estudio.** Revisión sistemática PRISMA: 26 artículos / 28 estudios (N=4597), 2009–2025, ERIC + Scopus. Clasifican por tipo de control: ITS vs profesor (8), vs sistema no inteligente (5), vs ITS modificado (11), sin control (4).

**Resultados principales.**
- ITS vs enseñanza tradicional: **7 de 8 estudios con efecto positivo medio-grande** (ej.: Cui et al. g=0.68; Ökördi: recuperación de brecha en multiplicación/división en 3°–4° básico con sesiones de 10–20 min).
- ITS vs sistema digital **no** inteligente: solo 1 de 4 muestra ventaja → lo que aporta valor es la **adaptividad bien implementada**, no lo digital per se (tesis de Honebein & Reigeluth: características correctas + condiciones correctas).
- Núcleo de un ITS efectivo: personalización/adaptividad, **retroalimentación inmediata**, descomposición en sub-pasos, apoyo a la autorregulación (skill diaries, self-assessment), progresión por dominio (mastery), e integración con el docente (blended, no reemplazo).
- Efectos mayores en enseñanza media-baja y en estudiantes de menor rendimiento (scaffolding).
- **Solo 14% de los estudios son de primaria** y **ninguno menciona consideraciones éticas** → dos vacíos que este trabajo aborda directamente.
- Matiza a Bloom (1984): VanLehn (2011) reporta ITS ≈ tutoría humana con d≈0.75–0.79, no 2σ.

**Relación con el proyecto.** Sustenta la arquitectura de 4 módulos y las decisiones de diseño (feedback inmediato, dificultad adaptativa, pasos intermedios); fundamenta la justificación del ITS, la identificación de la brecha en primaria, y la calibración del efecto esperado respecto de la formulación clásica del "2 sigma".

---

## 3. Shi, Yu, Dong & Chen (2026) — *LLMs in education: systematic review of empirical applications, benefits, and challenges* (Computers & Education: AI)

**Diseño del estudio.** Revisión PRISMA de **88 estudios empíricos** (nov 2022–mar 2025; Scopus, IEEE Xplore, ACM). Clasifican 6 aplicaciones: chatbots, generación de contenido, evaluación automática y feedback, task support, learning support, e **ITS (la categoría más prominente, n=22)**.

**Resultados principales.**
- Beneficios reportados: rendimiento académico (45 estudios), motivación/engagement (34), desarrollo cognitivo (26), optimización de recursos (16), accesibilidad (13). Ej.: evaluación automática con correlación r=0.92 con evaluadores humanos a ~$0.15/estudiante.
- Desafíos: **fiabilidad técnica y alucinación (28)**, sobre-dependencia (17), equidad en evaluación (8), privacidad (6; solo 27% de los papers la mencionan → vacío).
- Solo 23.9% de estudios en K-12; **Sudamérica: 1 solo estudio (Chile)** de 88 → vacío geográfico e idiomático.
- Marcos teóricos que usan los estudios: ZPD (Vygotsky), Carga Cognitiva (Sweller), aprendizaje autorregulado (Zimmerman), feedback (Hattie & Timperley) → insumo para el marco teórico del informe.
- Advertencias: los LLM deben **complementar, no reemplazar** al docente; el apoyo LLM puede reducir esfuerzo y ganancias si se usa como atajo; el modelado del estudiante multidimensional (tiempo, errores, engagement) es la tendencia.

**Relación con el proyecto.** Panorama general para la sección de estado del arte de LLM en educación; sus tablas A1/A2 permiten citar estudios específicos de matemáticas (Alvarez 2024 tutor LLM de cálculo; Zhu 2025 historias matemáticas con RAG; Norberg 2024 reescritura de problemas).

---

## 4. Maurya, Srivatsa, Petukhova & Kochmar (NAACL 2025) — *Unifying AI Tutor Evaluation: taxonomía de 8 dimensiones + MRBench* (MBZUAI)

**Diseño del estudio.** Proponen la primera taxonomía unificada, basada en principios de learning sciences, para evaluar respuestas de tutores IA ante **errores de estudiantes en matemáticas**: (1) identificación del error, (2) localización del error, (3) revelación de la respuesta (deseado: NO), (4) guía correcta y relevante, (5) accionabilidad, (6) coherencia, (7) tono (alentador), (8) naturalidad humana. Publican **MRBench**: 192 diálogos (Bridge = primaria; MathDial = media) × 7 LLMs + tutores humanos novato/experto = 1,596 respuestas anotadas (κ=0.71).

**Resultados principales.**
- **GPT-4 es buen sistema de pregunta-respuesta pero tutor deficiente: revela la respuesta ~47% de las veces.** Llama-3.1-405B fue el mejor tutor global; Llama-3.1-8B rinde razonable pese a su tamaño.
- Ningún LLM (ni los tutores humanos) cumple todas las dimensiones.
- **El LLM usado como juez no es confiable**: correlaciones con juicios humanos mayormente negativas (Prometheus2, Llama-3.1-8B) → la evaluación humana sigue siendo el estándar de referencia.

**Relación con el proyecto.** La taxonomía se adopta como rúbrica para la validación de "corrección pedagógica": además de comparar la respuesta final contra los ejercicios resueltos de referencia, evaluar cada respuesta del tutor en las 8 dimensiones (o un subconjunto: identificación, no-revelación, guía, accionabilidad). El prompt del sistema debe instruir explícitamente contra revelar la respuesta. Fundamenta además la decisión de que la validación sea humana y no automatizada con otro LLM.

---

## 5. Kochmar et al. (BEA 2025) — *Findings of the BEA 2025 Shared Task on Pedagogical Ability Assessment of AI-powered Tutors*

**Diseño del estudio.** Competencia internacional (50+ equipos, incl. equipos chilenos: IALab UC) sobre MRBench ampliado: predecir automáticamente 4 dimensiones pedagógicas (identificación de error, localización, guía, accionabilidad) + identificar qué tutor generó la respuesta.

**Resultados principales.**
- Mejores macro F1 exactos: identificación 0.718, localización 0.598, **guía 0.583 (la más difícil)**, accionabilidad 0.709 → incluso con fine-tuning y GPT-4o/Gemini-2.5-pro, **evaluar automáticamente la calidad pedagógica sigue siendo difícil**.
- Técnicas dominantes: LoRA fine-tuning, prompting avanzado, aumento de datos, ensembles.
- Los tutores LLM tienen "estilos" identificables (F1 0.97 para identificar el modelo autor).

**Relación con el proyecto.** Confirma que la validación pedagógica no puede delegarse a un LLM evaluador; se usa como evidencia metodológica de la elección de comparación con el conjunto de referencia + evaluación heurística humana. Complementario del anterior (mismo grupo de autores y datos).

---

## 6. Christ et al. (2026) — *EDUMATH: Generating Standards-aligned Educational Math Word Problems* (U. Virginia)

**Diseño del estudio.** Estudian generación de problemas matemáticos de enunciado (MWP) **alineados a estándares curriculares para grados 3–5**. Evalúan >11,000 problemas generados con jueces expertos humanos + LLM sobre 4 criterios: **resolubilidad, exactitud (solución CoT correcta y legible), pertinencia educativa y alineación al estándar**. Crean el dataset STEM (2,577 MWP anotados por docentes) y entrenan modelos abiertos (EDUMATH 12B/30B).

**Resultados principales.**
- Los modelos cerrados grandes rinden bien: GPT-4o/4.1 ≈ **92.8% de problemas que cumplen todos los criterios** con prompting 8-shot; los abiertos pequeños fallan mucho más (Gemma 12B: 63.9%).
- Por tema: **fracciones es de los temas con más errores** en casi todos los modelos (GPT-4o: 88.9% vs 100% en patrones/conversión) — el tema de mayor énfasis en este proyecto.
- Con estudiantes reales (3°–5° grado, n=94): rinden igual en problemas LLM vs humanos y **prefieren los problemas LLM personalizados a sus intereses**.

**Relación con el proyecto.** Modelo de referencia del módulo de generación de ejercicios: (a) prompt con el **texto completo del objetivo de aprendizaje** (OA de las Bases Curriculares/Priorización, no solo el tema), (b) few-shot con ejemplos de formato validado, (c) filtro de validación con los 4 criterios (adaptados al conjunto de referencia propio), (d) atención especial a fracciones. Sugiere además personalizar contextos según intereses del estudiante como mejora de engagement de bajo costo.

---

## 7. De Simone et al. (2025, actualizado dic 2025) — *From Chalkboards to Chatbots* (Banco Mundial, Policy Research WP 11125)

**Diseño del estudio.** RCT en Benin City, Nigeria: 657 tratados / 671 control (muestra final 422/337), 9 escuelas públicas, 6 semanas, 12 sesiones de 90 min after-school. Estudiantes en pares usando **Microsoft Copilot (GPT-4)** como tutor de inglés, con **docentes como guías** (no instruyen: monitorean y encauzan), prompts iniciales curados y alineados al currículum nigeriano, diseñados con principios de la ciencia del aprendizaje (dificultades deseables, práctica de recuperación, interrogación elaborativa; estructuras de Mollick & Mollick).

**Resultados principales.**
- ITT: **+0.31σ** en la evaluación total (IRT 0.26σ); inglés +0.24σ; y **+0.21σ en el examen curricular regular del tercer trimestre** → transferencia más allá del contenido de las sesiones.
- **Dosis-respuesta lineal: +0.031σ por día adicional de asistencia, sin meseta** → proyección de 1.2–2.2σ para un año completo.
- Heterogeneidad: efectos positivos en toda la distribución, pero mayores en mujeres, en estudiantes con mejor rendimiento previo y de mayor NSE (la alfabetización digital modera el beneficio → riesgo de equidad).
- Costo-efectividad: $48/alumno piloto ($9 marginal), 3.2 EYOS por $100, sobre el percentil 80 de las RCT educativas en países en desarrollo.
- Interpretación de los autores: los LLM **mejoran** el aprendizaje usados como tutores con barandas (prompts pedagógicos + supervisión docente + alineación curricular) y lo **dañan** usados como atajo (citan Bastani et al. 2024, *Generative AI Can Harm Learning*).

**Relación con el proyecto.** La evidencia causal más fuerte a favor de la premisa central del proyecto. Los "tres mecanismos" (prompts pedagógicos, supervisión, alineación curricular) se corresponden con el módulo pedagógico, la mediación del apoderado y el dominio cerrado al eje de Números. Aporta también una limitación a declarar: la brecha digital como riesgo de inequidad.

---

# Síntesis transversal

## Convergencia de la literatura (2024–2026)
1. **El LLM sin salvaguardas no es un tutor.** GPT-4 revela la respuesta ~47% de las veces (Maurya) y el acceso sin barandas puede dañar el aprendizaje (Bastani). Lo que funciona es LLM + prompt pedagógico estricto + dominio curricular cerrado + supervisión (De Simone, Vanzo).
2. **La adaptividad es el ingrediente activo**, no la digitalización (Létourneau: ITS supera al profesor tradicional en 7/8 estudios, pero solo en 1/4 frente a software no-inteligente).
3. **Los estudiantes de menor rendimiento ganan más** con tutoría escalonada (Vanzo, Létourneau) → conexión directa con el problema Simce/PISA.
4. **La evaluación pedagógica automática todavía no es confiable** (Maurya: correlaciones negativas de LLM-juez; BEA 2025: F1≈0.58 en "guía") → la validación debe ser humana + conjunto de referencia.
5. **Generar ejercicios alineados al currículum con LLM es viable** con modelos clase GPT-4o (≈93% cumplen todos los criterios), pero **fracciones concentra las fallas** → foco de la validación.

## Aplicación al diseño
- **Prompt del tutor** (módulo pedagógico): codificar las reglas de Vanzo + dimensiones de Maurya — identificar el error y su ubicación, guiar sin revelar la respuesta, un paso accionable a la vez, tono alentador, no avanzar hasta respuesta correcta.
- **Rúbrica de validación**: adoptar (adaptada) la taxonomía de 8 dimensiones de Maurya et al. para la evaluación de "corrección pedagógica", complementando la comparación de respuestas finales contra los ejercicios de referencia; BEA 2025 fundamenta la evaluación humana.
- **Generación de ejercicios**: prompts con el texto completo del OA curricular + few-shot; filtro con los 4 criterios de EDUMATH (resoluble, exacto, apropiado, alineado); sobre-representar fracciones en el conjunto de referencia.
- **Vacío de investigación que el proyecto aborda**: (a) solo 14% de estudios ITS en primaria (Létourneau), (b) 1 de 88 estudios empíricos LLM en Sudamérica (Shi), (c) escasa atención a ética/privacidad (ambas revisiones) — un tutor en español, para primaria, en matemáticas y con consideraciones de la Ley 21.719 cubre los tres.
- **Cuestionarios**: los instrumentos SESQ/ARCS de Vanzo (apéndice) son adaptables para la evaluación junto al SUS ya planificado.
- **Magnitud del efecto esperado**: Bloom (1984) como motivación histórica, calibrado con VanLehn (d≈0.76–0.79) y los meta-análisis modernos (d≈0.3–0.4).
- **Limitaciones a declarar**: revelación prematura de respuestas (más frecuente que la alucinación), sobre-dependencia, brecha de alfabetización digital (De Simone), y que el feedback LLM puede ser incorrecto en una fracción relevante de los hints abiertos (Danyaro et al., ya citado en el anteproyecto).

---

# Segundo lote (8 papers, julio 2026): resúmenes individuales en fichas `-T.md`

Análisis en profundidad de cada uno en su ficha respectiva. Lo que agregan:

1. **Bastani et al. (RCT Turquía)** — la evidencia causal del "doble filo": GPT Base −17% en examen sin ayuda vs GPT Tutor ≈0; GPT-4 solo 51% correcto sin apoyo; receta de barandas replicable (nunca revelar solución + pistas incrementales + **solución de referencia docente dentro del prompt** + errores comunes anticipados). El conjunto de referencia del proyecto puede usarse también *en producción* dentro del prompt, no solo para validar.
2. **Cho et al. (KT+LLM, revisión)** — mapa del modelado del estudiante (BKT→DKT→atención→LLM-KT). Conclusión aplicada: un modelo simple e interpretable (maestría por OA) está respaldado; el LLM es útil para el cold-start (diagnóstico inicial); la interpretabilidad que la revisión demanda es la que el panel del apoderado necesita.
3. **Ratinho et al. (meta-análisis gamificación en matemáticas)** — g=0.383 sobre motivación; puntos/niveles/feedback inmediato y progreso personal = perfil favorable; leaderboards/timers/recompensas externas = riesgo (SDT). Cubre secundaria/superior: se cita declarando esa limitación.
4. **Schwendimann et al. (learning dashboards, revisión)** — definición canónica + taxonomía de 6 tipos de indicadores para derivar los del panel; brecha documentada: ningún dashboard para apoderados en la literatura revisada; advertencia: granularidad según alfabetización de datos del usuario.
5. **Bull & Kay (SMILI☺)** — marco formal para diseñar el panel como Open Learner Model (preguntas por qué/qué/cómo/quién); skill meters = visualización con mejor evidencia; Self (1990): un arreglo de puntajes de maestría basta como modelo del estudiante; precedente de OLM para padres.
6. **Araya et al. (ConectaIdeas RCT, Chile)** — +0.27σ Simce 4° básico: la evidencia local central. El proyecto aborda sus tres carencias declaradas: feedback sin explicación, sin adaptividad, y costo de coordinador/laboratorio. Su efecto negativo (−0.22σ en preferencia por trabajo en equipo, mayor en niñas) refuerza la gamificación sin comparación social.
7. **Sugimaru & Glave (ConectaIdeas hogar, GRADE Perú)** — el escenario más cercano al del proyecto (plataforma gamificada usada desde casa, 4° de primaria): el disfrute — no la utilidad percibida — predice el uso a los ~10 años; la alfabetización digital del cuidador predice el uso del niño → diseñar para un apoderado de competencia digital básica; la ansiedad matemática reduce el uso voluntario → el tono del tutor debe reducirla.
8. **Priorización Curricular 2023-2025 (MINEDUC)** — jerarquización oficial basal/complementario que define el alcance en dos anillos (ver `curriculo_4a6_matematica.md`); COPISI respalda las representaciones pictóricas; la habilidad "g" ("identificar un error, explicar su causa y corregirlo") describe directamente la función del módulo pedagógico.

## Qué cierra este lote respecto del primero

- **Panel del apoderado**: fundamento completo — marco de diseño (SMILI☺), indicadores y visualizaciones (Schwendimann), precedente local del dashboard docente (ConectaIdeas) y evidencia de adopción en el hogar mediada por el adulto (GRADE). La brecha "dashboard para apoderados de primaria" no está cubierta en la literatura revisada.
- **Gamificación**: efecto causal en el tramo etario y país del proyecto (ConectaIdeas +0.27σ) + mecanismo y guía de diseño (Ratinho g=0.383, SDT) + motor de adopción a los 10 años (GRADE: disfrute).
- **Modelo del estudiante**: maestría por OA simple e interpretable (Self vía SMILI☺; Cho et al. para el vocabulario BKT/DKT y el cold-start con LLM).
- **Alcance curricular**: definido con fuente oficial (Priorización) y operacionalizado en `curriculo_4a6_matematica.md`.

---

# Tercer lote (4 papers, julio 2026): didáctica de la matemática

Incorporados para fundamentar el enfoque didáctico COPISI que orienta el diseño. Sustentan la sección 2.12 del informe de TT1.

1. **Leong, Ho & Cheng (2015) — *Concrete-Pictorial-Abstract: Surveying its origins and charting its future* (The Mathematics Educator 16(1), NIE Singapur)** — La genealogía documentada de CPA/COPISI: adoptado por el Ministerio de Educación de Singapur desde ~1980 (Primary Mathematics Project de Kho Tek Hong, confirmado por comunicación personal), construido directamente sobre los modos enactivo-icónico-simbólico de Bruner (1966). Puntos clave: (a) los modos no son etapas cronológicas separadas — lo simbólico se desarrolla gradualmente junto a los otros; (b) la meta es la fluidez simbólica; (c) lo pictórico queda como representación de respaldo ("fall back") cuando falla la manipulación simbólica (Bruner p. 49); (d) la secuencia concreto-a-abstracto es especialmente efectiva con estudiantes de bajo rendimiento, con evidencia en fracciones (Butler et al. 2003); (e) qué es "concreto/pictórico/abstracto" no es universal — se calibra al estudiante.
2. **Espinoza, Matus, Barbe, Fuentes & Márquez (2016) — *Qué y cuánto aprenden de matemáticas los estudiantes de básica con el Método Singapur* (Calidad en la Educación 45, Centro Félix Klein USACH)** — Evidencia chilena de didáctica en el nivel escolar del proyecto: postest a 4° básico (459 tratamiento / 221 comparación), logro 77,68% vs 72,92% (+4,76 pp, T-test significativo al 95%); por habilidad: resolver problemas +3,58 y manipular expresiones +6,72 (significativas), representar n.s. Brecha de género significativamente menor con el método (3,82 vs 5,44 pp general; 4,82 vs 7,22 en resolución de problemas). Cita clave (p. 113): el principio del método Singapur "es claramente descrito en las bases curriculares y de manera más sintetizada en el principio metodológico llamado COPISI (concreto-pictórico-simbólico)" — el vínculo textual COPISI↔Bases Curriculares↔método Singapur. Además: los materiales concretos disminuyen de 5° básico en adelante, priorizando lo pictórico-simbólico (respalda que un tutor web cubra esos dos registros).
3. **Fyfe, McNeil, Son & Goldstone (2014) — *Concreteness fading in mathematics and science instruction: A systematic review* (Educational Psychology Review 26(1))** — El respaldo cognitivo-experimental de la secuencia: funciona si son 3 etapas, vinculadas explícitamente (como referentes mutuos) y en ese orden (enactivo→icónico→simbólico); beneficios: interpretar símbolos ambiguos a partir de lo concreto, anclaje perceptual, reserva de imágenes de respaldo, y despojo de detalles superficiales que facilita la transferencia. Evidencia directamente pertinente: Koedinger & Anderson (1998) — tutor cognitivo de álgebra con mejores aprendizajes presentando lo concreto primero, una etapa intermedia y luego el símbolo (el principio opera dentro de un ITS); McNeil & Fyfe (2012) — mejor transferencia con fading que con solo-concreto o solo-abstracto a 1 y 3 semanas.
4. **Van den Heuvel-Panhuizen & Drijvers (2014) — *Realistic Mathematics Education* (Encyclopedia of Mathematics Education, Springer)** — Síntesis de la RME (Freudenthal): "realista" = imaginable por el estudiante (zich realiseren), no necesariamente del mundo real; 6 principios (actividad, realidad, niveles, entrelazamiento, interactividad, guía); principio de niveles: los modelos puente pasan de "modelo de" una situación a "modelo para" situaciones equivalentes. Aplicación: fundamenta los problemas verbales contextualizados que genera el LLM (principio de realidad) y la progresión informal→formal; la "guided re-invention" describe la explicación guiada del tutor.

**Libros citados sin ficha:** Bruner (1966) *Toward a theory of instruction* (raíz teórica, revisado vía Leong et al.) y Pólya (1965) *Cómo plantear y resolver problemas* (heurísticas comprender/planear/ejecutar/examinar, base de las 3 pistas graduadas).

**Qué cierra este lote:** el análisis de los enfoques pedagógicos (objetivo específico 2) queda sustentado con: el enfoque oficial del currículum (COPISI) + su genealogía teórica (Bruner→CPA) + evidencia chilena del mismo nivel escolar (+4,76 pp, reducción de la brecha de género) + las condiciones cognitivas de efectividad de la secuencia (concreteness fading, incluida su operación dentro de un ITS) + los complementos RME (contextos) y Pólya (pistas). Cada pieza está mapeada a una decisión de diseño en la sección 2.12 del informe.
