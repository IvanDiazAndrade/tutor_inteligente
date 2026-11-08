# Diagramas de Secuencia (Fase III, tarea 39)

**Proyecto:** Tutor inteligente basado en IA para el aprendizaje de matemáticas — eje de Números, 4°–6° básico.
**Documento:** Diagramas de secuencia de los flujos F1–F6 de `arquitectura.md` §5, más el acceso del estudiante y la explicación guiada. Usan las clases de `diagrama_clases.md` y las tablas de `modelo_base_datos.md`. En §1 se fija el contrato preliminar de la API que usan los diagramas, para que la app y el backend puedan avanzar en paralelo en la Fase IV.

---

## 1. Contrato preliminar de la API

Todas las rutas van sobre HTTPS con el JWT en la cabecera `Authorization` (salvo el registro y el login del apoderado). El rol del token restringe las rutas: `/estudiante/*` exige rol `estudiante`, `/apoderado/*` exige rol `apoderado` y `/auth/dispositivo/*` exige el token de `dispositivo`, que vincula el teléfono a la cuenta (§2).

| Método y ruta | Rol | Flujo | Respuesta (resumen) |
|---|---|---|---|
| `POST /auth/apoderado/registro` | — | CU-9 | apoderado creado |
| `POST /auth/apoderado/login` | — | CU-1 (§2) | JWT de apoderado + JWT de dispositivo |
| `POST /auth/dispositivo/estudiante` | dispositivo | CU-1 (§2) | JWT de estudiante (sin PIN) |
| `POST /auth/dispositivo/apoderado` | dispositivo | CU-1 (§2) | JWT de apoderado, con el PIN del panel |
| `POST /apoderado/estudiante` · `PATCH /apoderado/estudiante` | apoderado | CU-9 | perfil (alias, curso) |
| `PUT /apoderado/pin` | apoderado | CU-9 | cambia el PIN del panel |
| `GET /apoderado/dashboard` | apoderado | F4 | resumen semanal, medidores, unidades difíciles, sugerencias |
| `GET /estudiante/perfil` | estudiante | CU-6 | alias, curso y puntos |
| `GET /estudiante/unidades` | estudiante | CU-2 | unidades visibles con estrellas + unidad sugerida + `conEjercicios` (si ya hay ejercicios activos para practicarla) |
| `GET /estudiante/lecciones` | estudiante | CU-15 | lecciones de las unidades visibles, con sus partes (RF-D9; agregado 2-nov-2026) |
| `POST /estudiante/sesiones` · `POST /estudiante/sesiones/{id}/cierre` | estudiante | — | abre y cierra la sesión |
| `POST /estudiante/unidades/{unidad}/ejercicio` | estudiante | F1 | `EjercicioParaEstudiante` + id del ejercicio servido |
| `POST /estudiante/servidos/{id}/respuestas` | estudiante | F2 | `RespuestaTutor` |
| `POST /estudiante/servidos/{id}/pistas` | estudiante | F3 | `RespuestaTutor` |
| `POST /estudiante/servidos/{id}/no-entiendo` | estudiante | F2 | `RespuestaTutor` |
| `POST /estudiante/servidos/{id}/resolver-juntos` | estudiante | RF-P7 | pasos narrados + id del ejercicio análogo |
| `GET /estudiante/progreso` | estudiante | CU-6 | puntos, estrellas e insignias *(prevista; por ahora la pestaña Perfil usa `/estudiante/perfil` y `/estudiante/unidades`)* |

`RespuestaTutor` = `{ resultado: correcta | incorrecta | formato_invalido, mensaje, puntos, pistasRestantes, ofreceResolverJuntos, cambioNivel, degradado }`. Nunca contiene la respuesta final ni la solución de referencia.

## 2. Acceso: teléfono vinculado, estudiante y panel (CU-1)

*Actualizado el 2-nov-2026 (RF-A3).* El apoderado inicia sesión una vez por teléfono con correo y contraseña. La respuesta trae, además del JWT del panel (60 min), un **JWT de dispositivo** (30 días) que se guarda en `expo-secure-store` y solo sirve para dos cosas: entrar como el estudiante, sin PIN, y abrir el panel con el PIN del apoderado. El teléfono recuerda el perfil del estudiante de la cuenta vinculada (solo id, alias y curso), así el niño lo toca y entra. Cerrar sesión en el teléfono borra el JWT de dispositivo y el perfil recordado.

