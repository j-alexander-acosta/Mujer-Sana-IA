#!/bin/bash

# Script de inicio para la aplicación CPC-28
echo "🚀 Iniciando aplicación CPC-28..."
echo ""

# Verificar si Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 no está instalado"
    exit 1
fi

# Verificar si pip está instalado
if ! command -v pip3 &> /dev/null; then
    echo "❌ Error: pip3 no está instalado"
    exit 1
fi

# Instalar dependencias si es necesario
echo "📦 Verificando dependencias..."
pip3 install -q -r requirements.txt

# Crear directorio de respuestas si no existe
mkdir -p respuestas

# Iniciar servidor
echo ""
echo "✅ Iniciando servidor Flask..."
echo "🌐 La aplicación estará disponible en: http://localhost:5000"
echo "📱 Para acceder desde otro dispositivo, usa: http://[TU-IP]:5000"
echo ""
echo "Presiona Ctrl+C para detener el servidor"
echo ""

python3 app.py








