# Prompts para los mockups (Fase II, tarea 25)

**Uso:** pegar en Claude (claude.ai o Claude Code) el **Bloque 0 (estilo compartido)** seguido del prompt de la pantalla que quieras. Si haces todas las pantallas en una misma conversación, el Bloque 0 se pega una sola vez al inicio. Cada prompt produce un archivo HTML autocontenido listo para abrir en el navegador y capturar para el informe.

Los contenidos de ejemplo vienen de los documentos de diseño (`modelo_dominio.md`, `modelo_estudiante.md`, `modelo_pedagogico.md`) para que los mockups sean evidencia fiel del sistema, no dibujos genéricos.

---

## Bloque 0 — Estilo compartido (pegar siempre primero)

```
Vas a crear mockups de alta fidelidad para "Tutor Octavio", una app web educativa
de matemáticas para niños chilenos de 4° a 6° básico (9–12 años), con una vista
para el estudiante y otra para el apoderado (padre/madre). Reglas para TODOS los
mockups que te pida:

FORMATO
- Un solo archivo HTML autocontenido: CSS y SVG inline, sin librerías externas,
  sin imágenes remotas, sin JavaScript (mockup estático).
- Marco de teléfono (390×844 px, esquinas redondeadas, notch simple) centrado
  sobre un fondo gris neutro, para verse bien como captura en un informe.

ESTILO VISUAL: cartoon flat colorido, estilo app educativa moderna (tipo Duolingo)
- Color primario: morado (#6D28D9 con variantes #8B5CF6 y fondo lavanda #F5F1FF).
- Acentos: amarillo estrella #FBBF24, verde éxito #34D399, coral amable #FB7185
  (nunca rojo alarma), azul noche #312E81 para el sombrero de Octavio.
- Fondo de pantalla claro (#FAF7FF), tarjetas blancas con esquinas de 20 px y
  sombra muy suave, botones grandes (mínimo 48 px de alto), tipografía redondeada
  (font-family: 'Nunito', 'Quicksand', ui-rounded, sans-serif).

LA MASCOTA: Octavio, un pulpo morado MAGO, dibujado como SVG flat inline
- Cuerpo morado (#8B5CF6) redondo y amigable, ojos grandes con brillo, sonrisa.
- Sombrero de mago azul noche puntiagudo con ESTAMPADO de símbolos + − × ÷ en
  amarillo, y un ala ancha.
- 6–8 tentáculos visibles; varios sostienen VARITAS mágicas (palito café con
  estrella amarilla en la punta). Puede tener chispas/estrellitas alrededor.
- Aparece según la pantalla: mediano junto a un globo de diálogo, o pequeño como
  ícono. Dibújalo simple (formas básicas SVG), consistente entre pantallas.

TEXTO DE LA INTERFAZ
- Español de Chile, tuteo, tono alentador y no punitivo. Vocabulario escolar
  chileno: "sustracción", "décimos", "denominador".
- Números con coma decimal (0,5) y punto de miles ($1.000).

PROHIBIDO EN CUALQUIER PANTALLA
- Comparaciones entre estudiantes, rankings, promedios de otros niños.
- Rojos punitivos, ceros gigantes, lenguaje de examen ("malo", "reprobado").
- Mostrar la respuesta correcta de un ejercicio en pantalla.
```

---

## Prompt 1 — Pantalla de ejercicio con tutor (la central)

```
Crea el mockup de la PANTALLA DE EJERCICIO del estudiante.

Barra superior: flecha volver, título "Fracciones: sumar con igual denominador"
(unidad 4B-OA9), y a la derecha un contador de puntos "⭐ 1.250".

Bajo la barra: chip pequeño "Nivel 2" y racha "🔥 2 seguidas".

Tarjeta principal del ejercicio:
- Enunciado: "Pedro tiene 1/4 de pizza y su hermana le regala 2/4 más.
  ¿Qué fracción de pizza tiene ahora?"
- Debajo, representación pictórica SVG: un círculo (pizza) dividido en 4 partes
  iguales, 1 parte pintada de morado y 2 de amarillo, con borde delgado.
- Campo de respuesta de fracción: dos casillas grandes apiladas (numerador arriba,
  denominador abajo) separadas por una línea horizontal, con teclado numérico
  insinuado abajo o placeholder "?".
- Botón primario grande "Responder".

Zona del tutor (entre la tarjeta y el fondo): Octavio mediano a la izquierda,
con globo de diálogo que dice: "Fíjate bien en los números de abajo de cada
fracción. ¡Tú puedes!".

Fila de acciones secundarias (botones tipo píldora):
- "💡 Pista (quedan 3)"  - "🤔 No entiendo"  - "↻ Otro ejercicio"

La pantalla debe verse alegre pero sin distraer del ejercicio.
```

## Prompt 2 — Home del estudiante (mapa de unidades)

