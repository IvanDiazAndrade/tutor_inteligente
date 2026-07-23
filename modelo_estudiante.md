# Modelo del Estudiante (Fase II, tarea 22)

**Proyecto:** Tutor inteligente basado en IA para el aprendizaje de matemáticas — eje de Números, 4°–6° básico.
**Documento:** Diseño preliminar del modelo del estudiante del ITS: señales registradas, algoritmo del índice de dominio, política de adaptación de nivel, arranque en frío, repaso y presentación del dominio por rol. Deriva de `requisitos.md` (RF-E1–E5, RF-G2, RF-DA2–DA6) y de `arquitectura.md` (§3 "Motor adaptativo", AD-5: índice simple e interpretable, sin knowledge tracing profundo). Consume las celdas **unidad × nivel** del banco definidas en `modelo_dominio.md`.

**Decisiones tomadas con el equipo para este documento:** índice = promedio móvil exponencial; señales = correcto/incorrecto + descuento por pistas (el tiempo se registra pero no puntúa); adaptación por umbral con histéresis + racha de seguridad; arranque en frío por sondeo integrado (nivel 2, α alto); sin decaimiento del índice — marca "para repasar"; navegación libre con sugerencia; apoderado ve 3 bandas de avance; estudiante ve solo la versión gamificada.

---

## 1. Señales: qué registra cada intento (RF-E1)

Cada respuesta evaluada por el corrector produce un `Intento` (entidad de `arquitectura.md` §4). El modelo del estudiante consume de él:

| Señal | Uso en el índice | Otro uso |
|---|---|---|
| `esCorrecta` | sí — resultado base | puntos (RF-G1), dashboard |
| `pistasUsadas` | sí — descuenta (§2) | descuento de puntos (RF-G1), indicador de dificultad (RF-DA3) |
| `tiempoSegundos` | **no** — premiaría apurarse, contra el encuadre sin presión de RF-DA6 | dashboard (tiempo de uso, RF-DA1) |
| patrón de error detectado | no (v1) | retroalimentación dirigida (RF-P2) y "tipos de ejercicio difíciles" (RF-DA3) |

Las respuestas rechazadas por formato (texto no parseable, denominador 0 — `modelo_dominio.md` §3) **no cuentan como intento**: no son evidencia de dominio matemático.

**Resultado ponderado** de un intento:

```
r = 0                                  si es incorrecta
r = max(0,4 ; 1 − 0,15 · pistasUsadas) si es correcta
```

Una correcta limpia vale 1; con una pista 0,85; con dos 0,70; el piso 0,4 reconoce que resolver con ayuda sigue siendo evidencia parcial de aprendizaje (coherente con el descuento de gamificación RF-G1: misma filosofía, otra escala).

---

## 2. Índice de dominio por OA (RF-E2)

Un valor `indice ∈ [0,1]` por estudiante × unidad (`DominioOA`), actualizado tras cada intento con **promedio móvil exponencial**:

```
indice ← indice + α · (r − indice)
```

- **α = 0,3** en régimen normal: lo reciente pesa más (un índice es una foto del estado actual, no un promedio histórico), pero un acierto o error aislado no lo dispara.
- **α = 0,5 durante los primeros 3 intentos de la unidad** (fase de sondeo, §4): el índice converge rápido a la zona real del estudiante.
- **Valor inicial: 0,5** (incertidumbre máxima, ni "no sabe" ni "domina").

Propiedades que motivan la elección (AD-5): un solo número persistido, actualización O(1), sin datos de entrenamiento previos, y explicable al apoderado en una frase: *"sube cuando responde bien, baja cuando se equivoca; lo último pesa más"*.

**Ejemplo trazado** (estudiante entra por primera vez a 4B-OA9):

| Intento | Nivel | Resultado | r | α | índice |
|---|---|---|---|---|---|
| — | 2 | (inicio) | — | — | 0,50 |
| 1 | 2 | correcta | 1,00 | 0,5 | 0,75 |
| 2 | 2 | correcta, 1 pista | 0,85 | 0,5 | 0,80 |
| 3 | 2 | correcta | 1,00 | 0,5 | 0,90 → **sube a nivel 3** (≥0,8 y racha 3) |
| 4 | 3 | incorrecta | 0,00 | 0,3 | 0,63 |
| 5 | 3 | correcta | 1,00 | 0,3 | 0,74 |