```mermaid
sequenceDiagram
    autonumber
    actor A as Apoderado
    actor E as Estudiante
    participant App as App Android
    participant API as ServicioAuth
    participant DB as PostgreSQL

    A->>App: correo + contraseña (una vez por teléfono)
    App->>API: POST /auth/apoderado/login
    API->>DB: SELECT apoderado (bcrypt)
    API-->>App: JWT {rol: apoderado} + JWT {rol: dispositivo, 30 días}
    App->>App: guarda el JWT de dispositivo en expo-secure-store
    App->>A: pantalla de acceso: perfil del estudiante o panel<br/>(si la cuenta es nueva, antes crea el perfil)

    E->>App: toca su perfil
    App->>API: POST /auth/dispositivo/estudiante (JWT de dispositivo)
    API-->>App: JWT {rol: estudiante, sub: id del estudiante de la cuenta}

    A->>App: "Soy el apoderado" + PIN de 4 números
    App->>API: POST /auth/dispositivo/apoderado {pin} (JWT de dispositivo)
    API->>DB: SELECT apoderado
    alt bloqueado_hasta > ahora
        API-->>App: 423 "Espera un momento e intenta otra vez"
    else PIN correcto (bcrypt)
        API->>DB: UPDATE pin_fallos = 0
        API-->>App: JWT {rol: apoderado, 60 min}
    else PIN incorrecto
        API->>DB: UPDATE pin_fallos + 1 (≥ 5 → bloqueado_hasta = ahora + 5 min)
        API-->>App: 401
    end
```

## 3. F1 — Servir ejercicio (sin LLM)

```mermaid
sequenceDiagram
    autonumber
    actor E as Estudiante
    participant App as App Android
    participant O as OrquestadorPedagogico
    participant M as MotorAdaptativo
    participant B as BancoEjercicios
    participant DB as PostgreSQL

    E->>App: toca una unidad
    App->>O: POST /estudiante/unidades/{unidad}/ejercicio
    O->>M: nivelPara(estudiante, unidad)
    M->>DB: SELECT dominio_oa
    alt primera vez en la unidad
        M->>DB: INSERT dominio_oa (índice 0,5, nivel 2)
    end
    M-->>O: nivel
    O->>B: servir(estudiante, unidad, nivel)
    B->>DB: ejercicio activo no visto de la celda (o el visto hace más tiempo)
    B-->>O: Ejercicio
    O->>DB: INSERT ejercicio_servido (en_curso)
    O-->>App: EjercicioParaEstudiante (sin respuestaFinal ni solución)
    App-->>E: enunciado + figura SVG + teclado según el formato
```

## 4. F2 — Responder: correcta e incorrecta (incluye F6)

```mermaid
sequenceDiagram
    autonumber
    actor E as Estudiante
    participant App as App Android
    participant O as OrquestadorPedagogico
    participant C as Corrector
    participant G as Gamificacion
    participant M as MotorAdaptativo
    participant A as AdaptadorLLM
    participant F as FiltroNoRevelacion
    participant P as PlantillasLocales
    participant DB as PostgreSQL
    participant LLM as OpenAI

    E->>App: escribe la respuesta y toca "Revisar"
    App->>O: POST /estudiante/servidos/{id}/respuestas {respuesta, tiempo}
    O->>C: corregir(respuesta, ejercicio)
    alt respuesta no parseable
        O-->>App: formato_invalido (no cuenta como intento)
    else correcta
        O->>G: puntosPor(intento, nivel)
        O->>DB: INSERT intento · UPDATE servido = resuelto · UPDATE puntaje
        O->>M: registrarIntento(intento)
        M->>DB: UPDATE dominio_oa (índice, racha, nivel)
        O->>P: refuerzo(banda, logro)
        O-->>App: correcta + refuerzo + puntos + cambioNivel
    else incorrecta
        O->>DB: INSERT intento · UPDATE servido.fallos + 1
        O->>M: registrarIntento(intento)
        M->>DB: UPDATE dominio_oa
        O->>A: generarRetroalimentacion(ejercicio, solución, respuesta, patrón, banda)
        alt LLM disponible y bajo el tope
            A->>LLM: prompt (solo contenido matemático)
            LLM-->>A: texto
            A->>DB: INSERT llamada_llm
            A-->>O: texto
            O->>F: revela(texto, ejercicio)
            alt revela la respuesta
                O->>DB: INSERT evento_filtro
                O->>P: errorSinLLM(ejercicio, patrón)
            end
        else circuito abierto, timeout o tope alcanzado (F6)
            A-->>O: degradado
            O->>P: errorSinLLM(ejercicio, patrón) + aviso
        end
        O-->>App: incorrecta + mensaje + ofreceResolverJuntos (si fallos ≥ 3)
    end
    App-->>E: Octavio responde
```

La ruta de respuesta correcta no llama al LLM (`modelo_pedagogico.md` §3). El alias se inserta en el servidor después del filtro, en el marcador `{nombre}` (`estrategia_llm.md` §4).

## 5. F3 — Pedir pista