```
Crea el mockup del HOME DEL ESTUDIANTE (después de entrar con su PIN).

Encabezado: "¡Hola, Vale!" con Octavio pequeño saludando con una varita,
puntos totales "⭐ 1.250" y racha semanal "🔥 3 días".

Tarjeta destacada "Octavio te sugiere" (borde morado, varita apuntando):
unidad "Fracciones equivalentes" con etiqueta "¡A repasar!" y botón "Practicar".

Debajo, lista/mapa vertical de unidades del curso (5° básico) como tarjetas,
cada una con: nombre en lenguaje simple, estrellas de dominio (⭐ a ⭐⭐⭐) y una
insignia de "¡Dominada!" cuando tiene 3 estrellas. Ejemplos:
- "Números grandes" ⭐⭐⭐ (dominada, con insignia)
- "Multiplicación" ⭐⭐
- "Fracciones equivalentes" ⭐⭐ (marcada "¡A repasar!")
- "Sumar y restar fracciones" ⭐
- "Decimales" (sin empezar, SIN candado: solo estrellas vacías y "¡Nueva!")

Al final, un acceso discreto "Ver unidades de 4° básico" (repaso de cursos
anteriores). Barra de navegación inferior simple: Inicio · Practicar · Mis logros.
```

## Prompt 3 — Dashboard del apoderado

```
Crea el mockup del DASHBOARD DEL APODERADO (adulto, competencia digital básica:
pocas vistas, texto explicativo, nada técnico).

Encabezado sobrio (mantiene la paleta pero más calmo): "Progreso de Vale" y
selector de semana "Esta semana ▾".

1) Tarjeta RESUMEN SEMANAL con 4 datos grandes y claros:
   "23 ejercicios resueltos" · "7 de cada 10 correctos" · "1 h 40 min de práctica"
   · "Practicó 3 días". Con una mini-tendencia (barras simples por día).

2) Tarjeta "QUÉ ESTÁ APRENDIENDO": medidores de habilidad (skill meters), una
   barra horizontal por unidad con 3 estados en lenguaje ciudadano y color:
   - "Leer y escribir números grandes" → Dominado (barra llena, verde suave)
   - "Multiplicar números de dos cifras" → Practicando (media, morado)
   - "Fracciones equivalentes" → Practicando (media, morado)
   - "Sumar y restar fracciones" → Empezando (corta, amarillo — NO rojo)
   Cada barra con texto pequeño explicativo, ej: "Le está costando un poco:
   usa hartas pistas aquí".

3) Tarjeta "SUGERENCIA DE LA SEMANA" con ícono de Octavio pequeño:
   "Esta semana conviene repasar fracciones equivalentes. Practicar 10 minutos,
   2 o 3 veces por semana, ayuda más que una sesión larga."

Pie con nota de privacidad en letra pequeña: "Ves indicadores del avance de Vale.
Las conversaciones con el tutor son privadas."

Encuadre 100% de avance y apoyo: sin alarmas, sin comparaciones con otros niños.
```

## Prompt 4 — Acceso y selección de perfil

```
Crea el mockup de ACCESO en dos paneles apilados dentro del mismo teléfono
(como storyboard vertical de dos pantallas):

PANEL A — Login del apoderado: logo "Tutor Octavio" (Octavio con su sombrero
de símbolos), campos "Correo" y "Contraseña", botón "Entrar", enlace
"Crear cuenta". Limpio y simple.

PANEL B — Selección de perfil (tras el login): título "¿Quién va a practicar?",
tarjeta grande del estudiante "Vale · 5° básico" con avatar genérico, y al
tocarla un teclado de PIN de 4 dígitos con puntos grandes, título "Escribe tu
PIN secreto" y Octavio pequeño guiñando. Además una tarjeta secundaria
"Soy el apoderado → ver progreso".

Transmitir: una cuenta familiar, el niño entra fácil con su PIN (sin correo),
y los datos del niño son mínimos (solo alias y curso).
```

## Prompt 5 — Hoja de personaje de Octavio (opcional, para el informe)

```
Crea una LÁMINA DE PERSONAJE de Octavio en HTML+SVG: fondo claro, título
"Octavio — tutor de matemáticas", y el personaje dibujado en flat SVG en
4 poses sobre una grilla de 2×2, cada una rotulada:
- "Saludando": varita en alto con chispas.
- "Celebrando": confeti y dos varitas arriba ("¡Muy bien!").
- "Pensando": tentáculo en el mentón, signo de interrogación suave (para
  retroalimentación de error, gesto curioso, jamás enojado).
- "Descansando": dormido con gorro caído y zzz (modo degradado del sistema).
Debajo, una fila con la paleta de colores usada (morado #8B5CF6, azul noche
#312E81, amarillo #FBBF24) y los símbolos + − × ÷ del estampado del sombrero.
```

---

## Después de generar

- Capturar cada pantalla y llevarla al informe (tarea 25 → insumo de las tareas 29–33 y del prototipo de interfaz de Fase III, tarea 42).
- Verificar contra la lista PROHIBIDO del Bloque 0 antes de dar por buena una pantalla.
- Los textos de ejemplo (unidades, indicadores, sugerencias) son datos reales del diseño: si Claude los cambia, corregirlos.
