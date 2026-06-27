#!/usr/bin/env python3
"""
Worker RQ para escalado horizontal (opcional).

La API encola en Redis cuando defines REDIS_URL; uno o más de estos workers
consumen la cola y ejecutan el render determinista. El estado del job se guarda
en un hash de Redis (`job:<job_id>`), que la API también puede leer.

Arranque:
    REDIS_URL=redis://localhost:6379/0 python worker.py
    # o varios en paralelo (N workers = N renders simultáneos)
"""
from __future__ import annotations

import json
import os

from redis import Redis
from rq import Queue, SimpleWorker

from engine import Engine

REDIS_URL = os.environ["REDIS_URL"]
_redis = Redis.from_url(REDIS_URL)
_eng = Engine()


def render_job(problem_id: str, job_id: str) -> dict:
    """Tarea ejecutada por el worker: render determinista + estado en Redis."""
    _set_status(job_id, {"status": "running", "problem_id": problem_id})
    result = _eng.render(problem_id)
    state = {
        "job_id": job_id,
        "problem_id": problem_id,
        "status": "done" if result.ok else "error",
        "video_url": "/" + result.video_path if result.ok else "",
        "sha256": result.sha256,
        "size_bytes": result.size_bytes,
        "error": "" if result.ok else (result.log_tail or "render falló"),
    }
    _set_status(job_id, state)
    return state


def _set_status(job_id: str, state: dict) -> None:
    _redis.set(f"job:{job_id}", json.dumps(state, ensure_ascii=False), ex=86400)


if __name__ == "__main__":
    q = Queue("renders", connection=_redis)
    SimpleWorker([q], connection=_redis).work()
