#!/bin/bash

# =================================================================
# Script de Despliegue Automático - Mujer Sana IA
# =================================================================
# Este script está diseñado para ejecutarse dentro del servidor AWS
# para actualizar la aplicación a la última versión de GitHub.

# Configuración (Detección automática de la carpeta del proyecto)
if [ -d "/home/ubuntu/mujersanaia" ]; then
    APP_DIR="/home/ubuntu/mujersanaia"
elif [ -d "/home/ubuntu/Mujer-Sana-IA" ]; then
    APP_DIR="/home/ubuntu/Mujer-Sana-IA"
else
    APP_DIR=$(pwd)
fi

VENV_DIR="$APP_DIR/venv"
SERVICE_NAME="mujersana" # Nombre del servicio systemd

echo "----------------------------------------------------"
echo "🚀 Iniciando proceso de despliegue..."
echo "----------------------------------------------------"

# 1. Navegar al directorio del proyecto
cd $APP_DIR || { echo "❌ Error: No se encontró el directorio $APP_DIR"; exit 1; }

# 2. Obtener cambios de GitHub
echo "🔄 Obteniendo cambios de GitHub (main)..."
git fetch origin main
git reset --hard origin main

# 3. Activar entorno virtual e instalar dependencias
if [ -d "$VENV_DIR" ]; then
    echo "📦 Actualizando dependencias en el entorno virtual..."
    source $VENV_DIR/bin/activate
    pip install -r requirements.txt
else
    echo "⚠️ Advertencia: No se encontró el entorno virtual en $VENV_DIR"
    echo "Intentando instalar dependencias con pip3 global..."
    pip3 install -r requirements.txt
fi

# 4. Crear directorios necesarios (por si acaso)
mkdir -p respuestas

# 5. Reiniciar el servicio de la aplicación
echo "🔄 Reiniciando el servidor de la aplicación..."

# Intentar reiniciar vía systemctl (método recomendado para producción)
if systemctl is-active --quiet $SERVICE_NAME; then
    sudo systemctl restart $SERVICE_NAME
    echo "✅ Servicio $SERVICE_NAME reiniciado con éxito."
else
    # Si no es un servicio, intentar matar el proceso gunicorn anterior y reiniciar
    echo "⚠️ El servicio $SERVICE_NAME no está activo. Intentando reinicio manual..."
    pkill -9 gunicorn
    sleep 2
    # Iniciar usando la configuración existente y el venv si existe
    if [ -f "$VENV_DIR/bin/gunicorn" ]; then
        $VENV_DIR/bin/gunicorn --bind 0.0.0.0:5000 app:app &
    else
        gunicorn --bind 0.0.0.0:5000 app:app &
    fi
    echo "✅ Gunicorn iniciado manualmente en segundo plano."
fi

echo "----------------------------------------------------"
echo "🎉 Despliegue completado con éxito."
echo "🌐 Revisa: https://mujersanaia.duckdns.org/admin/descargar-csv-anonimizado"
echo "----------------------------------------------------"
