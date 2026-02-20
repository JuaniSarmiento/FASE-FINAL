# Script de PowerShell para reconstruir el backend en Windows/Docker Desktop
# Ejecutar desde el directorio del proyecto

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "🔧 RECONSTRUYENDO BACKEND CON CONFIGURACIÓN CORREGIDA" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar que docker-compose.yml existe
if (!(Test-Path "docker-compose.yml")) {
    Write-Host "❌ Error: docker-compose.yml no encontrado" -ForegroundColor Red
    Write-Host "   Por favor ejecuta este script desde el directorio raíz del proyecto" -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ Directorio correcto" -ForegroundColor Green

# 2. Verificar que Docker esté corriendo
try {
    docker ps | Out-Null
    Write-Host "✅ Docker está corriendo" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker no está corriendo. Inicia Docker Desktop." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🛑 Deteniendo backend actual..." -ForegroundColor Yellow
docker-compose stop backend

Write-Host ""
Write-Host "🗑️ Eliminando contenedor anterior..." -ForegroundColor Yellow
docker-compose rm -f backend

Write-Host ""
Write-Host "🔨 Reconstruyendo backend (esto puede tomar unos minutos)..." -ForegroundColor Yellow
docker-compose build --no-cache backend

Write-Host ""
Write-Host "🚀 Iniciando backend con nueva configuración..." -ForegroundColor Yellow
docker-compose up -d backend

Write-Host ""
Write-Host "⏳ Esperando 10 segundos a que el backend inicie..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "📊 ESTADO DE SERVICIOS" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
docker-compose ps

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "🔍 VERIFICANDO VARIABLES DE ENTORNO EN EL BACKEND" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan

$chromaHost = docker exec fase_final_backend printenv CHROMA_DB_HOST 2>$null
$chromaPort = docker exec fase_final_backend printenv CHROMA_DB_PORT 2>$null
$ollamaUrl = docker exec fase_final_backend printenv OLLAMA_BASE_URL 2>$null

Write-Host "CHROMA_DB_HOST: $chromaHost" -ForegroundColor $(if ($chromaHost -eq "chroma") { "Green" } else { "Red" })
Write-Host "CHROMA_DB_PORT: $chromaPort" -ForegroundColor $(if ($chromaPort -eq "8000") { "Green" } else { "Red" })
Write-Host "OLLAMA_BASE_URL: $ollamaUrl" -ForegroundColor $(if ($ollamaUrl -like "*ollama*") { "Green" } else { "Red" })

if ($chromaHost -ne "chroma") {
    Write-Host ""
    Write-Host "❌ ERROR: CHROMA_DB_HOST debería ser 'chroma', pero es: $chromaHost" -ForegroundColor Red
    Write-Host "   Las variables de entorno NO se aplicaron correctamente." -ForegroundColor Red
    Write-Host ""
    Write-Host "📝 Verifica que docker-compose.yml tenga en la sección backend:" -ForegroundColor Yellow
    Write-Host "    environment:" -ForegroundColor Yellow
    Write-Host "      - CHROMA_DB_HOST=chroma" -ForegroundColor Yellow
    Write-Host "      - CHROMA_DB_PORT=8000" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "✅ Variables de entorno correctas" -ForegroundColor Green

Write-Host ""
Write-Host "🔍 Verificando conectividad a ChromaDB..." -ForegroundColor Yellow
$chromaTest = docker exec fase_final_backend curl -s -f http://chroma:8000/api/v1/heartbeat 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Backend puede conectarse a ChromaDB" -ForegroundColor Green
} else {
    Write-Host "❌ Backend NO puede conectarse a ChromaDB" -ForegroundColor Red
    Write-Host ""
    Write-Host "📋 Logs de ChromaDB:" -ForegroundColor Yellow
    docker-compose logs --tail=20 chroma
    exit 1
}

Write-Host ""
Write-Host "🔍 Verificando conectividad a Ollama..." -ForegroundColor Yellow
$ollamaTest = docker exec fase_final_backend curl -s -f http://ollama:11434/api/tags 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Backend puede conectarse a Ollama" -ForegroundColor Green
} else {
    Write-Host "⚠️  Backend NO puede conectarse a Ollama" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "📋 ÚLTIMOS LOGS DEL BACKEND" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
docker-compose logs --tail=30 backend

Write-Host ""
Write-Host "================================================================" -ForegroundColor Green
Write-Host "✅ BACKEND RECONSTRUIDO CORRECTAMENTE" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "📝 En los logs deberías ver:" -ForegroundColor Cyan
Write-Host "   CHROMA_DB_HOST: chroma" -ForegroundColor White
Write-Host "   --- [RagService] Successfully connected to ChromaDB ---" -ForegroundColor White
Write-Host ""
Write-Host "🧪 Prueba ahora:" -ForegroundColor Cyan
Write-Host "   1. Ir al frontend" -ForegroundColor White
Write-Host "   2. Crear una actividad" -ForegroundColor White
Write-Host "   3. Subir un PDF" -ForegroundColor White
Write-Host ""
Write-Host "📊 Ver logs en tiempo real:" -ForegroundColor Cyan
Write-Host "   docker-compose logs -f backend" -ForegroundColor White
Write-Host ""
