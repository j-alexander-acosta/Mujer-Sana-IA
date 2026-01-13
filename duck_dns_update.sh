#!/bin/bash

# Configuración de Duck DNS
# Basado en la imagen enviada por el usuario
DOMAIN="mujersanaia"
TOKEN="0616e421-907b-418b-938d-a160de22b501"

echo "Actualizando Duck DNS para $DOMAIN.duckdns.org..."

# Realizar la actualización
RESPONSE=$(curl -s "https://www.duckdns.org/update?domains=$DOMAIN&token=$TOKEN&ip=")

if [ "$RESPONSE" == "OK" ]; then
    echo "✅ Éxito: IP actualizada correctamente."
else
    echo "❌ Error: No se pudo actualizar la IP. Respuesta: $RESPONSE"
fi
