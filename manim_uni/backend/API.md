# API REST (diseño de referencia)

Servicio sin estado sobre `engine.Engine`. Sugerido: **FastAPI**.
Los renders son asíncronos (un job pesado), con caché por hash.

## Endpoints

### `GET /problems`
Lista los problemas registrados.
```json
[
  { "id": "uni-p30", "dimension": "2D", "topic": "Áreas · Tangencia",
    "answer": { "clave": "D", "valor": "5√6 m" } }
]
```

### `GET /problems/{id}`
Detalle de un problema (el registro del manifiesto).

### `POST /renders`
Encola un render. Idempotente por `(id, profile)`.
```jsonc
// request
{ "id": "uni-p30" }

// 202 Accepted  (nuevo job)
{ "job_id": "r_a1b2c3", "status": "queued", "status_url": "/renders/r_a1b2c3" }

// 200 OK  (cache hit: ya existe ese hash)
{ "status": "done", "video_url": "https://.../PreguntaUNI30.mp4",
  "sha256": "23f4da11…" }
```

### `GET /renders/{job_id}`
Estado del job.
```json
{ "job_id": "r_a1b2c3", "status": "done",
  "video_url": "https://.../PreguntaUNI30.mp4",
  "sha256": "23f4da11bf8ecc46…", "size_bytes": 879878,
  "started_at": "…", "finished_at": "…" }
```
`status ∈ { queued, running, done, error }`.

## Implementación de referencia (FastAPI)

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from engine import Engine

app = FastAPI(title="Manim UNI render API")
eng = Engine()

class RenderReq(BaseModel):
    id: str

@app.get("/problems")
def problems():
    return [eng.get(i) for i in eng.list_ids()]

@app.get("/problems/{pid}")
def problem(pid: str):
    try:
        return eng.get(pid)
    except KeyError:
        raise HTTPException(404, "problema no encontrado")

@app.post("/renders", status_code=202)
def create_render(req: RenderReq):
    try:
        eng.get(req.id)
    except KeyError:
        raise HTTPException(404, "problema no encontrado")
    job_id = enqueue(req.id)            # -> Redis/Celery; el worker llama eng.render(id)
    return {"job_id": job_id, "status": "queued",
            "status_url": f"/renders/{job_id}"}

@app.get("/renders/{job_id}")
def get_render(job_id: str):
    return job_status(job_id)           # consulta a la cola/DB
```

El worker (fuera de la API) ejecuta el trabajo:
```python
def work(job_id, pid):
    r = eng.render(pid)                 # determinista
    url = upload(r.video_path)          # S3 / R2 / GH Pages
    save(job_id, status="done", url=url, sha256=r.sha256, bytes=r.size_bytes)
```

## Notas

- **Auth**: API key por cliente; rate-limit por `id` (los 3D son caros).
- **Versionado**: incluir el `engine`/`profile_hash` en la URL del MP4 para
  poder convivir con re-renders de otra versión sin romper enlaces viejos.
- **Webhooks**: opcional `POST {callback_url}` al terminar el job.
