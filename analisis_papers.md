# Análisis en profundidad de los papers base

Proyecto: Tutor inteligente basado en IA para matemáticas, eje de Números, 4°–6° básico (Chile).
Fecha de análisis: 2026-07-12. Los 7 PDFs están en `papers/`.

---

## 1. Vanzo, Pal Chowdhury & Sachan (2024/ACL 2025) — *GPT-4 as a Homework Tutor can Improve Student Engagement and Learning Outcomes* (ETH Zürich)

**Qué hicieron.** RCT en un liceo técnico italiano: 4 cursos (75 estudiantes, 16–18 años), 8 semanas. El grupo tratamiento reemplazó las tareas normales de inglés por sesiones interactivas con GPT-4 (`gpt-4-0125-preview`) en una web propia; el control hizo la tarea tradicional. Diseño de prompting en 2 pasos: el profesor entrega un **ejercicio semilla** (propósito + descripción + ejemplo) → GPT genera una **estrategia de tutoría** → ambas se insertan en un **prompt de tutoría** con reglas fijas ("una pregunta a la vez", "nunca des la respuesta", "no avances hasta respuesta correcta", "señala todos los errores").

**Resultados clave.**
- Ganancia global d=0.251 (p=0.314, n.s.); en 3° año (ejercicios objetivos) d=0.603 (p=0.087); en 5° (ensayos abiertos) nulo → el tutor LLM funciona mejor con **ejercicios de respuesta objetiva** (como los del eje de Números).
- Los estudiantes **más débiles ganaron más** (correlación score inicial vs ganancia R=−0.777 en tratamiento).
- Engagement (palabras escritas) mucho mayor en tratamiento (d=1.421) y correlacionado con aprendizaje → el beneficio parece **mediado por el engagement**.
- **Alucinaciones <1%**: 14 errores en 1549 preguntas, nunca insistió en el error. Problema real: **reveló la respuesta** en 365/1549 preguntas cuando los estudiantes intentaban "sacársela".
- 32/35 querían seguir usándolo; sin efecto novedad detectable (ratings estables 6 semanas).

**Para nuestro proyecto.** Plantilla directa para el diseño de prompts del módulo pedagógico; los cuestionarios (SESQ + ARCS, apéndice A) son reutilizables para la evaluación heurística; el riesgo principal a mitigar no es tanto la alucinación sino la **revelación prematura de respuestas**.

---

## 2. Létourneau et al. (2025) — *A systematic review of AI-driven ITS in K-12 education* (npj Science of Learning)

**Qué hicieron.** Revisión sistemática PRISMA: 26 artículos / 28 estudios (N=4597), 2009–2025, ERIC + Scopus. Clasifican por tipo de control: ITS vs profesor (8), vs sistema no inteligente (5), vs ITS modificado (11), sin control (4).

**Resultados clave.**
- ITS vs enseñanza tradicional: **7 de 8 estudios con efecto positivo medio-grande** (ej.: Cui et al. g=0.68; Ökördi: recuperación de brecha en multiplicación/división en 3°–4° básico con sesiones de 10–20 min).
- ITS vs sistema digital **no** inteligente: solo 1 de 4 muestra ventaja → lo que aporta valor es la **adaptividad bien implementada**, no lo digital per se (tesis de Honebein & Reigeluth: características correctas + condiciones correctas).
- Núcleo de un ITS efectivo: personalización/adaptividad, **retroalimentación inmediata**, descomposición en sub-pasos, apoyo a la autorregulación (skill diaries, self-assessment), progresión por dominio (mastery), e integración con el docente (blended, no reemplazo).
- Efectos mayores en enseñanza media-baja y en estudiantes de menor rendimiento (scaffolding).
- **Solo 14% de los estudios son de primaria** y **ninguno menciona consideraciones éticas** → dos vacíos que nuestro trabajo puede reclamar explícitamente.
- Matiza a Bloom (1984): VanLehn (2011) reporta ITS ≈ tutoría humana con d≈0.75–0.79, no 2σ.