```mermaid
sequenceDiagram
    autonumber
    actor E as Estudiante
    participant App as App Android
    participant O as OrquestadorPedagogico
    participant A as AdaptadorLLM
    participant F as FiltroNoRevelacion
    participant DB as PostgreSQL

    E->>App: toca "Pista"
    App->>O: POST /estudiante/servidos/{id}/pistas
    alt ya usó 3 pistas o el ejercicio no está en curso
        O-->>App: 409 (el botón ya estaba deshabilitado)
    else
        O->>DB: UPDATE servido.pistas_usadas + 1
        O->>A: generarPista(pista almacenada n, banda, pistas vistas)
        alt LLM disponible
            A-->>O: pista reformulada
            O->>F: revela(pista, ejercicio)
            opt revela
                O->>DB: INSERT evento_filtro
                Note over O: se usa la pista almacenada
            end
        else degradado
            A-->>O: degradado
            Note over O: se usa la pista almacenada tal cual
        end
        O-->>App: pista + pistasRestantes
    end
```

El descuento de la pista se aplica al responder: `intento.pistas_usadas` copia el contador del ejercicio servido y lo usan `Gamificacion` y `MotorAdaptativo` (`modelo_estudiante.md` §1).

## 6. Resolver juntos (RF-P7)

```mermaid
sequenceDiagram
    autonumber
    actor E as Estudiante
    participant App as App Android
    participant O as OrquestadorPedagogico
    participant A as AdaptadorLLM
    participant B as BancoEjercicios
    participant DB as PostgreSQL

    Note over App: tras el 3er fallo aparece "¿Lo resolvemos juntos?"
    E->>App: acepta
    App->>O: POST /estudiante/servidos/{id}/resolver-juntos
    O->>O: verifica fallos ≥ 3
    O->>A: narrarExplicacionGuiada(solución de referencia, banda)
    A-->>O: pasos narrados (o los pasos tal cual si está degradado)
    O->>DB: UPDATE servido = explicado (sin penalizar más)
    O->>B: analogo(ejercicio)
    B-->>O: ejercicio de la misma celda
    O->>DB: INSERT ejercicio_servido (analogo_de = original)
    O-->>App: pasos + EjercicioParaEstudiante del análogo
    App-->>E: pasos con "siguiente →" y luego el ejercicio análogo
```

Durante la narración el filtro deja pasar los pasos intermedios del ejercicio original, pero sigue bloqueando la respuesta del análogo (`modelo_pedagogico.md` §6).

## 7. F4 — Dashboard del apoderado (sin LLM)

```mermaid
sequenceDiagram
    autonumber
    actor P as Apoderado
    participant App as App Android
    participant D as ServicioDashboard
    participant M as MotorAdaptativo
    participant DB as PostgreSQL

    P->>App: entra como apoderado
    App->>D: GET /apoderado/dashboard
    D->>DB: resumen semanal (intento, sesion)
    D->>M: bandas y marca "para repasar" (dominio_oa)
    D->>DB: unidades con más errores o más pistas
    D->>D: sugerencias por reglas
    D-->>App: resumen, medidores, unidades difíciles, sugerencias
    App-->>P: panel (distribución según tamaño y orientación)
```

## 8. F5 — Reposición del banco (asíncrono)

```mermaid
sequenceDiagram
    autonumber
    participant J as ReposicionBanco (APScheduler)
    participant B as BancoEjercicios
    participant GP as GeneradorParametrico
    participant A as AdaptadorLLM
    participant V as PipelineVerificacion
    participant DB as PostgreSQL
    participant LLM as OpenAI
    actor R as Revisor

    J->>DB: pg_try_advisory_lock (un solo ejecutor)
    J->>B: celdasConStockBajo()
    loop cada celda con < 5 activos
        alt la unidad tiene plantilla paramétrica aprobada
            J->>GP: instanciar(plantilla, nivel)
            GP-->>J: ejercicio correcto por construcción
            J->>DB: INSERT ejercicio (activo)
        else problema verbal
            J->>A: generarEjercicio(unidad, nivel, ejemplo gold)
            A->>LLM: structured output
            LLM-->>A: JSON del ejercicio
            opt unidad de fracciones (RF-D6)
                J->>A: generarEjercicio (2ª pasada independiente)
            end
            J->>V: verificarAritmetica + verificarForma
            alt falla capa 1 o 2
                J->>DB: INSERT ejercicio (descartado, motivo)
            else pasa
                J->>V: triaje(ejercicio)
                J->>DB: INSERT ejercicio (verificado, ok | dudoso)
            end
        end
    end
    Note over R,DB: más tarde, CU-14 por CLI
    R->>DB: revisa los verificados (dudosos primero) → activo o descartado
```

Si el Adaptador está degradado o sin presupuesto, el lote verbal se pospone al siguiente ciclo y el banco sigue sirviendo lo que tiene (`estrategia_llm.md` §3).
