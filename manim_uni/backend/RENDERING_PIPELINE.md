# Pipeline de render y garantías de determinismo

## Etapas

```
problems.json ──▶ engine.Engine.render(id)
                      │
                      ├─ 1. resuelve (scene_file, scene_class, profile)
                      ├─ 2. fija entorno: PYTHONHASHSEED=0, TZ=UTC
                      ├─ 3. ejecuta:  manim -qh --disable_caching <file> <Class>
                      │        │
                      │        ├─ Manim construye los Mobjects (geometría exacta)
                      │        ├─ LaTeX → dvisvgm → SVG  (fórmulas)
                      │        ├─ Cairo/Pango rasteriza cada frame (PNG)
                      │        └─ ffmpeg ensambla los frames → MP4 (libx264)
                      │
                      ├─ 4. localiza el MP4 canónico (media/videos/<stem>/<res>/<Class>.mp4)
                      └─ 5. calcula SHA-256 + tamaño → RenderResult
```

## Qué garantiza el determinismo

| Fuente de no-determinismo | Mitigación |
|---------------------------|------------|
| `random` / `Math.random` | Las escenas **no** lo usan; la geometría es analítica |
| Reloj / fecha (`time`, `datetime.now`) | No se usa; `TZ=UTC` por si acaso |
| Orden de hash de sets/dicts | `PYTHONHASHSEED=0` |
| Caché de Manim (estados previos) | `--disable_caching` siempre |
| Versión de librerías | `engine` pineado (`manim==0.20.1`) |
| Fuentes / LaTeX | Se fija la imagen del worker (mismas fuentes y texlive) |

Con esto, el **contenido visual** (cada frame PNG) es idéntico entre corridas.

## Límite honesto: el contenedor MP4

El *stream de video* (los frames) es determinista, pero el **contenedor MP4**
puede incluir metadatos volátiles (p. ej. `encoder`, timestamps de muxing) que
hacen variar el SHA-256 del archivo entre máquinas/versiones de ffmpeg.

Estrategias para un hash 100 % estable:

1. **Hash del contenido, no del contenedor**: comparar los PNG por frame, o
   re-muxear con flags que limpian metadatos:
   ```bash
   ffmpeg -i in.mp4 -map_metadata -1 -fflags +bitexact \
          -flags:v +bitexact -flags:a +bitexact out.mp4
   ```
2. **Fijar el worker**: misma imagen Docker (misma versión de ffmpeg/x264) ⇒
   mismo MP4 byte a byte. Es la opción recomendada en producción.

`engine.py verify` aplica el criterio práctico: misma imagen/worker ⇒ mismos hashes.

## Reproducibilidad en CI

```yaml
# pseudo-workflow
steps:
  - render-all:  python engine.py render-all      # genera render_manifest.json
  - commit:      git add render_manifest.json
  - on-PR:       python engine.py verify           # re-render y compara hashes
                 # si un hash cambió sin cambiar la escena -> falla el check
```

## Rendimiento (orden de magnitud, 1080p60)

| Escena | Animaciones | Tiempo aprox. | Tamaño |
|--------|-------------|---------------|--------|
| 2D (álgebra/geometría) | ~25–40 | 30–90 s | 0.8–1.7 MB |
| 3D (semiesferas) | ~23 | 60–120 s | ~2.4 MB |

Los 3D y el LaTeX dominan el costo; conviene cola con prioridad y workers
dedicados a 3D.
