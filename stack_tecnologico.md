# Stack Tecnológico y Tope de Costo (Fase II, tarea 26)

**Proyecto:** Tutor inteligente basado en IA para el aprendizaje de matemáticas — eje de Números, 4°–6° básico.
**Documento:** Selección y justificación del stack. La arquitectura (`arquitectura.md`) dejó las tecnologías neutras a propósito; aquí se fijan contra los requisitos y los diseños de las tareas 22–24. Decisiones tomadas con el equipo: React + TypeScript en el frontend, PostgreSQL, hosting en nube con capa gratuita, tope de API US$5/mes; el backend se recomienda aquí (el equipo domina Node y Python por igual).

---

## 1. Criterios de selección

1. **Aritmética exacta como ciudadano de primera clase**: el corrector, el generador paramétrico y la capa 1 del pipeline prohíben floats (`modelo_dominio.md` §3, §8) — el lenguaje del backend debe hacer esto fácil y seguro.
2. **Validación estructural del JSON del ejercicio** en la frontera (RF-D3, pipeline capa 2).
3. **Equipo de 2 personas con plazo**: tecnologías establecidas, documentación abundante, mínima infraestructura que administrar.
4. **Costo ≈ 0** en desarrollo y validación (RNF-C1, C2) y **URL pública** para la evaluación heurística y el SUS a distancia.
5. Lo que exige la arquitectura: SPA en navegador (RNF-U4), API HTTPS (RNF-S5), BD relacional con agregaciones (AD-7), proceso asíncrono de reposición (F5), prompts fuera del código (RNF-M1).

## 2. Stack seleccionado (resumen)

| Capa | Tecnología | Rol |
|---|---|---|
| Frontend | **React 18 + TypeScript**, build con Vite | SPA, dos vistas por rol; SVG inline (pictórico, Octavio) |
| Estilos | **Tailwind CSS** | traducir los mockups rápido y consistente |
| Estado/datos | **TanStack Query** (React Query) | caché de API; sin gestor de estado global pesado |
| Backend | **Python 3.12 + FastAPI** (Uvicorn) | API REST; todos los componentes de `arquitectura.md` §3 |
| Validación | **Pydantic v2** | esquema del ejercicio y contratos de la API |
| ORM / migraciones | **SQLAlchemy 2 + Alembic** | entidades de `arquitectura.md` §4 |
| Base de datos | **PostgreSQL 16** | relacional + columnas JSONB para `erroresComunes`, `pistas`, `representacion` |
| Autenticación | **JWT** (PyJWT) + **bcrypt** (passlib) | RF-A2, RNF-S1 |
| LLM | **SDK oficial de OpenAI** (GPT-4o mini) con *structured outputs* | detrás del Adaptador (AD-4); salida forzada al esquema JSON del ejercicio |
| Prompts | archivos **Jinja2/YAML versionados** en `/prompts` del repo | RNF-M1: editar sin recompilar; versión registrada en `metadatos.versionPrompt` |
| Tarea asíncrona | **APScheduler** (in-process) | reposición del banco (F5) sin broker externo |
| Hosting | **Render**: un web service (API + SPA compilada) + PostgreSQL gestionado | URL pública HTTPS; capa gratuita, opción ~US$7/mes el mes de validación |
| Repositorio | **Git monorepo en GitHub** (`/frontend`, `/backend`, `/prompts`) | tarea 35; CI simple con GitHub Actions (pytest + build) |
| Testing | **pytest** (backend, tarea 52) · **Vitest + React Testing Library** (frontend) | pruebas unitarias e integración (tareas 52, 67, 69) |

## 3. Justificaciones clave

**Python/FastAPI sobre Node.js** (la decisión que estaba abierta): ambos sirven; inclina la balanza el corazón del sistema. `fractions.Fraction` y `decimal.Decimal` de la biblioteca estándar implementan *nativamente* la aritmética exacta que el corrector, el generador paramétrico y la capa 1 del pipeline exigen — en Node habría que traer dependencias y disciplina extra para evitar floats accidentales (`0.1 + 0.2 !== 0.3`), justo en el componente donde un descuido invalida RNF-P1. Además: Pydantic valida el JSON del ejercicio en la frontera (capa 2 del pipeline casi gratis), el SDK de OpenAI y los *structured outputs* están de primera clase en Python, y FastAPI genera documentación OpenAPI automática (útil para el informe y para el desarrollo en paralelo frontend/backend). El costo aceptado: dos lenguajes en el proyecto — mitigado porque el contrato de la API queda tipado en ambos lados (Pydantic ↔ TypeScript).