**Para nuestro proyecto.** Sustenta la arquitectura de 4 módulos y las decisiones de diseño (feedback inmediato, dificultad adaptativa, pasos intermedios). Citar para: justificación del ITS, brecha en primaria, y para NO sobrevender el "2 sigma".

---

## 3. Shi, Yu, Dong & Chen (2026) — *LLMs in education: systematic review of empirical applications, benefits, and challenges* (Computers & Education: AI)

**Qué hicieron.** Revisión PRISMA de **88 estudios empíricos** (nov 2022–mar 2025; Scopus, IEEE Xplore, ACM). Clasifican 6 aplicaciones: chatbots, generación de contenido, evaluación automática y feedback, task support, learning support, e **ITS (la categoría más prominente, n=22)**.

**Resultados clave.**
- Beneficios reportados: rendimiento académico (45 estudios), motivación/engagement (34), desarrollo cognitivo (26), optimización de recursos (16), accesibilidad (13). Ej.: evaluación automática con correlación r=0.92 con evaluadores humanos a ~$0.15/estudiante.
- Desafíos: **fiabilidad técnica y alucinación (28)**, sobre-dependencia (17), equidad en evaluación (8), privacidad (6; solo 27% de los papers la mencionan → vacío).
- Solo 23.9% de estudios en K-12; **Sudamérica: 1 solo estudio (Chile)** de 88 → vacío geográfico/idiomático enorme.
- Marco teórico que usan los estudios: ZPD (Vygotsky), Carga Cognitiva (Sweller), aprendizaje autorregulado (Zimmerman), feedback (Hattie & Timperley) → lista lista para nuestro Capítulo III.
- Advertencias: los LLM deben **complementar, no reemplazar** al docente; el apoyo LLM puede reducir esfuerzo y ganancias si se usa como atajo; modelado del estudiante multidimensional (tiempo, errores, engagement) es la tendencia.

**Para nuestro proyecto.** Es el "mapa maestro" para la sección de estado del arte de LLMs en educación; la Tabla A1/A2 permite citar estudios específicos de matemáticas (Alvarez 2024 tutor LLM de cálculo; Zhu 2025 historias matemáticas con RAG; Norberg 2024 reescritura de problemas).

---

## 4. Maurya, Srivatsa, Petukhova & Kochmar (NAACL 2025) — *Unifying AI Tutor Evaluation: taxonomía de 8 dimensiones + MRBench* (MBZUAI)

**Qué hicieron.** Proponen la primera taxonomía unificada, basada en principios de learning sciences, para evaluar respuestas de tutores IA ante **errores de estudiantes en matemáticas**: (1) identificación del error, (2) localización del error, (3) revelación de la respuesta (deseado: NO), (4) guía correcta y relevante, (5) accionabilidad, (6) coherencia, (7) tono (alentador), (8) naturalidad humana. Publican **MRBench**: 192 diálogos (Bridge = primaria; MathDial = media) × 7 LLMs + tutores humanos novato/experto = 1,596 respuestas anotadas (κ=0.71).

**Resultados clave.**
- **GPT-4 es buen sistema de pregunta-respuesta pero tutor mediocre: revela la respuesta ~47% de las veces.** Llama-3.1-405B fue el mejor tutor global; Llama-3.1-8B rinde razonable pese a su tamaño.
- Ningún LLM (ni los tutores humanos) cumple todas las dimensiones; enorme margen de mejora.
- **LLM-como-juez no es confiable**: correlaciones con juicios humanos mayormente negativas (Prometheus2, Llama-3.1-8B) → la evaluación humana sigue siendo el gold standard.

**Para nuestro proyecto.** La taxonomía es **directamente adoptable como rúbrica** para nuestra validación de "corrección pedagógica": en vez de solo comparar respuesta final vs ejercicios resueltos de referencia, evaluar cada respuesta del tutor en las 8 dimensiones (o un subconjunto: identificación, no-revelación, guía, accionabilidad). El prompt del sistema debe instruir explícitamente contra revelar la respuesta. Además valida nuestro plan de evaluación humana (no automatizada con otro LLM).

---

## 5. Kochmar et al. (BEA 2025) — *Findings of the BEA 2025 Shared Task on Pedagogical Ability Assessment of AI-powered Tutors*

