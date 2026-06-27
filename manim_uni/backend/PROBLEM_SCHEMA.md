# Esquema del problema (`problems.json`)

El manifiesto es el **contrato de datos** del backend. Un problema es declarativo:
describe *qué* animar, no *cómo* renderizar (eso lo fija `render_profile`).

## Estructura

```jsonc
{
  "version": "1.0",
  "engine": "manim-community-0.20.1",   // versión pineada (reproducibilidad)
  "render_profile": {                    // perfil ÚNICO para todos los renders
    "quality": "-qh",                    // -ql/-qm/-qh/-qk
    "resolution": "1920x1080",
    "fps": 60,
    "flags": ["--disable_caching"],
    "env": { "PYTHONHASHSEED": "0", "TZ": "UTC" }
  },
  "problems": [ /* … registros … */ ]
}
```

## Registro de un problema

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | `string` | Identificador único y estable (clave de caché/URL). p. ej. `uni-p30` |
| `source.exam` | `string` | Examen de origen. p. ej. `"UNI 2024-1"` |
| `source.question` | `int\|null` | Número de pregunta |
| `source.topic` | `string` | Tema (taxonomía: Álgebra, Geometría, …) |
| `statement` | `string` | Enunciado en texto plano (para búsqueda/SEO) |
| `scene_file` | `string` | Archivo Python con la escena (relativo a `manim_uni/`) |
| `scene_class` | `string` | Nombre de la clase `Scene`/`ThreeDScene` a renderizar |
| `dimension` | `"2D"\|"3D"` | Tipo de escena |
| `answer.clave` | `string\|null` | Alternativa correcta (A–E) si aplica |
| `answer.valor` | `string` | Resultado final legible |

## Reglas (invariantes)

1. `id` es **inmutable**: si cambia, es otro problema (rompería URLs/caché).
2. `(scene_file, scene_class)` debe existir y ser renderizable de forma aislada.
3. La escena **no** usa aleatoriedad ni reloj — ver [pipeline](RENDERING_PIPELINE.md).
4. `engine` se pinea: subir de versión es un cambio explícito (los hashes cambian).

## Validación

Antes de aceptar un registro, la API valida:

- JSON Schema (tipos y campos requeridos).
- `id` único en el manifiesto.
- El archivo de escena importa y la clase existe (`importlib`).
- `dimension` consistente (`ThreeDScene` ⇒ `"3D"`).

## Extensiones futuras (sin romper el contrato)

- `i18n`: `statement` por idioma (`es`, `en`).
- `thumbnail`: frame de portada (segundo `t`).
- `prerequisites`: ids de problemas/temas previos (grafo de aprendizaje).
- `variants`: parámetros para generar versiones (p. ej. cambiar el dato 48 → 72).
