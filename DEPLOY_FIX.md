# 🔧 Corrección Urgente - ChromaDB en la Nube

## Problema
El backend en Docker está intentando conectarse a `localhost:8001` en lugar de `chroma:8000`.

## Solución Aplicada
✅ Corregido `settings.py` para que lea correctamente las variables de entorno de Docker
✅ Actualizado `docker-compose.yml` con configuración correcta

## 🚀 Pasos para Aplicar en el Servidor (187.77.41.214)

### 1. Conectar al servidor
```bash
ssh usuario@187.77.41.214
cd /ruta/al/proyecto
```

### 2. Detener servicios actuales
```bash
docker-compose down
```

### 3. Actualizar el código
```bash
# Si usas git:
git pull origin main

# Si subes archivos manualmente, asegúrate de reemplazar:
# - src/infrastructure/config/settings.py
# - docker-compose.yml
```

### 4. Verificar que docker-compose.yml tenga estas variables
```bash
cat docker-compose.yml | grep -A 8 "environment:"
```

**Debe mostrar:**
```yaml
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/ai_native
      - OLLAMA_BASE_URL=http://ollama:11434
      - CHROMA_DB_HOST=chroma
      - CHROMA_DB_PORT=8000
      - DB_ECHO=False
      - PYTHONUNBUFFERED=1
```

### 5. Reconstruir e iniciar servicios
```bash
# Limpiar contenedores anteriores
docker-compose rm -f backend

# Reconstruir el backend con los cambios
docker-compose build --no-cache backend

# Iniciar todos los servicios
docker-compose up -d

# Ver logs en tiempo real
docker-compose logs -f backend
```

### 6. Verificar que arranque correctamente

**Deberías ver en los logs:**
```
============================================================
📋 CONFIGURATION LOADED
============================================================
OLLAMA_BASE_URL: http://ollama:11434
CHROMA_DB_HOST: chroma
CHROMA_DB_PORT: 8000
DATABASE_URL: postgresql://postgres:postgres@db:5432/...
============================================================
```

Si ves `localhost` en lugar de `chroma`, las variables de entorno no se están aplicando.

### 7. Probar la generación de ejercicios

```bash
# Verificar que ChromaDB está accesible desde el backend
docker exec -it fase_final_backend curl http://chroma:8000/api/v1/heartbeat

# Debería retornar algo como: {"nanosecond heartbeat": ...}
```

### 8. Verificar estado de todos los servicios
```bash
docker-compose ps
```

Todos los servicios deben estar `Up`:
- fase_final_db
- fase_final_ollama  
- fase_final_chroma
- fase_final_backend

---

## 🐛 Si aún falla

### Verificar logs de ChromaDB
```bash
docker-compose logs chroma
```

### Verificar que ChromaDB esté en la misma red
```bash
docker network inspect fase_final_default | grep -A 5 "chroma\|backend"
```

Ambos contenedores deben estar en la misma red.

### Verificar variables de entorno dentro del contenedor
```bash
docker exec -it fase_final_backend env | grep CHROMA
```

Debe mostrar:
```
CHROMA_DB_HOST=chroma
CHROMA_DB_PORT=8000
```

### Reiniciar ChromaDB si es necesario
```bash
docker-compose restart chroma
docker-compose logs -f chroma
```

---

## 🧪 Prueba Final

Una vez que todo esté corriendo, prueba subir un PDF desde el frontend:

1. Ir a la creación de actividad
2. Subir un PDF
3. Generar ejercicios

**Si todo funciona, verás en los logs del backend:**
```
--- [RagService] Successfully connected to ChromaDB ---
--- [RagService] Processing document: archivo.pdf for activity xxx ---
--- [RagService] Created X chunks ---
--- [RagService] Successfully stored X chunks in ChromaDB ---
```

---

## 📞 Comandos Útiles

```bash
# Ver logs en vivo del backend
docker-compose logs -f backend

# Ver logs de todos los servicios
docker-compose logs -f

# Reiniciar solo el backend
docker-compose restart backend

# Ver estado de servicios
docker-compose ps

# Entrar al contenedor del backend (para debugging)
docker exec -it fase_final_backend bash
```

---

## ✅ Checklist de Verificación

- [ ] docker-compose.yml actualizado con `CHROMA_DB_HOST=chroma`
- [ ] settings.py actualizado (sin usar `os.getenv()` directamente)
- [ ] Backend reconstruido (`docker-compose build --no-cache backend`)
- [ ] Todos los servicios corriendo (`docker-compose ps`)
- [ ] Logs muestran `CHROMA_DB_HOST: chroma` (no localhost)
- [ ] Backend conecta a ChromaDB (ver en logs)
- [ ] Prueba de subida de PDF funciona

Si después de estos pasos sigue fallando, ejecuta:
```bash
docker-compose logs backend > backend_logs.txt
```
Y comparte el contenido para diagnóstico.