**Qué hicieron.** Competencia internacional (50+ equipos, incl. equipos chilenos: IALab UC) sobre MRBench ampliado: predecir automáticamente 4 dimensiones pedagógicas (identificación de error, localización, guía, accionabilidad) + identificar qué tutor generó la respuesta.

**Resultados clave.**
- Mejores macro F1 exactos: identificación 0.718, localización 0.598, **guía 0.583 (la más difícil)**, accionabilidad 0.709 → incluso con fine-tuning y GPT-4o/Gemini-2.5-pro, **evaluar automáticamente la calidad pedagógica sigue siendo difícil**.
- Técnicas dominantes: LoRA fine-tuning, prompting avanzado, aumento de datos, ensembles.
- Los tutores LLM tienen "estilos" identificables (F1 0.97 para identificar el modelo autor).

**Para nuestro proyecto.** Refuerza que no podemos delegar la validación pedagógica a un LLM evaluador; sirve como evidencia en la metodología de por qué elegimos comparación con gold standard + evaluación heurística humana. Es el paper "hermano" del anterior (mismos autores/datos).

---

## 6. Christ et al. (2026) — *EDUMATH: Generating Standards-aligned Educational Math Word Problems* (U. Virginia)

**Qué hicieron.** Estudian generación de problemas matemáticos de enunciado (MWP) **alineados a estándares curriculares para grados 3–5** (≈ nuestro 4°–6° básico). Evalúan >11,000 problemas generados con jueces expertos humanos + LLM sobre 4 criterios: **resolubilidad, exactitud (solución CoT correcta y legible), pertinencia educativa y alineación al estándar**. Crean el dataset STEM (2,577 MWP anotados por docentes) y entrenan modelos abiertos (EDUMATH 12B/30B).

**Resultados clave.**
- Los modelos cerrados grandes ya lo hacen bien: GPT-4o/4.1 ≈ **92.8% de problemas que cumplen todos los criterios** con prompting 8-shot; los abiertos pequeños fallan mucho más (Gemma 12B: 63.9%).
- Por tema: **fracciones es de los temas con más errores** en casi todos los modelos (GPT-4o: 88.9% vs 100% en patrones/conversión) — y fracciones es justo nuestro énfasis.
- Con estudiantes reales (3°–5° grado, n=94): rinden igual en problemas LLM vs humanos y **prefieren los problemas LLM personalizados a sus intereses**.

**Para nuestro proyecto.** Blueprint del módulo de generación de ejercicios: (a) prompt con el **lenguaje completo del objetivo de aprendizaje** (OA de las Bases Curriculares/priorización, no solo el tema), (b) few-shot con ejemplos de formato validado, (c) filtro de validación con los 4 criterios (adaptables a nuestro gold standard), (d) atención especial a fracciones. También sugiere personalizar contextos según intereses del estudiante como mejora de engagement barata.

---

## 7. De Simone et al. (2025, actualizado dic 2025) — *From Chalkboards to Chatbots* (Banco Mundial, Policy Research WP 11125)

**Qué hicieron.** RCT en Benin City, Nigeria: 657 tratados / 671 control (muestra final 422/337), 9 escuelas públicas, 6 semanas, 12 sesiones de 90 min after-school. Estudiantes en pares usando **Microsoft Copilot (GPT-4)** como tutor de inglés, con **docentes como guías** (no instruyen: monitorean y encauzan), prompts iniciales curados y alineados al currículum nigeriano, diseñados con principios de la ciencia del aprendizaje (dificultades deseables, práctica de recuperación, interrogación elaborativa; estructuras de Mollick & Mollick).

