#!/bin/bash
set -e  # Exit on error

# Función para limpieza al salir
cleanup() {
    echo "Shutting down application..."
    exit 0
}

# Capturar señales de terminación
trap cleanup SIGTERM SIGINT SIGQUIT

echo "Starting application..."

# Verificar que las variables de entorno necesarias estén definidas
: "${REDIS_URL:?REDIS_URL must be set}"
: "${HOST:?HOST must be set}"
: "${PORT:?PORT must be set}"

# Iniciar la aplicación
exec poetry run python src/main.py