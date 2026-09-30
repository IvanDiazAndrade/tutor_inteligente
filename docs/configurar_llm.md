# Configurar el LLM

El tutor funciona sin LLM: sin clave responde con sus mensajes locales (modo degradado, flujo
F6) y la app se puede usar y probar completa. Esta guía es para activar el LLM cuando el equipo
tenga la clave de OpenAI (estrategia_llm.md).

## Qué hace el LLM y qué no

- **Sí redacta:** la retroalimentación de una respuesta incorrecta, la reformulación de las
  pistas del banco, la re-explicación de "No entiendo" y la narración de "Resolvamos juntos".
- **No decide nada:** la corrección, los puntos y el índice se calculan antes de llamarlo
  (AD-2). La respuesta correcta nunca llama al LLM.
- **No recibe datos personales:** solo el ejercicio, la respuesta numérica del niño, la banda
  (Empezando, Practicando o Dominado) y la racha. El LLM escribe `{nombre}` y el servidor pone
  el alias después de filtrar (RNF-S3).
- **Se filtra antes de mostrar:** si el texto revela la respuesta final (literal o
  equivalente, como 6/8 por 3/4) o si una pista o narración trae números que no estaban en el
  ejercicio, se descarta, se registra en `evento_filtro` y se usa el mensaje local.

## Pasos

1. Crear la clave en la consola de OpenAI, en un proyecto propio del tutor, con un límite de
   gasto mensual en la consola además del tope del backend.
2. Copiar `backend/.env.example` a `backend/.env` (nunca se sube al repositorio) y completar:
   - `OPENAI_API_KEY`: la clave.
   - `LLM_MODELO`: el snapshot exacto que muestra la consola (por ejemplo
     `gpt-5.4-nano-AAAA-MM-DD`), para que el comportamiento no cambie sin aviso.
   - `LLM_PRECIO_ENTRADA_USD_MTOK` y `LLM_PRECIO_SALIDA_USD_MTOK`: los precios vigentes por
     millón de tokens. El costo de cada llamada se calcula con ellos.
   - `LLM_USAR_TEMPERATURA=false` si el modelo responde que no acepta `temperature`.
3. Reiniciar el backend. En Render, las mismas variables van en *Environment*.

## Cómo verificar

- En la app, responder mal un ejercicio: el mensaje cambia respecto del local y la
  respuesta de la API trae `degradado: false`.
- En la base de datos:

  ```sql
  SELECT operacion, resultado, latencia_ms, tokens_entrada, tokens_salida, costo_usd
  FROM llamada_llm ORDER BY id DESC LIMIT 10;

  SELECT operacion, texto_bloqueado FROM evento_filtro ORDER BY id DESC LIMIT 10;
  ```

  `resultado` puede ser `ok`, `filtrado` (el filtro lo descartó), `timeout` o `error` (se
  reintentó dos veces), `degradado` (circuit breaker abierto tras 5 fallos seguidos, por 60 s)
  o `tope` (se alcanzó el tope mensual).

## Ajustes disponibles

Todos en `backend/tutor/config.py`, sobreescribibles por variable de entorno:
`LLM_TIMEOUT_SEGUNDOS` (8), `LLM_REINTENTOS` (2), `LLM_FALLOS_PARA_CORTE` (5),
`LLM_SEGUNDOS_DE_CORTE` (60), `LLM_TOPE_USD` (5) y `LLM_ALERTA_FRACCION` (0,8).

Los prompts están en `/prompts` y declaran su versión en la primera línea; esa versión se guarda
en cada llamada para comparar la calidad entre versiones (tarea 58).

## Pruebas

Las pruebas usan un proveedor simulado y nunca llaman a OpenAI, aunque haya una clave en
`backend/.env`.