---

## 3. Adaptación de nivel dentro de la unidad (RF-E3)

El nivel actual (1–3) por estudiante × unidad decide de qué **celda unidad×nivel** del banco se sirve el siguiente ejercicio (F1 de la arquitectura). Reglas:

- **Sube** (1→2, 2→3) cuando `indice ≥ 0,8` **y** las últimas **3 respuestas del nivel actual fueron correctas** (racha de seguridad: impide subir por historial viejo o por aciertos alternados).
- **Baja** (3→2, 2→1) cuando `indice < 0,4`. Sin condición de racha: ante evidencia de frustración se actúa rápido (RF-P5: el error no debe acumularse en castigo).
- La **histéresis** (0,8 / 0,4) deja una zona estable amplia [0,4–0,8) donde se practica sin cambios de nivel — evita el ping-pong.
- La racha se reinicia con cada respuesta incorrecta y con cada cambio de nivel.
- En el nivel 3 con `indice ≥ 0,8` no hay adónde subir: la unidad queda **Dominada** (§6) y el sistema sugiere otra unidad (§5), sin bloquear seguir practicando.

Pseudocódigo del motor (referencia para Fase IV, tarea 56):

```
tras corregir(intento):
    r ← ponderar(intento)                        # §1
    α ← 0,5 si intentosEnUnidad ≤ 3, sino 0,3    # §2, §4
    dominio.indice ← dominio.indice + α·(r − dominio.indice)
    actualizar racha, fechaUltimoIntento
    si indice ≥ 0,8 y racha ≥ 3 y nivel < 3:  nivel += 1
    si indice < 0,4 y nivel > 1:              nivel −= 1
```

---

## 4. Arranque en frío: sondeo integrado (RF-E4)

Primera vez en una unidad: **nivel inicial 2, índice 0,5**, y los primeros 3 intentos usan α = 0,5. No hay test diagnóstico separado — el estudiante solo percibe que está practicando, pero en 2–3 ejercicios el índice ya lo ubicó:

- 3 correctas → índice ≈ 0,94: sube a nivel 3 de inmediato (el que domina no se aburre).
- 3 incorrectas → índice ≈ 0,06: baja a nivel 1 en el segundo fallo (el que no domina no se frustra).

Los intentos de sondeo **sí otorgan puntos** (RF-G1): no existe una modalidad "sin premio" que delate la evaluación.

---

## 5. Repaso y navegación entre unidades

**Sin decaimiento del índice**: el número solo cambia con intentos — el niño nunca ve bajar un logro sin haber hecho nada (RF-DA6) y el apoderado no ve medidores que se mueven solos. El olvido se modela como **marca, no como castigo**:

- `paraRepasar = true` cuando pasan **21 días sin intentos** en una unidad con `indice ≥ 0,4` (solo unidades donde hubo avance real; una unidad apenas tocada no "se oxida", simplemente sigue pendiente).
- La marca se limpia tras una sesión de práctica en la unidad (≥3 intentos nuevos).
- La marca alimenta la **sugerencia** al estudiante y las **sugerencias accionables** del apoderado (RF-DA5: "esta semana conviene repasar fracciones equivalentes").

**Navegación libre con sugerencia**: el estudiante ve todas las unidades de su curso y de los cursos anteriores (un estudiante de 5° ve 4° y 5°) y elige libremente — la autonomía sostiene el uso voluntario (Sugimaru & Glave). El sistema **destaca una unidad sugerida**, elegida por prioridad:

1. la unidad `paraRepasar` más antigua;
2. si no hay: la unidad iniciada con menor índice (< 0,6);
3. si no hay: la siguiente unidad no iniciada según el `orden` del catálogo de su curso.

Las unidades de cursos superiores no se muestran (evita que un niño de 4° entre a decimales de 6° y se frustre sin que el motor pueda impedirlo).

