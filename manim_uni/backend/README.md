# Backend de animaciones matemáticas (Manim) — UNI

Motor **determinista** que convierte un *problema de examen* en un **video MP4**
explicativo, renderizado con [Manim Community](https://www.manim.community/).

> Misma entrada ⇒ mismo video. El estado vive en datos (`problems.json`),
> no en el código de ejecución, y cada salida se sella con un hash SHA-256.

## ¿Qué resuelve?

Hoy el flujo es manual: leer el problema → escribir la escena → renderizar →
subir el MP4. Este backend lo formaliza en un servicio reproducible y escalable,
de modo que cualquiera (una API, un cron, un worker) pueda pedir un render y
obtener exactamente el mismo resultado.

## Componentes

| Pieza | Archivo | Rol |
|-------|---------|-----|
| **Manifiesto** | `problems.json` | Fuente de verdad: registro declarativo de problemas y perfil de render |
| **Motor** | `engine.py` | Carga el manifiesto y ejecuta los renders de forma determinista |
| **Escenas** | `uni_*.py` | Una clase `Scene`/`ThreeDScene` por problema (la "lógica visual") |
| **Manifiesto de salida** | `render_manifest.json` | Hashes + tamaños de cada MP4 producido (auditoría) |
| **API** | `api.py` | Servicio REST (FastAPI) sobre el motor |
| **Worker** | `worker.py` | Consumidor RQ para escalado horizontal (opcional) |
| **Imagen** | `Dockerfile`, `docker-compose.yml` | Contenedor con toda la cadena de render |
| **Tests** | `tests/` | Unitarios + integración (render determinista) |

## Documentos

- [`ARCHITECTURE.md`](ARCHITECTURE.md) — arquitectura del servicio (API, cola, workers, almacenamiento)
- [`PROBLEM_SCHEMA.md`](PROBLEM_SCHEMA.md) — esquema del problema y contrato de datos
- [`RENDERING_PIPELINE.md`](RENDERING_PIPELINE.md) — pipeline y garantías de determinismo
- [`API.md`](API.md) — diseño de la API REST

## Inicio rápido

```bash
# dependencias del sistema: ffmpeg, LaTeX (texlive), dvisvgm, cairo, pango
python -m venv .venv && source .venv/bin/activate
pip install manim==0.20.1

# usar el binario de manim del venv
export MANIM_BIN=$(which manim)

python engine.py list            # listar problemas registrados
python engine.py render uni-p30  # renderizar uno (imprime su SHA-256)
python engine.py render-all      # renderizar todos + escribir render_manifest.json
python engine.py verify          # re-render y comparar hashes (reproducibilidad)
```

## Levantar la API

```bash
pip install -r requirements.txt
export MANIM_BIN=$(which manim)
uvicorn api:app --port 8000

# pedir un render y consultar su estado
curl -X POST localhost:8000/renders -H 'Content-Type: application/json' -d '{"id":"uni-p30"}'
curl localhost:8000/renders/<job_id>
```

## Desplegar con Docker (API + Redis + workers)

```bash
docker compose up --build          # API en :8000, 2 workers de render, Redis
# escalar workers: docker compose up --scale worker=4
```

- **Sin cola** (un nodo): `docker build -t manim-uni . && docker run -p 8000:8000 manim-uni`
  → la API usa un ThreadPoolExecutor interno (`RENDER_WORKERS`).
- **Con cola** (multi-nodo): define `REDIS_URL` y corre `worker.py` (lo hace compose).

## Tests

```bash
pytest -m "not slow"   # rápidos (manifiesto, escenas, API)
pytest -m slow         # render real + verificación de hash determinista
```
