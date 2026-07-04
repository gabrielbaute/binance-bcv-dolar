# ==========================================
# Etapa 0: Builder Frontend (TypeScript -> Bundle)
# ==========================================
FROM node:20-alpine AS ui-builder

WORKDIR /app

ARG VCS_REF=local
ARG BUILD_DATE=unknown

COPY package.json tsconfig.json ./
RUN npm install
COPY app/ui/src ./app/ui/src
COPY app/ui/static ./app/ui/static
RUN echo "ui-build-ref=${VCS_REF} ui-build-date=${BUILD_DATE}" > /tmp/ui-build-info.txt
RUN npm run build:ui

# ==========================================
# Etapa 1: Constructor (Builder Nativo con uv)
# ==========================================
FROM python:3.11-slim AS builder

# Evitar la generación de archivos .pyc en la etapa de compilación
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Extraer el binario de 'uv' directamente desde la imagen oficial
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Sincronización de dependencias usando la caché nativa de uv y montajes eficientes
# Nota: Si el proyecto usa un requirements.txt clásico en lugar de pyproject.toml, 
# se puede cambiar por: uv pip compile / uv pip install. Asumimos el estándar moderno de uv.
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    uv sync --frozen --no-install-project --no-dev

# ==========================================
# Etapa 2: Imagen Final de Producción (Runtime)
# ==========================================
FROM python:3.11-slim AS runtime

# Mantener consistencia con las variables de optimización de python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    LOG_DIR="/logs" \
    INSTANCE_DIR="/instance" \
    API_PORT=8000 \
    API_HOST="0.0.0.0"

# Inyectar el entorno virtual generado directamente al PATH global de ejecución
ENV PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Instalación de utilidades esenciales para producción (curl requerido para el HEALTHCHECK)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario, grupo sin privilegios y directorios de persistencia necesarios
RUN groupadd -r dolar_vzl -g 1000 && \
    useradd -u 1000 -g dolar_vzl -m -s /bin/bash dolar_vzl && \
    mkdir -p /logs /instance && \
    chown -R dolar_vzl:dolar_vzl /logs /instance /app

# Copiar el entorno virtual aislado desde la etapa de compilación
COPY --from=builder --chown=dolar_vzl:dolar_vzl /app/.venv /app/.venv

# Copiar la aplicación garantizando que el usuario no privilegiado sea el dueño
COPY --chown=dolar_vzl:dolar_vzl . .

# Sobrescribir el bundle con la compilacion generada en la etapa frontend
COPY --from=ui-builder --chown=dolar_vzl:dolar_vzl /app/app/ui/static/js/app.js /app/app/ui/static/js/app.js

# Diagnóstico de salud del contenedor usando la ruta asignada
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:${API_PORT}/health || exit 1

# Exponer el puerto de la API configurado
EXPOSE 8000

# Cambiar de forma definitiva al usuario seguro
USER dolar_vzl

# Comando de arranque optimizado invocando directamente uvicorn desde el .venv compartido al PATH
CMD ["sh", "-c", "uvicorn app.main:app --host ${API_HOST} --port ${API_PORT}"]