**Resultados clave.**
- ITT: **+0.31σ** en la evaluación total (IRT 0.26σ); inglés +0.24σ; y **+0.21σ en el examen curricular regular del tercer trimestre** → transferencia más allá del contenido de las sesiones.
- **Dosis-respuesta lineal: +0.031σ por día adicional de asistencia, sin meseta** → proyección de 1.2–2.2σ para un año completo.
- Heterogeneidad: efectos positivos en toda la distribución, pero mayores en mujeres, en estudiantes con mejor rendimiento previo y de mayor NSE (la alfabetización digital modera el beneficio → riesgo de equidad).
- Costo-efectividad sobresaliente: $48/alumno piloto ($9 marginal), 3.2 EYOS por $100, sobre el percentil 80 de las RCT educativas en países en desarrollo.
- Interpretación clave de los autores: los LLM **mejoran** el aprendizaje usados como tutores con barandas (prompts pedagógicos + supervisión docente + alineación curricular) y lo **dañan** usados como atajo/muleta (citan Bastani et al. 2024, *Generative AI Can Harm Learning*).

**Para nuestro proyecto.** Es la evidencia causal más fuerte a favor de la tesis central del proyecto. Los "tres mecanismos" (prompts pedagógicos, supervisión, alineación curricular) mapean 1:1 con nuestro módulo pedagógico, la advertencia de supervisión adulta, y el dominio cerrado al eje de Números. Citar también para limitaciones: brecha digital como riesgo de inequidad.

---

# Síntesis transversal: qué cambia en nuestro proyecto

## Convergencia de la literatura (2024–2026)
1. **El LLM crudo no es un tutor.** GPT-4 revela la respuesta ~47% de las veces (Maurya) y el acceso sin barandas puede dañar el aprendizaje (Bastani, citado en Nigeria). Lo que funciona es LLM + prompt pedagógico estricto + dominio curricular cerrado + supervisión (Nigeria, Vanzo).
2. **La adaptividad es el ingrediente activo**, no la digitalización (Létourneau: ITS gana a profesor tradicional 7/8, pero solo 1/4 vs software no-inteligente).
3. **Los más débiles ganan más** con tutoría escalonada (Vanzo, Létourneau) → argumento social directo para el problema Simce/PISA.
4. **La evaluación pedagógica automática todavía no es confiable** (Maurya: correlaciones negativas de LLM-juez; BEA 2025: F1≈0.58 en "guía") → nuestra validación debe ser humana + gold standard.
5. **Generar ejercicios alineados al currículum con LLM es viable** con modelos clase GPT-4o (≈93% cumplen todos los criterios), pero **fracciones es el tema con más fallas** → foco de la validación.

## Recomendaciones concretas
- **Prompt del tutor** (módulo pedagógico): codificar las reglas de Vanzo + dimensiones de Maurya — identificar el error y su ubicación, guiar sin revelar la respuesta, un paso accionable a la vez, tono alentador, no avanzar hasta respuesta correcta.
- **Rúbrica de validación**: adoptar (adaptada) la taxonomía de 8 dimensiones de Maurya et al. para la evaluación de "corrección pedagógica", complementando la comparación de respuestas finales vs ejercicios de referencia. Citar BEA 2025 para justificar evaluación humana.
- **Generación de ejercicios**: prompts con el texto completo del OA curricular + few-shot; filtro con los 4 criterios de EDUMATH (resoluble, exacto, apropiado, alineado); sobre-representar fracciones en el gold standard.
- **Posicionamiento del vacío de investigación** (Capítulo II): (a) solo 14% de estudios ITS en primaria (Létourneau), (b) 1 de 88 estudios empíricos LLM en Sudamérica (Shi), (c) casi nula atención a ética/privacidad (ambas revisiones) — nuestro proyecto en español, primaria, matemáticas, con consideraciones de Ley 21.719, cubre los tres.
- **Cuestionarios**: los instrumentos SESQ/ARCS de Vanzo (apéndice) pueden adaptarse para la evaluación heurística junto al SUS ya planificado.
- **Cuidado con el "2 sigma"**: citar Bloom como motivación histórica pero calibrar con VanLehn (d≈0.76–0.79) y los meta-análisis modernos (d≈0.3–0.4), como hace toda la literatura seria.
- **Limitaciones a añadir/reforzar**: revelación prematura de respuestas (más frecuente que la alucinación pura), sobre-dependencia/uso como muleta, brecha de alfabetización digital (Nigeria), y que el feedback LLM puede ser incorrecto ~1/3 de las veces en hints abiertos (IJAIED 2025, ya citado en el anteproyecto vía Danyaro).

