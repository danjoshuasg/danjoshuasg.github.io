#!/usr/bin/env python3
"""
Motor determinista de renderizado de animaciones UNI con Manim.

Idea central: *misma entrada -> mismo video*. El estado (qué problema, qué
escena, qué perfil de render) vive en `problems.json`; este módulo solo lo
ejecuta de forma reproducible y registra un manifiesto de salida con hashes.

Por qué es determinista:
  - La escena Manim no usa aleatoriedad ni reloj (sin random / time).
  - Se fija PYTHONHASHSEED=0 y TZ=UTC.
  - Se renderiza con --disable_caching y resolución/fps fijos del perfil.
  - Se calcula SHA-256 de cada MP4 para detectar cualquier desviación.

Uso (CLI):
    python engine.py list
    python engine.py render uni-p30
    python engine.py render-all
    python engine.py verify            # re-renderiza y compara hashes

Uso (librería):
    from engine import Engine
    eng = Engine()
    result = eng.render("uni-p30")
    print(result.video_path, result.sha256)
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from dataclasses import dataclass, asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "problems.json"
OUTPUT_MANIFEST = ROOT / "render_manifest.json"
# Permite override del binario de manim (p. ej. el del venv).
MANIM_BIN = os.environ.get("MANIM_BIN", "manim")


@dataclass
class RenderResult:
    id: str
    scene_file: str
    scene_class: str
    video_path: str
    sha256: str
    size_bytes: int
    ok: bool
    log_tail: str = ""


def _load_manifest() -> dict:
    with open(MANIFEST, encoding="utf-8") as fh:
        return json.load(fh)


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _deterministic_env(profile: dict) -> dict:
    env = os.environ.copy()
    env.update(profile.get("env", {}))
    env.setdefault("PYTHONHASHSEED", "0")
    env.setdefault("TZ", "UTC")
    return env


class Engine:
    """Ejecuta el manifiesto de problemas de forma determinista."""

    def __init__(self, manifest: dict | None = None):
        self.manifest = manifest or _load_manifest()
        self.profile = self.manifest["render_profile"]
        self.problems = {p["id"]: p for p in self.manifest["problems"]}

    # ---- consultas ----
    def list_ids(self) -> list[str]:
        return list(self.problems)

    def get(self, pid: str) -> dict:
        if pid not in self.problems:
            raise KeyError(f"Problema desconocido: {pid!r}. Disponibles: {self.list_ids()}")
        return self.problems[pid]

    def expected_video(self, pid: str) -> Path:
        """Ruta canónica del MP4 que produce Manim para esta escena."""
        p = self.get(pid)
        res = self.profile["resolution"].split("x")[1] + "p" + str(self.profile["fps"])
        stem = Path(p["scene_file"]).stem
        return ROOT / "media" / "videos" / stem / res / f"{p['scene_class']}.mp4"

    # ---- render ----
    def render(self, pid: str) -> RenderResult:
        p = self.get(pid)
        scene_path = ROOT / p["scene_file"]
        cmd = [MANIM_BIN, self.profile["quality"], *self.profile["flags"],
               str(scene_path), p["scene_class"]]
        proc = subprocess.run(
            cmd, cwd=ROOT, env=_deterministic_env(self.profile),
            capture_output=True, text=True,
        )
        video = self.expected_video(pid)
        ok = proc.returncode == 0 and video.exists()
        return RenderResult(
            id=pid,
            scene_file=p["scene_file"],
            scene_class=p["scene_class"],
            video_path=str(video.relative_to(ROOT)) if video.exists() else "",
            sha256=_sha256(video) if video.exists() else "",
            size_bytes=video.stat().st_size if video.exists() else 0,
            ok=ok,
            log_tail="\n".join((proc.stderr or proc.stdout).splitlines()[-6:]),
        )

    def render_all(self) -> list[RenderResult]:
        return [self.render(pid) for pid in self.list_ids()]

    def write_output_manifest(self, results: list[RenderResult]) -> Path:
        data = {
            "engine": self.manifest["engine"],
            "render_profile": self.profile,
            "renders": [asdict(r) for r in results],
        }
        with open(OUTPUT_MANIFEST, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
        return OUTPUT_MANIFEST

    def verify(self) -> bool:
        """Re-renderiza y compara contra el manifiesto de salida previo."""
        if not OUTPUT_MANIFEST.exists():
            print("No hay render_manifest.json previo; ejecuta 'render-all' primero.")
            return False
        prev = {r["id"]: r["sha256"] for r in json.load(open(OUTPUT_MANIFEST))["renders"]}
        all_ok = True
        for r in self.render_all():
            before = prev.get(r.id, "")
            same = before == r.sha256 and r.ok
            flag = "OK " if same else "DIFF"
            print(f"[{flag}] {r.id}  {before[:12]} -> {r.sha256[:12]}")
            all_ok = all_ok and same
        return all_ok


def _main(argv: list[str]) -> int:
    eng = Engine()
    cmd = argv[1] if len(argv) > 1 else "list"

    if cmd == "list":
        for pid in eng.list_ids():
            p = eng.get(pid)
            ans = p["answer"]
            clave = f"clave {ans['clave']}" if ans.get("clave") else "—"
            print(f"  {pid:16s} [{p['dimension']}] {p['source']['topic']:32s} {clave}: {ans['valor']}")
        return 0

    if cmd == "render":
        if len(argv) < 3:
            print("Uso: engine.py render <id>")
            return 2
        r = eng.render(argv[2])
        print(json.dumps(asdict(r), ensure_ascii=False, indent=2))
        return 0 if r.ok else 1

    if cmd == "render-all":
        results = eng.render_all()
        out = eng.write_output_manifest(results)
        for r in results:
            print(f"[{'OK ' if r.ok else 'ERR'}] {r.id:16s} {r.sha256[:16]}  {r.size_bytes:>9d} B")
        print(f"\nManifiesto de salida -> {out.relative_to(ROOT)}")
        return 0 if all(r.ok for r in results) else 1

    if cmd == "verify":
        return 0 if eng.verify() else 1

    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv))
