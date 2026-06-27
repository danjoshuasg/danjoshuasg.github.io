#!/usr/bin/env python3
"""
API REST para el motor determinista de render Manim.

Dos modos, sin cambiar el código:
  - Standalone (por defecto): los renders corren en un ThreadPoolExecutor.
    Ideal para un solo nodo / demo. No requiere Redis.
  - Escalado (si defines REDIS_URL): encola en RQ y los procesa `worker.py`.

Arranque:
    uvicorn api:app --host 0.0.0.0 --port 8000
    # con cola:
    REDIS_URL=redis://localhost:6379/0 uvicorn api:app --port 8000

Endpoints:
    GET  /healthz
    GET  /problems
    GET  /problems/{id}
    POST /renders            {"id": "uni-p30"}
    GET  /renders/{job_id}
    GET  /media/...          (sirve los MP4 generados)
"""
from __future__ import annotations

import hashlib
import os
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass, field
from pathlib import Path
from threading import Lock

from fastapi import FastAPI, HTTPException, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from engine import Engine, ROOT

eng = Engine()
app = FastAPI(title="Manim UNI · API de render", version="1.0")

REDIS_URL = os.environ.get("REDIS_URL")  # si está, usa RQ; si no, threadpool
_POOL = ThreadPoolExecutor(max_workers=int(os.environ.get("RENDER_WORKERS", "2")))


# --------------------------------------------------------------------------- #
#  Almacén de jobs en memoria (suficiente para un nodo). Para multi-nodo,      #
#  el estado vive en Redis vía RQ (ver worker.py).                             #
# --------------------------------------------------------------------------- #
@dataclass
class Job:
    job_id: str
    problem_id: str
    status: str = "queued"          # queued | running | done | error
    video_url: str = ""
    sha256: str = ""
    size_bytes: int = 0
    error: str = ""
    cache_key: str = ""


_JOBS: dict[str, Job] = {}
_BY_KEY: dict[str, str] = {}        # cache_key -> job_id (idempotencia)
_LOCK = Lock()


def _cache_key(pid: str) -> str:
    """Clave de caché: contenido de la escena + clase + perfil de render."""
    p = eng.get(pid)
    scene_bytes = (ROOT / p["scene_file"]).read_bytes()
    h = hashlib.sha256()
    h.update(scene_bytes)
    h.update(p["scene_class"].encode())
    h.update(repr(sorted(eng.profile.items())).encode())
    return h.hexdigest()


def _video_url(rel_path: str) -> str:
    # rel_path viene como "media/videos/.../X.mp4"
    return "/" + rel_path.replace("\\", "/")


def _run_job(job_id: str) -> None:
    with _LOCK:
        job = _JOBS[job_id]
        job.status = "running"
    try:
        result = eng.render(job.problem_id)
        with _LOCK:
            if result.ok:
                job.status = "done"
                job.video_url = _video_url(result.video_path)
                job.sha256 = result.sha256
                job.size_bytes = result.size_bytes
            else:
                job.status = "error"
                job.error = result.log_tail or "render falló"
    except Exception as exc:  # noqa: BLE001
        with _LOCK:
            job.status = "error"
            job.error = str(exc)


# ------------------------------- modelos ----------------------------------- #
class RenderReq(BaseModel):
    id: str


# ------------------------------- rutas ------------------------------------- #
@app.get("/healthz")
def healthz():
    return {"status": "ok", "engine": eng.manifest["engine"],
            "queue": "redis" if REDIS_URL else "threadpool"}


@app.get("/problems")
def problems():
    return [eng.get(i) for i in eng.list_ids()]


@app.get("/problems/{pid}")
def problem(pid: str):
    try:
        return eng.get(pid)
    except KeyError:
        raise HTTPException(404, "problema no encontrado")


@app.post("/renders")
def create_render(req: RenderReq, response: Response):
    try:
        eng.get(req.id)
    except KeyError:
        raise HTTPException(404, "problema no encontrado")

    key = _cache_key(req.id)
    with _LOCK:
        # idempotencia: si ya hay un job con la misma clave, reutilízalo
        if key in _BY_KEY:
            existing = _JOBS[_BY_KEY[key]]
            if existing.status in ("queued", "running", "done"):
                # 200 si ya terminó (cache hit), 202 si sigue en curso
                response.status_code = 200 if existing.status == "done" else 202
                return _body(existing)

        job = Job(job_id=f"r_{uuid.uuid4().hex[:10]}", problem_id=req.id, cache_key=key)
        _JOBS[job.job_id] = job
        _BY_KEY[key] = job.job_id

    if REDIS_URL:
        _enqueue_rq(job)            # escalado horizontal
    else:
        _POOL.submit(_run_job, job.job_id)
    response.status_code = 202
    return _body(job)


@app.get("/renders/{job_id}")
def get_render(job_id: str):
    job = _JOBS.get(job_id)
    if not job:
        raise HTTPException(404, "job no encontrado")
    return _body(job)


def _body(job: Job) -> dict:
    out = {k: v for k, v in asdict(job).items() if k != "cache_key"}
    out["status_url"] = f"/renders/{job.job_id}"
    return out


def _enqueue_rq(job: Job) -> None:
    """Encola en RQ cuando hay REDIS_URL (lo procesa worker.py)."""
    from redis import Redis
    from rq import Queue

    q = Queue("renders", connection=Redis.from_url(REDIS_URL))
    q.enqueue("worker.render_job", job.problem_id, job.job_id, job_id=job.job_id)


# Sirve los MP4 generados (en producción: detrás de CDN / object storage)
_media = ROOT / "media"
_media.mkdir(exist_ok=True)
app.mount("/media", StaticFiles(directory=str(_media)), name="media")
