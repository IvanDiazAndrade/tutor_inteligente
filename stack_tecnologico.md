# Stack Tecnológico y Tope de Costo (Fase II, tarea 26)

**Proyecto:** Tutor inteligente basado en IA para el aprendizaje de matemáticas — eje de Números, 4°–6° básico.
**Documento:** Selección y justificación del stack. La arquitectura (`arquitectura.md`) dejó las tecnologías neutras a propósito; aquí se fijan contra los requisitos y los diseños de las tareas 22–24. Decisiones tomadas con el equipo: React + TypeScript en el frontend, PostgreSQL, hosting en nube con capa gratuita, tope de API US$5/mes; el backend se recomienda aquí (el equipo domina Node y Python por igual).

> **Actualización 24-sep-2026:** el equipo decidió que el cliente sea una **app nativa Android para teléfono y tablet** (Android 8 o superior, orientación vertical y horizontal, ambas vistas usables en los dos tamaños), en lugar de la SPA web. Cambia solo la capa del cliente: el frontend pasa de React web a **React Native + Expo** (se mantiene TypeScript y el conocimiento de React del equipo), y Render queda sirviendo solo la API. Backend, base de datos, LLM y prompts no cambian.

---

## 1. Criterios de selección

1. **Aritmética exacta como ciudadano de primera clase**: el corrector, el generador paramétrico y la capa 1 del pipeline prohíben floats (`modelo_dominio.md` §3, §8) — el lenguaje del backend debe hacer esto fácil y seguro.
2. **Validación estructural del JSON del ejercicio** en la frontera (RF-D3, pipeline capa 2).
3. **Equipo de 2 personas con plazo**: tecnologías establecidas, documentación abundante, mínima infraestructura que administrar.
4. **Costo ≈ 0** en desarrollo y validación (RNF-C1, C2) y una forma simple de **entregar la app a los evaluadores** para la evaluación heurística y el SUS a distancia.
5. Lo que exige la arquitectura: app nativa Android para teléfono y tablet (RNF-U4), API HTTPS (RNF-S5), BD relacional con agregaciones (AD-7), proceso asíncrono de reposición (F5), prompts fuera del código (RNF-M1).

## 2. Stack seleccionado (resumen)

| Capa | Tecnología | Rol |
|---|---|---|
| App (cliente) | **React Native + Expo** con **TypeScript** | app nativa Android (8+, `minSdkVersion` 26) para teléfono y tablet; dos vistas por rol |
| Navegación | **Expo Router** | pantalla de acceso que separa estudiante y apoderado; rutas protegidas por rol |
| Estilos | **NativeWind** (clases estilo Tailwind) | traducir los mockups rápido y consistente; distribuciones distintas por tamaño y orientación |
| Gráficos | **react-native-svg** | representaciones pictóricas (fracciones, recta numérica) y el personaje Octavio |
| Estado/datos | **TanStack Query** (React Query) | caché de API; sin gestor de estado global pesado |
| Sesión en el dispositivo | **expo-secure-store** | JWT guardado cifrado en el dispositivo (RNF-S1) |
| Backend | **Python 3.12 + FastAPI** (Uvicorn) | API REST; todos los componentes de `arquitectura.md` §3 |
| Validación | **Pydantic v2** | esquema del ejercicio y contratos de la API |
| ORM / migraciones | **SQLAlchemy 2 + Alembic** | entidades de `arquitectura.md` §4 |
| Base de datos | **PostgreSQL 16** | relacional + columnas JSONB para `erroresComunes`, `pistas`, `representacion` |
| Autenticación | **JWT** (PyJWT) + **bcrypt** (passlib) | RF-A2, RNF-S1 |
| LLM | **SDK oficial de OpenAI** (GPT-5.4 nano) con *structured outputs* | detrás del Adaptador (AD-4); salida forzada al esquema JSON del ejercicio |
| Prompts | archivos **Jinja2/YAML versionados** en `/prompts` del repo | RNF-M1: editar sin recompilar; versión registrada en `metadatos.versionPrompt` |
| Tarea asíncrona | **APScheduler** (in-process) | reposición del banco (F5) sin broker externo |
| Hosting | **Render**: un web service (solo la API) + PostgreSQL gestionado | API pública HTTPS; capa gratuita, opción ~US$7/mes el mes de validación |
| Compilación | **EAS Build** (capa gratuita) o build local con Android Studio | generar el APK/AAB firmado |
| Desarrollo | **Expo Go** + emulador de Android Studio | probar en el dispositivo sin compilar |
| Distribución | **APK directo** en la validación; prueba interna de Google Play opcional | instalar la app en los dispositivos de los evaluadores |
| Repositorio | **Git monorepo en GitHub** (`/docs`, `/app`, `/backend`, `/prompts`) | tarea 35; CI con GitHub Actions filtrado por carpeta (pytest; lint y pruebas de la app) |
| Testing | **pytest** (backend, tarea 52) · **Jest (jest-expo) + React Native Testing Library** (app) | pruebas unitarias e integración (tareas 52, 67, 69) |
| Pruebas en dispositivo | al menos 1 teléfono y 1 tablet Android reales + emulador con Android 8 | RNF-U4: ambos tamaños, ambas orientaciones |

