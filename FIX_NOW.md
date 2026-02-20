# PASOS PARA CORREGIR EL PROBLEMA DE CHROMADB

## El problema
El backend sigue intentando conectarse a `localhost:8001` en lugar de `chroma:8000`

## Solución: Reconstruir el backend

### Opción 1: Script Automático (Recomendado)
```powershell
# En PowerShell, desde el directorio del proyecto:
.\rebuild_backend.ps1
```

### Opción 2: Comandos Manuales
```powershell
# 1. Detener backend
docker-compose stop backend

# 2. Eliminar contenedor
docker-compose rm -f backend

# 3. Reconstruir SIN caché (importante)
docker-compose build --no-cache backend

# 4. Iniciar backend
docker-compose up -d backend

# 5. Ver logs
docker-compose logs -f backend
```

### Opción 3: Reiniciar todo (si lo anterior no funciona)
```powershell
# Detener todo
docker-compose down

# Reconstruir backend
docker-compose build --no-cache backend

# Iniciar todo
docker-compose up -d

# Ver logs
docker-compose logs -f backend
```

## ¿Cómo verificar que funcionó?

En los logs del backend deberías ver:
```
============================================================
📋 CONFIGURATION LOADED
============================================================
OLLAMA_BASE_URL: http://ollama:11434
CHROMA_DB_HOST: chroma              ← DEBE SER "chroma" NO "localhost"
CHROMA_DB_PORT: 8000
============================================================
--- [RagService] Successfully connected to ChromaDB ---
```

Si ves `localhost` en lugar de `chroma`, las variables de entorno NO se están aplicando.

## Verificar variables manualmente
```powershell
docker exec fase_final_backend printenv | Select-String "CHROMA"
```

Debe mostrar:
```
CHROMA_DB_HOST=chroma
CHROMA_DB_PORT=8000
```

## Probar conectividad
```powershell
# Desde el backend a ChromaDB
docker exec fase_final_backend curl http://chroma:8000/api/v1/heartbeat
```

Si responde, la conexión funciona.

## Si después de todo esto SIGUE fallando

El problema puede ser que el contenedor tenga un `CMD` o `ENTRYPOINT` que ignore las variables de entorno. En ese caso:

1. Verificar Dockerfile
2. Asegurarse de que NO haya un `.env` dentro del contenedor que sobreescriba las variables
3. Ver los logs completos: `docker-compose logs backend > logs.txt`
