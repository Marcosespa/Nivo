# Nivo Backend — Dockerfile (Producción / Full Stack)
# Construcción multi-stage para imagen optimizada.
# Instala liboqs C completo para PQC real (ML-KEM-768, ML-DSA-65).
#
# Build:  docker build -t nivo-api .
# Run:    docker run -p 8000:8000 --env-file .env nivo-api

# ── Stage 1: Builder ──────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

# Dependencias del sistema para liboqs y librerías crypto
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    libssl-dev \
    pkg-config \
    git \
    && rm -rf /var/lib/apt/lists/*

# Instalar liboqs C (requerido por liboqs-python para PQC real)
RUN git clone --depth 1 https://github.com/open-quantum-safe/liboqs.git /tmp/liboqs \
    && cd /tmp/liboqs \
    && mkdir build && cd build \
    && cmake -DCMAKE_BUILD_TYPE=Release -DBUILD_SHARED_LIBS=ON .. \
    && make -j$(nproc) \
    && make install \
    && ldconfig \
    && rm -rf /tmp/liboqs

WORKDIR /app

# Instalar dependencias Python en directorio separado
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ── Stage 2: Runtime ──────────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

# Copiar librerías del sistema necesarias en runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    libssl3 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar liboqs C compilado
COPY --from=builder /usr/local/lib/liboqs* /usr/local/lib/
COPY --from=builder /usr/local/include/oqs /usr/local/include/oqs
RUN ldconfig

# Copiar dependencias Python
COPY --from=builder /install /usr/local

WORKDIR /app

# Crear usuario no-root para seguridad
RUN groupadd -r nivo && useradd -r -g nivo nivo
COPY --chown=nivo:nivo . .

USER nivo

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
