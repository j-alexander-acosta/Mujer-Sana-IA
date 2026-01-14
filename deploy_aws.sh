#!/bin/bash

# =================================================================
# Script de Despliegue Automático - Mujer Sana IA
# =================================================================
# Este script está diseñado para ejecutarse dentro del servidor AWS
# para actualizar la aplicación a la última versión de GitHub.

# Configuración (Ajustar si las rutas cambian en AWS)
APP_DIR="/home/ubuntu/mujersanaia"
VENV_DIR="$APP_DIR/.venv"
SERVICE_NAME="gunicorn" # O el nombre de tu servicio systemd

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
    pkill gunicorn
    sleep 2
    # Iniciar usando la configuración existente
    gunicorn -c gunicorn_config.py app:app &
    echo "✅ Gunicorn iniciado manualmente en segundo plano."
fi

echo "----------------------------------------------------"
echo "🎉 Despliegue completado con éxito."
echo "🌐 Revisa: https://mujersanaia.duckdns.org/admin/descargar-csv-anonimizado"
echo "----------------------------------------------------"