## 3. Justificaciones clave

**Python/FastAPI sobre Node.js** (la decisión que estaba abierta): ambos sirven; inclina la balanza el corazón del sistema. `fractions.Fraction` y `decimal.Decimal` de la biblioteca estándar implementan *nativamente* la aritmética exacta que el corrector, el generador paramétrico y la capa 1 del pipeline exigen — en Node habría que traer dependencias y disciplina extra para evitar floats accidentales (`0.1 + 0.2 !== 0.3`), justo en el componente donde un descuido invalida RNF-P1. Además: Pydantic valida el JSON del ejercicio en la frontera (capa 2 del pipeline casi gratis), el SDK de OpenAI y los *structured outputs* están de primera clase en Python, y FastAPI genera documentación OpenAPI automática (útil para el informe y para el desarrollo en paralelo frontend/backend). El costo aceptado: dos lenguajes en el proyecto — mitigado porque el contrato de la API queda tipado en ambos lados (Pydantic ↔ TypeScript).

**TypeScript en la app**: los contratos (ejercicio sin solución, `DominioOA`, intentos) quedan tipados en compilación; los errores de forma aparecen al desarrollar, no en la demo. Los tipos se pueden generar desde el OpenAPI de FastAPI (`openapi-typescript`) para que la app y el backend no se desalineen.

**React Native + Expo para la app Android** (actualización 24-sep-2026): el equipo ya conoce React, y React Native permite reutilizar ese conocimiento, junto con TypeScript y TanStack Query. Una sola base de código cubre teléfono y tablet; las distribuciones por tamaño y orientación se resuelven con `useWindowDimensions` y clases de NativeWind. Expo evita administrar el proyecto Android a mano: Expo Go sirve para probar en el dispositivo durante el desarrollo y EAS Build genera el APK firmado. El costo aceptado: la entrega a evaluadores ya no es una URL sino un APK, y quedan fuera los usuarios de iPhone/iPad (ver `riesgos.md`, R10 y R16).

**APScheduler y no Celery/Redis**: la reposición del banco es un job periódico de minutos con lotes de 10–20 ejercicios — un scheduler dentro del propio proceso basta y elimina un broker que administrar y pagar. Si TT2 demostrara necesidad real de colas, el Adaptador ya aísla el punto de cambio.

**Sin framework de orquestación LLM (LangChain u similar)**: el Adaptador propio de AD-4 son ~3 operaciones (`generarEjercicio`, `generarRetroalimentacion`, `generarPista`) con plantillas Jinja2; un framework agregaría una capa de abstracción ajena justo donde RNF-M3 pide control directo para sustituir proveedor.

**Render como hosting**: web service + PostgreSQL gestionado con capa gratuita y despliegue desde GitHub. La instancia gratuita "duerme" tras inactividad (primer request lento): irrelevante en desarrollo, y el mes de la validación se sube al plan básico (~US$7) para cumplir RNF-R2/R4 con ~30 usuarios concurrentes. Con la app nativa, Render sirve solo la API; la app se instala en el dispositivo y se conecta por HTTPS.

**Repositorio y secretos**: el monorepo es público, por lo que no se suben la API key de OpenAI ni los `.env`, las credenciales de EAS ni el keystore de firma de Android (`*.jks`, `*.keystore`); si el keystore se pierde, no se puede publicar una actualización firmada de la app. Los secretos van en las variables de entorno de Render, en los secretos de EAS y en los *secrets* de GitHub Actions.

## 4. Costos y tope (RNF-C1, C2)

Precios de referencia GPT-5.4 nano (julio 2026): ~US$0,20 / 1M tokens de entrada, ~US$1,25 / 1M de salida (≈2× las estimaciones originales hechas con GPT-4o mini; siguen holgadamente dentro del tope de US$5 — re-estimar en Fase III con precios oficiales).