**TypeScript en el frontend**: los contratos (ejercicio sin solución, `DominioOA`, intentos) quedan tipados en compilación; los errores de forma aparecen al desarrollar, no en la demo.

**APScheduler y no Celery/Redis**: la reposición del banco es un job periódico de minutos con lotes de 10–20 ejercicios — un scheduler dentro del propio proceso basta y elimina un broker que administrar y pagar. Si TT2 demostrara necesidad real de colas, el Adaptador ya aísla el punto de cambio.

**Sin framework de orquestación LLM (LangChain u similar)**: el Adaptador propio de AD-4 son ~3 operaciones (`generarEjercicio`, `generarRetroalimentacion`, `generarPista`) con plantillas Jinja2; un framework agregaría una capa de abstracción ajena justo donde RNF-M3 pide control directo para sustituir proveedor.

**Render como hosting**: web service + PostgreSQL gestionado con capa gratuita y despliegue desde GitHub. La instancia gratuita "duerme" tras inactividad (primer request lento): irrelevante en desarrollo, y el mes de la validación se sube al plan básico (~US$7) para cumplir RNF-R2/R4 con ~30 usuarios concurrentes. La SPA compilada se sirve desde el mismo servicio (un solo origen: sin CORS, un solo deploy, cero costo extra).

## 4. Costos y tope (RNF-C1, C2)

Precios de referencia GPT-4o mini: ~US$0,15 / 1M tokens de entrada, ~US$0,60 / 1M de salida.

| Concepto | Estimación | Costo aprox. |
|---|---|---|
| Banco inicial: ~105 ejercicios verbales × (≈1.000 in + 700 out) × 2 pasadas (fracciones) + triaje | ~0,4M tokens | **< US$0,25** |
| Retroalimentación de error / pista reformulada: ≈800 in + 150 out por llamada | ~US$0,0002 por llamada | 5.000 llamadas ≈ US$1 |
| Sesión típica (20 ejercicios, ~8 errores con feedback, refuerzos locales sin LLM) | ~8 llamadas | **< US$0,01** |
| Mes de validación completo (banco + reposiciones + pruebas adversariales + 30 usuarios de prueba) | — | **US$1–2** |

**Tope: US$5/mes**, margen ×2–5 sobre el peor mes esperado. El Adaptador contabiliza tokens por llamada y acumulado mensual (RNF-C1): al **80%** alerta al equipo; al **100%** deja de llamar a la API y el sistema opera en modo degradado (F6) — que por diseño mantiene la práctica funcionando (pistas pre-generadas, plantillas locales). El tope es configuración, no código.

Costo total de operación TT2: **US$0–7/mes** (API ≤5 + hosting 0, o ~7 el mes de validación) — compatible con presupuesto de estudiantes y evidencia de la viabilidad económica declarada en el anteproyecto.

## 5. Alternativas descartadas (registro)

| Alternativa | Por qué no |
|---|---|
| Node.js/Express en backend | sin aritmética exacta nativa; el riesgo de floats cae en el peor lugar (corrector/pipeline) |
| Vue / Svelte | válidos; React gana por ecosistema, documentación y familiaridad declarada en los bocetos |
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
| RNF-S1/S5 (bcrypt, HTTPS) | passlib/bcrypt, JWT; TLS incluido en Render |
| RNF-C1/C2 (tope US$5, infra gratuita) | contabilidad de tokens en el Adaptador; capa gratuita + ~7 US$ puntual |
| RNF-U4 (SPA responsiva) | React + Tailwind, mobile-first según mockups |

**Queda para tareas siguientes:** ~~parámetros de llamada al LLM~~ → resuelto en `estrategia_llm.md` (tarea 27: snapshot congelado de GPT-4o mini, temperaturas por operación, timeout 8 s, circuit breaker, sustitutos GPT-4.1 mini / Gemini Flash-Lite); versiones exactas se congelan al configurar el entorno (Fase III, tareas 35–36); riesgos del stack (dependencia de OpenAI/Render, deriva y obsolescencia del modelo — GPT-4o mini es *legacy* desde enero 2026) → tarea 28.
