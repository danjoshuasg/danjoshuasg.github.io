# Arquitectura del backend

## Principio rector

**El estado vive en los datos, no en el proceso.** Un problema es un registro
declarativo (`problems.json`); el render es una función pura de ese registro más
un perfil fijo (resolución, fps, flags, entorno). Esto hace el sistema:

- **Determinista** — misma entrada ⇒ mismo MP4 (verificable por hash).
- **Idempotente** — re-pedir un render ya hecho devuelve el mismo artefacto.
- **Cacheable** — la clave de caché es `hash(escena + perfil)`.

## Vista de alto nivel

```
┌──────────┐     POST /renders          ┌──────────────┐
│ Cliente  │ ─────────────────────────▶ │   API (REST) │
│ (web/app)│ ◀───────────────────────── │  FastAPI     │
└──────────┘     202 + job_id           └──────┬───────┘
                                                │ encola
                                          ┌─────▼──────┐
                                          │   Cola     │  (Redis / SQS)
                                          └─────┬──────┘
                                                │ consume
                                   ┌────────────▼─────────────┐
                                   │   Worker de render        │
                                   │  ┌─────────────────────┐  │
                                   │  │ engine.Engine        │  │
                                   │  │  · carga manifiesto  │  │
                                   │  │  · manim --qh ...    │  │
                                   │  │  · sha256 del MP4    │  │
                                   │  └─────────────────────┘  │
                                   └───────┬──────────┬────────┘
                                           │          │
                                    sube MP4│          │metadatos
                                    ┌───────▼───┐  ┌───▼──────────┐
                                    │  Storage  │  │   Base de    │
                                    │ (S3/R2/   │  │   datos      │
                                    │  GH Pages)│  │ (jobs+hashes)│
                                    └───────────┘  └──────────────┘
```

## Capas

### 1. API (sin estado)
- Recibe la petición, valida contra el [esquema](PROBLEM_SCHEMA.md), crea un `job`.
- Responde `202 Accepted` con `job_id` y un enlace de estado.
- Si el `(scene, profile)` ya fue renderizado (hash conocido), responde `200` con
  la URL cacheada — sin re-render.

### 2. Cola
- Desacopla la petición del trabajo pesado (un render tarda segundos/minutos).
- Permite reintentos, prioridad (2D rápido vs 3D lento) y back-pressure.
- Tecnologías: Redis + RQ/Celery, o SQS + workers.

### 3. Worker de render
- Contenedor con **toda** la cadena: Manim, ffmpeg, LaTeX, Cairo/Pango.
- Ejecuta `engine.Engine.render(id)` (el mismo código que el CLI).
- Aísla cada job (cwd temporal) y sube el MP4 + el hash.
- Escala horizontalmente: N workers = N renders en paralelo.

### 4. Almacenamiento
- **Objetos**: los MP4 en S3 / Cloudflare R2 / GitHub Pages (este repo).
- **Metadatos**: tabla `renders(id, scene, profile_hash, sha256, url, bytes, created_at)`.
- La URL pública es estable y versionada por hash.

## Determinismo como contrato

El worker SIEMPRE fija el entorno (`PYTHONHASHSEED=0`, `TZ=UTC`, `--disable_caching`)
y registra el `sha256`. Un job de **CI** corre `engine.py verify` tras cada cambio:
si un hash cambió sin que cambiara la escena, es un regresión a investigar.
Ver [`RENDERING_PIPELINE.md`](RENDERING_PIPELINE.md) para los detalles y límites.

## Por qué no generar la escena con un LLM en tiempo de request

La **lógica visual** (la clase `Scene`) se versiona en git y se revisa como código.
Un LLM puede *proponer* una nueva escena (paso de autoría), pero el render en
producción ejecuta solo código auditado y determinista. Así se separa la
creatividad (offline, revisable) de la ejecución (online, reproducible).