---

# Segundo lote (8 papers, julio 2026): resúmenes individuales en `papers/*-T.md`

Análisis en profundidad de cada uno en su archivo `-T.md`. Lo que agregan al cuadro:

1. **Bastani et al. (RCT Turquía)** — el ancla causal del "doble filo": GPT Base −17% en examen sin ayuda vs GPT Tutor ≈0; GPT-4 solo 51% correcto sin apoyo; receta de barandas replicable (nunca revelar solución + pistas incrementales + **solución de referencia docente dentro del prompt** + errores comunes anticipados). Nuestro gold standard puede usarse *en producción* dentro del prompt, no solo para validar.
2. **Cho et al. (KT+LLM, revisión)** — mapa completo del modelo del estudiante (BKT→DKT→atención→LLM-KT). Conclusión para nosotros: modelo simple e interpretable (maestría por OA) es defendible; LLM útil para el cold-start (diagnóstico inicial); la interpretabilidad que piden es la que el dashboard del apoderado necesita.
3. **Ratinho et al. (meta-análisis gamificación en matemáticas)** — g=0.383 sobre motivación; puntos/niveles/feedback inmediato y progreso personal = perfil bueno; leaderboards/timers/recompensas externas = riesgo (SDT). Cubre secundaria/superior: citarlo declarando esa limitación.
4. **Schwendimann et al. (learning dashboards, revisión)** — definición canónica + taxonomía de 6 tipos de indicadores para derivar los del dashboard; brecha citable: ningún dashboard para apoderados en la literatura; advertencia: granularidad según alfabetización de datos del usuario.
5. **Bull & Kay (SMILI☺)** — marco formal para diseñar el dashboard como Open Learner Model (7 preguntas: por qué/qué/cómo/quién); skill meters = visualización con mejor evidencia; Self (1990): un arreglo de puntajes de maestría basta como modelo del estudiante; precedente de OLMs para padres.
6. **Araya et al. (ConectaIdeas RCT, Chile)** — +0.27σ SIMCE 4° básico: la evidencia local central. Nuestro proyecto ataca sus tres carencias declaradas: feedback sin explicación, sin adaptividad, y costo de coordinador/laboratorio. Su efecto negativo (−0.22σ preferencia por trabajo en equipo, peor en niñas) refuerza gamificación sin comparación social.
7. **Sugimaru & Glave (ConectaIdeas hogar, GRADE Perú)** — el escenario más parecido al nuestro (plataforma gamificada usada desde casa, 4° de primaria): el disfrute — no la utilidad percibida — predice el uso a los ~10 años; la alfabetización digital del cuidador predice el uso del niño → diseñar para un apoderado de competencia digital básica; la ansiedad matemática reduce el uso voluntario → tono del tutor debe bajarla.
8. **Priorización Curricular 2023-2025 (MINEDUC)** — jerarquización oficial basal/complementario que define nuestro alcance en dos anillos (ver `curriculo_4a6_matematica.md`); COPISI respalda representaciones pictóricas; la habilidad "g" ("identificar un error, explicar su causa y corregirlo") describe literalmente el módulo pedagógico.

## Qué cierra este lote respecto del primero

- **Dashboard del apoderado**: ahora tiene fundamento completo — marco de diseño (SMILI☺), indicadores y visualizaciones (Schwendimann), precedente local del dashboard docente (ConectaIdeas) y evidencia de adopción en el hogar mediada por el adulto (GRADE). La brecha "dashboard para apoderados de primaria" no está cubierta en la literatura → aporte declarable.
- **Gamificación**: par de citas complementarias — efecto causal en el tramo etario y país correctos (ConectaIdeas +0.27σ) + mecanismo y guía de diseño (Ratinho g=0.383, SDT) + motor de adopción a los 10 años (GRADE: disfrute).
- **Modelo del estudiante**: decisión informada — maestría por OA simple e interpretable (Self vía SMILI☺; Cho et al. para el vocabulario BKT/DKT y el cold-start con LLM).
- **Alcance curricular**: definido con fuente oficial (Priorización) y operacionalizado en `curriculo_4a6_matematica.md`.
