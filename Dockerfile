FROM python:3.12-slim

# Configurar variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VERSION=1.7.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false

# Agregar poetry a PATH
ENV PATH="$POETRY_HOME/bin:$PATH"

# Instalar poetry y dependencias del sistema
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && curl -sSL https://install.python-poetry.org | python3 - \
    && apt-get purge -y --auto-remove curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar archivos de configuración
COPY pyproject.toml poetry.lock .env ./
COPY src/ ./src/
COPY start.sh ./

# Convertir line endings y dar permisos
RUN sed -i 's/\r$//' start.sh && \
    chmod +x start.sh

# Instalar dependencias
RUN poetry install --no-dev

CMD ["/bin/bash", "./start.sh"]