---

## 6. Presentación del dominio: un dato, dos encuadres (RF-DA2, RF-G2)

El mismo `DominioOA` se proyecta distinto por rol (AD-8: una fuente de verdad, dos vistas):

| Banda del índice | Apoderado (skill meter) | Estudiante (gamificación) |
|---|---|---|
| < 0,4 | **Empezando** | unidad nivel ⭐ |
| 0,4 – 0,8 | **Practicando** | unidad nivel ⭐⭐ |
| ≥ 0,8 | **Dominado** | unidad nivel ⭐⭐⭐ + insignia de unidad |

- **Apoderado**: barra continua con la banda en lenguaje ciudadano y la `descripcionCiudadana` del OA (RF-DA2), sin porcentajes tipo nota escolar ni rojos punitivos (RF-DA6); las unidades `paraRepasar` aparecen como sugerencia, no como alerta.
- **Estudiante**: nunca ve un "medidor de evaluación"; ve el nivel de la unidad, sus puntos y sus insignias (RF-G2). Los cortes de banda coinciden con los umbrales de adaptación (0,4 / 0,8): una sola escala en todo el sistema — subir de estrellas y subir de nivel de dificultad son el mismo evento contado de dos formas.
- Sin ningún elemento comparativo entre estudiantes, en ninguna de las dos vistas (RF-G3, por construcción).

---

## 7. Casos borde

- **RF-P7 (3 fallos consecutivos → explicación guiada):** los 3 intentos fallidos ya bajaron el índice por la vía normal; la explicación guiada no lo modifica, y el **ejercicio análogo** que la acompaña cuenta como un intento normal. Si con eso el índice cayó bajo 0,4, la baja de nivel ya ocurrió — la explicación guiada y la bajada de nivel se complementan, no se duplican.
- **Celda agotada** (el estudiante vio los 5 ejercicios activos de su unidad×nivel): se re-sirve el ejercicio respondido hace más tiempo mientras el proceso de reposición (F5) rellena la celda; el umbral de reposición de `modelo_dominio.md` §5 hace este caso poco frecuente.
- **Cambio de curso del estudiante** (nuevo año escolar, RF-A3): los índices se conservan — las unidades del curso anterior pasan a ser material de repaso, no se reinician.

---

## 8. Extensión de la entidad `DominioOA`

El modelo de datos de `arquitectura.md` §4 se precisa con los campos que este diseño necesita:

```
DominioOA: estudianteId, oaCodigo, indice (0–1), nivelActual (1–3),
           rachaCorrectas, intentosEnUnidad, fechaUltimoIntento
```

`paraRepasar` y la banda **se derivan por consulta** (de `fechaUltimoIntento` y de `indice`), no se almacenan — misma regla que el "progreso" (una sola fuente de verdad).

---

## 9. Trazabilidad y puntos abiertos

| Requisito | Dónde se resuelve aquí |
|---|---|
| RF-E1 (registro de intentos) | §1 |
| RF-E2 (índice de dominio por OA) | §2 |
| RF-E3 (adaptación entre 3 niveles) | §3 |
| RF-E4 (diagnóstico inicial) | §4 |
| RF-E5 (progreso visible) | §6 |
| RF-G2 (niveles por unidad) | §6 (bandas = niveles) |
| RF-DA2, DA5, DA6 (skill meters, sugerencias, encuadre) | §5, §6 |
| AD-5 (simple e interpretable) | §2 (una fórmula, un número, explicable en una frase) |

**Parámetros a calibrar en TT2** (con datos sintéticos y las pruebas de las tareas 70–74, no hay estudiantes reales): α (0,3/0,5), descuento por pista (0,15, piso 0,4), umbrales (0,8/0,4), racha (3), días de repaso (21). Todos viven en configuración, no en código (RNF-M1 extendido al motor).
**Se resuelve en tareas siguientes:** cómo usa el tutor la banda y la racha para modular tono y andamiaje de las pistas → tarea 24; visualización concreta de skill meters y estrellas → tarea 25 (mockups).
