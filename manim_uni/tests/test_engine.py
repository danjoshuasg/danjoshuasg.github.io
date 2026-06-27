"""
Tests del motor y la API.

  - Unitarios (rápidos): manifiesto, rutas, escenas importables, API sin render.
  - Integración (lento): renderiza la escena más corta y verifica hash.
    Se omite si no hay binario de manim:  pytest -m "not slow"  para saltarlo.
"""
import importlib.util
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from engine import Engine  # noqa: E402


@pytest.fixture(scope="module")
def eng():
    return Engine()


# ------------------------------- unitarios --------------------------------- #
def test_manifiesto_carga(eng):
    assert eng.manifest["engine"].startswith("manim")
    assert len(eng.list_ids()) >= 1


def test_ids_unicos(eng):
    ids = eng.list_ids()
    assert len(ids) == len(set(ids))


def test_perfil_render(eng):
    p = eng.profile
    assert p["fps"] == 60
    assert "--disable_caching" in p["flags"]
    assert p["env"]["PYTHONHASHSEED"] == "0"


def test_ruta_video_canonica(eng):
    v = eng.expected_video("uni-p30")
    assert v.name == "PreguntaUNI30.mp4"
    assert "1080p60" in str(v)


def test_escenas_importables_y_clase_existe(eng):
    """Cada (scene_file, scene_class) debe existir y la clase estar definida."""
    for pid in eng.list_ids():
        p = eng.get(pid)
        path = ROOT / p["scene_file"]
        assert path.exists(), f"falta {path}"
        spec = importlib.util.spec_from_file_location(path.stem, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        assert hasattr(mod, p["scene_class"]), f"{pid}: no existe {p['scene_class']}"


def test_dimension_consistente(eng):
    for pid in eng.list_ids():
        p = eng.get(pid)
        assert p["dimension"] in ("2D", "3D")


def test_get_desconocido_lanza(eng):
    with pytest.raises(KeyError):
        eng.get("no-existe")


# ----------------------------------- API ----------------------------------- #
def test_api_endpoints():
    from fastapi.testclient import TestClient
    import api

    client = TestClient(api.app)
    assert client.get("/healthz").json()["status"] == "ok"
    assert len(client.get("/problems").json()) >= 1
    assert client.get("/problems/uni-p30").json()["id"] == "uni-p30"
    assert client.get("/problems/nope").status_code == 404
    assert client.post("/renders", json={"id": "nope"}).status_code == 404


# ----------------------------- integración (lento) ------------------------- #
@pytest.mark.slow
@pytest.mark.skipif(shutil.which("manim") is None,
                    reason="manim no está en PATH")
def test_render_determinista(eng):
    """Renderiza la escena más corta dos veces y compara el hash."""
    pid = "uni-2024-p31"
    r1 = eng.render(pid)
    assert r1.ok and len(r1.sha256) == 64
    r2 = eng.render(pid)
    assert r1.sha256 == r2.sha256, "el render no fue determinista en esta máquina"
