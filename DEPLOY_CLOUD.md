# 🌐 Guía de Despliegue en la Nube

## ⚡ Corrección Rápida (Si tienes el error de ChromaDB)

```bash
# 1. Conectar al servidor
ssh usuario@187.77.41.214
cd /ruta/al/proyecto

# 2. Subir archivos actualizados
# - src/infrastructure/config/settings.py
# - docker-compose.yml
# O hacer git pull si usas git

# 3. Ejecutar script de corrección
chmod +x fix_cloud.sh
bash fix_cloud.sh
```

El script automáticamente:

- ✅ Detiene servicios
- ✅ Reconstruye el backend
- ✅ Verifica configuración
- ✅ Inicia servicios
- ✅ Valida conectividad

---

## Configuración para Producción

### 1. Preparar Variables de Entorno

Crea un archivo `.env.production` en el servidor:

```env
# Database
DATABASE_URL=postgresql://user:password@host:5432/ai_native
DB_ECHO=False

# AI Services (Deben estar en la misma red Docker o accesibles)
OLLAMA_BASE_URL=http://ollama:11434
CHROMA_DB_HOST=chroma
CHROMA_DB_PORT=8000

# Security
SECRET_KEY=genera-un-secret-key-super-seguro-y-aleatorio

# Frontend API URL
VITE_API_BASE_URL=https://tudominio.com/api/v1
```

### 2. Actualizar docker-compose.yml para Producción

Asegúrate de que el archivo `docker-compose.yml` tenga las configuraciones correctas ya aplicadas en este proyecto.

### 3. Iniciar Servicios en el Servidor

```bash
# SSH al servidor
ssh usuario@187.77.41.214

# Navegar al directorio del proyecto
cd /ruta/al/proyecto

# Copiar variables de entorno
cp .env.production .env

# Construir e iniciar servicios
docker-compose up -d --build

# Descargar modelo Ollama
docker exec -it fase_final_ollama ollama pull llama3

# Verificar que todos los servicios estén corriendo
docker-compose ps

# Ver logs
docker-compose logs -f backend
```

### 4. Configurar Nginx (si aplica)

Si usas Nginx como reverse proxy:

```nginx
server {
    listen 80;
    server_name tudominio.com;

    # Frontend
    location / {
        proxy_pass http://localhost:5173;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;

        # Aumentar timeouts para generación de IA
        proxy_read_timeout 600s;
        proxy_connect_timeout 600s;
        proxy_send_timeout 600s;
    }
}
```

### 5. Verificar Conectividad

```bash
# Desde el servidor, verificar servicios
curl http://localhost:8000/health
curl http://187.77.41.214:11434/api/tags

# Desde tu máquina, verificar acceso externo
curl http://187.77.41.214:8000/health
```

### 6. Troubleshooting en Producción

#### Los ejercicios no se generan

1. **Verificar Ollama dentro del contenedor**:

```bash
docker exec -it fase_final_backend curl http://ollama:11434/api/tags
```

Si falla, el problema es la red Docker. Verifica que todos los contenedores estén en la misma red:

```bash
docker network inspect fase_final_default
```

2. **Verificar logs del backend**:

```bash
docker logs fase_final_backend -f | grep -i "ollama\|error\|exception"
```

3. **Verificar que el modelo esté descargado**:

```bash
docker exec -it fase_final_ollama ollama list
```

#### ChromaDB no funciona

1. **Verificar ChromaDB**:

```bash
docker exec -it fase_final_backend curl http://chroma:8000/api/v1/heartbeat
```

2. **Ver logs de ChromaDB**:

```bash
docker logs fase_final_chroma -f
```

#### Base de datos no conecta

1. **Verificar PostgreSQL**:

```bash
docker exec -it fase_final_db psql -U postgres -d ai_native -c "SELECT 1;"
```

2. **Verificar variable DATABASE_URL**:

```bash
docker exec -it fase_final_backend env | grep DATABASE_URL
```

### 7. Monitoreo

#### Health Check Endpoint

```bash
# Verificar estado general
curl http://tudominio.com/api/v1/health

# Respuesta esperada
{"status": "ok"}
```

#### Logs en Tiempo Real

```bash
# Todos los servicios
docker-compose logs -f

# Solo backend
docker-compose logs -f backend

# Solo Ollama
docker-compose logs -f ollama
```

### 8. Actualizaciones

```bash
# Detener servicios
docker-compose down

# Actualizar código (git pull o como corresponda)
git pull origin main

# Reconstruir e iniciar
docker-compose up -d --build

# Verificar
docker-compose ps
curl http://localhost:8000/health
```

### 9. Backup

#### Base de Datos

```bash
# Backup
docker exec fase_final_db pg_dump -U postgres ai_native > backup_$(date +%Y%m%d).sql

# Restaurar
cat backup_20260220.sql | docker exec -i fase_final_db psql -U postgres ai_native
```

#### ChromaDB

```bash
# Backup del volumen
docker run --rm -v fase_final_chroma_data:/data -v $(pwd):/backup alpine tar czf /backup/chroma_backup_$(date +%Y%m%d).tar.gz /data
```

### 10. Seguridad

- [ ] Cambiar SECRET_KEY en `.env`
- [ ] Usar HTTPS (certificado SSL con Let's Encrypt)
- [ ] Configurar firewall (solo puertos 80, 443, 22)
- [ ] Actualizar contraseñas de PostgreSQL
- [ ] Limitar acceso SSH por IP si es posible
- [ ] Configurar backups automáticos diarios

---

## Checklist Pre-Despliegue

- [ ] `.env.production` configurado
- [ ] Código actualizado en el servidor
- [ ] Docker y docker-compose instalados
- [ ] Puertos abiertos (80, 443, 8000)
- [ ] Modelo Ollama descargado
- [ ] Base de datos migrada
- [ ] Nginx configurado (si aplica)
- [ ] Certificado SSL instalado (si aplica)
- [ ] Backups configurados

## URLs de Referencia

- **Backend Health**: `http://tudominio.com/api/v1/health`
- **API Docs**: `http://tudominio.com/api/v1/docs`
- **Frontend**: `http://tudominio.com`

## Soporte

Si tienes problemas en producción, revisa:

1. Logs del backend: `docker logs fase_final_backend -f`
2. Estado de servicios: `docker-compose ps`
3. Guía de troubleshooting en `SETUP_AI.md`
