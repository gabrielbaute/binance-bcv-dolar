# Imagen base
FROM python:3.11-alpine

# Instalar dependencias del sistema y crear usuario no privilegiado
RUN apk add --no-cache curl build-base && \
    addgroup -g 1000 dolar_vzl && \
    adduser -D -s /bin/sh -u 1000 -G dolar_vzl dolar_vzl

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    LOG_DIR="/logs" \
    INSTANCE_DIR="/instance" \
    API_PORT=8000 \
    API_HOST="0.0.0.0"

WORKDIR /app

# Copiar requirements primero para aprovechar cache
COPY requirements.txt ./

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt && rm -rf ~/.cache/pip

# Copiar el resto del proyecto con permisos correctos
COPY --chown=dolar_vzl:dolar_vzl . .

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:${API_PORT}/health || exit 1

# Exponer puerto
EXPOSE 8000

# Cambiar a usuario no privilegiado
USER dolar_vzl

# Comando de arranque con uvicorn
CMD ["sh", "-c", "uvicorn app.main:app --host ${API_HOST} --port ${API_PORT}"]
