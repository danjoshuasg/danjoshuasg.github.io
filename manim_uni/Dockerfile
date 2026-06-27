# Imagen del worker/API: incluye TODA la cadena de render determinista.
# (Fijar esta imagen = mismos binarios = MP4 reproducible byte a byte.)
FROM python:3.11-slim-bookworm

ENV PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=0 \
    TZ=UTC \
    MANIM_BIN=manim \
    DEBIAN_FRONTEND=noninteractive

# Dependencias del sistema:
#   ffmpeg                -> ensamblado de video
#   libcairo2/pango       -> rasterizado de frames
#   texlive + dvisvgm     -> fórmulas LaTeX (MathTex)
#   build-essential, pkg-config -> compilar manimpango
RUN apt-get update && apt-get install -y --no-install-recommends \
        ffmpeg \
        build-essential pkg-config \
        libcairo2-dev libpango1.0-dev \
        texlive-latex-base texlive-latex-extra texlive-fonts-recommended \
        texlive-science dvisvgm \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Por defecto arranca la API (modo standalone). Para el worker:
#   docker run ... python worker.py
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
