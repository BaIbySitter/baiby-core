FROM python:3.9-slim

# Instalar poetry
RUN pip install poetry

WORKDIR /app

# Copiar archivos de configuración
COPY pyproject.toml poetry.lock ./

# Instalar dependencias
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

# Copiar código
COPY . .

CMD ["poetry", "run", "python", "src/main.py"]