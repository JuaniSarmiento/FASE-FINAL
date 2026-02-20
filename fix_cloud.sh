#!/bin/bash
# Script de verificación y corrección para el servidor en la nube
# Ejecutar con: bash fix_cloud.sh

set -e

echo "================================================================"
echo "🔧 CORRECCIÓN DE CONFIGURACIÓN EN LA NUBE"
echo "================================================================"

# 1. Verificar que estamos en el directorio correcto
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Error: docker-compose.yml no encontrado"
    echo "   Por favor ejecuta este script desde el directorio raíz del proyecto"
    exit 1
fi

echo "✅ Directorio correcto"

# 2. Detener servicios
echo ""
echo "🛑 Deteniendo servicios..."
docker-compose down

# 3. Verificar docker-compose.yml
echo ""
echo "🔍 Verificando configuración en docker-compose.yml..."
if grep -q "CHROMA_DB_HOST=chroma" docker-compose.yml; then
    echo "✅ CHROMA_DB_HOST configurado correctamente"
else
    echo "⚠️  CHROMA_DB_HOST no configurado correctamente"
    echo "   Asegúrate de que docker-compose.yml tenga:"
    echo "   - CHROMA_DB_HOST=chroma"
    exit 1
fi

# 4. Limpiar contenedores anteriores
echo ""
echo "🧹 Limpiando contenedores anteriores..."
docker-compose rm -f backend

# 5. Reconstruir backend
echo ""
echo "🔨 Reconstruyendo backend (esto puede tomar unos minutos)..."
docker-compose build --no-cache backend

# 6. Iniciar servicios
echo ""
echo "🚀 Iniciando servicios..."
docker-compose up -d

# 7. Esperar a que los servicios estén listos
echo ""
echo "⏳ Esperando 15 segundos a que los servicios inicien..."
sleep 15

# 8. Verificar estado de servicios
echo ""
echo "📊 Estado de los servicios:"
docker-compose ps

# 9. Verificar variables de entorno en el backend
echo ""
echo "🔍 Verificando variables de entorno en el backend..."
CHROMA_HOST=$(docker exec fase_final_backend printenv CHROMA_DB_HOST 2>/dev/null || echo "ERROR")
CHROMA_PORT=$(docker exec fase_final_backend printenv CHROMA_DB_PORT 2>/dev/null || echo "ERROR")
OLLAMA_URL=$(docker exec fase_final_backend printenv OLLAMA_BASE_URL 2>/dev/null || echo "ERROR")

echo "CHROMA_DB_HOST: $CHROMA_HOST"
echo "CHROMA_DB_PORT: $CHROMA_PORT"
echo "OLLAMA_BASE_URL: $OLLAMA_URL"

if [ "$CHROMA_HOST" != "chroma" ]; then
    echo "❌ ERROR: CHROMA_DB_HOST debería ser 'chroma', pero es: $CHROMA_HOST"
    exit 1
fi

echo "✅ Variables de entorno correctas"

# 10. Verificar conectividad a ChromaDB
echo ""
echo "🔍 Verificando conectividad a ChromaDB..."
if docker exec fase_final_backend curl -s -f http://chroma:8000/api/v1/heartbeat > /dev/null 2>&1; then
    echo "✅ Backend puede conectarse a ChromaDB"
else
    echo "❌ ERROR: Backend NO puede conectarse a ChromaDB"
    echo "   Verificando logs de ChromaDB:"
    docker-compose logs --tail=20 chroma
    exit 1
fi

# 11. Verificar conectividad a Ollama
echo ""
echo "🔍 Verificando conectividad a Ollama..."
if docker exec fase_final_backend curl -s -f http://ollama:11434/api/tags > /dev/null 2>&1; then
    echo "✅ Backend puede conectarse a Ollama"
    
    # Verificar modelo
    MODELS=$(docker exec fase_final_backend curl -s http://ollama:11434/api/tags | grep -o '"name":"[^"]*"' | cut -d'"' -f4)
    echo "   Modelos disponibles: $MODELS"
    
    if echo "$MODELS" | grep -q "llama3"; then
        echo "✅ Modelo llama3 está disponible"
    else
        echo "⚠️  Modelo llama3 NO encontrado"
        echo "   Ejecuta: docker exec -it fase_final_ollama ollama pull llama3"
    fi
else
    echo "❌ ERROR: Backend NO puede conectarse a Ollama"
    exit 1
fi

# 12. Ver logs del backend
echo ""
echo "📋 Últimas líneas de logs del backend:"
echo "================================================================"
docker-compose logs --tail=30 backend

echo ""
echo "================================================================"
echo "✅ CONFIGURACIÓN APLICADA CORRECTAMENTE"
echo "================================================================"
echo ""
echo "📝 Próximos pasos:"
echo "1. Verificar logs en tiempo real: docker-compose logs -f backend"
echo "2. Probar subir un PDF desde el frontend"
echo "3. Si hay problemas, ejecutar: docker-compose logs backend > logs.txt"
echo ""
echo "🌐 Endpoints:"
echo "   - Backend: http://$(hostname -I | awk '{print $1}'):8000"
echo "   - Health: http://$(hostname -I | awk '{print $1}'):8000/health"
echo ""