| Concepto | Estimación | Costo aprox. |
|---|---|---|
| Banco inicial: ~105 ejercicios verbales × (≈1.000 in + 700 out) × 2 pasadas (fracciones) + triaje | ~0,4M tokens | **< US$0,25** |
| Retroalimentación de error / pista reformulada: ≈800 in + 150 out por llamada | ~US$0,0002 por llamada | 5.000 llamadas ≈ US$1 |
| Sesión típica (20 ejercicios, ~8 errores con feedback, refuerzos locales sin LLM) | ~8 llamadas | **< US$0,01** |
| Mes de validación completo (banco + reposiciones + pruebas adversariales + 30 usuarios de prueba) | — | **US$1–2** |

**Tope: US$5/mes**, margen ×2–5 sobre el peor mes esperado. El Adaptador contabiliza tokens por llamada y acumulado mensual (RNF-C1): al **80%** alerta al equipo; al **100%** deja de llamar a la API y el sistema opera en modo degradado (F6) — que por diseño mantiene la práctica funcionando (pistas pre-generadas, plantillas locales). El tope es configuración, no código.

Compilar con EAS (capa gratuita) y distribuir el APK directo no tiene costo; publicar en Google Play exige una cuenta de desarrollador de pago único (~US$25) y es opcional.

Costo total de operación TT2: **US$0–7/mes** (API ≤5 + hosting 0, o ~7 el mes de validación) — compatible con presupuesto de estudiantes y evidencia de la viabilidad económica declarada en el anteproyecto.

## 5. Alternativas descartadas (registro)

| Alternativa | Por qué no |
|---|---|
| Node.js/Express en backend | sin aritmética exacta nativa; el riesgo de floats cae en el peor lugar (corrector/pipeline) |
| Vue / Svelte | válidos; React gana por ecosistema, documentación y familiaridad declarada en los bocetos |
| SPA web / PWA (diseño original) | reemplazada el 24-sep-2026 por decisión del equipo: app nativa Android para teléfono y tablet |
| Kotlin + Jetpack Compose | válido para Android; exige aprender un lenguaje nuevo y no reutiliza lo que el equipo sabe de React |
| Flutter | válido y multiplataforma; exige aprender Dart y otro ecosistema |
| MySQL/MariaDB | válido; PostgreSQL gana por JSONB ergonómico y disponibilidad en capas gratuitas |
| SQLite | cómodo en desarrollo, justo con ~30 concurrentes + job asíncrono escribiendo (RNF-R4); PostgreSQL desde el día 1 evita migrar |
| Celery + Redis | infraestructura sobredimensionada para un job periódico de lotes chicos |
| LangChain | abstracción innecesaria sobre 3 llamadas con plantillas; contradice el control directo de AD-4/RNF-M3 |
| VPS propio / local + túnel | administración o disponibilidad frágil durante las evaluaciones remotas |

## 6. Trazabilidad y puntos abiertos

| Requisito | Cómo lo cubre el stack |
|---|---|
| RNF-P1 (corrección ≥95%) | `Fraction`/`Decimal` en corrector, generador y pipeline |
| RNF-M1 (prompts editables) | Jinja2/YAML versionados en `/prompts` |
| RNF-M3 (proveedor sustituible) | Adaptador propio, sin framework LLM |
| RNF-R2/R4 (≤2 s, ~30 concurrentes) | banco en PostgreSQL sin LLM en línea; plan básico de Render el mes de validación |
| RNF-S1/S5 (bcrypt, HTTPS) | passlib/bcrypt, JWT guardado con expo-secure-store; TLS incluido en Render |
| RNF-C1/C2 (tope US$5, infra gratuita) | contabilidad de tokens en el Adaptador; capa gratuita + ~7 US$ puntual; EAS y APK directo sin costo |
| RNF-U4 (app Android, teléfono y tablet) | React Native + Expo + NativeWind; distribuciones por tamaño y orientación; `minSdkVersion` 26 |

**Queda para tareas siguientes:** ~~parámetros de llamada al LLM~~ → resuelto en `estrategia_llm.md` (tarea 27, actualizada 23-jul-2026: snapshot congelado de GPT-5.4 nano, temperaturas por operación, timeout 8 s, circuit breaker, sustitutos GPT-5.4 mini / Gemini Flash-Lite); versiones exactas (incluido el SDK de Expo) se congelan al configurar el entorno (Fase III, tareas 35–36); riesgos del stack (dependencia de OpenAI/Render, deriva y obsolescencia del modelo — el GPT-4o mini original quedó obsoleto durante TT1 y fue reemplazado por GPT-5.4 nano) → tarea 28.
