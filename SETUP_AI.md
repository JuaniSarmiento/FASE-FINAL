# 🛠️ Guía de Configuración - Generación de Ejercicios con IA

## Problemas Corregidos

### 1. **Configuración de Ollama**
- ✅ Corregida URL de Ollama para Docker y modo local
- ✅ Agregada detección automática de URLs disponibles
- ✅ Verificación de modelo descargado

### 2. **Configuración de ChromaDB**
- ✅ Variables de entorno configurables
- ✅ Manejo de errores mejorado
- ✅ Logs detallados del procesamiento de PDFs

### 3. **Variables de Entorno**
- ✅ Archivo `.env` creado con configuración correcta

---

## 🚀 Configuración Rápida

### Opción 1: Desarrollo Local

#### 1. Instalar Ollama
```bash
# Windows: Descargar desde https://ollama.ai
# Linux/Mac:
curl -fsSL https://ollama.ai/install.sh | sh
```

#### 2. Descargar el modelo
```bash
ollama pull llama3
```

#### 3. Iniciar servicios
```bash
# Terminal 1: Iniciar base de datos y ChromaDB
docker-compose up db chroma

# Terminal 2: Verificar Ollama
ollama serve  # Si no está corriendo automáticamente

# Terminal 3: Verificar configuración
python check_ai_services.py

# Terminal 4: Iniciar backend
python -m uvicorn src.infrastructure.http.main:app --reload --host 0.0.0.0 --port 8000
```

#### 4. Configurar `.env` para local
Tu archivo `.env` ya está configurado para modo local:
```env
OLLAMA_BASE_URL=http://localhost:11434
CHROMA_DB_HOST=localhost
CHROMA_DB_PORT=8001
```

### Opción 2: Docker Completo

#### 1. Actualizar `.env` para Docker
Si vas a ejecutar todo en Docker, actualiza `.env`:
```env
OLLAMA_BASE_URL=http://ollama:11434
CHROMA_DB_HOST=chroma
CHROMA_DB_PORT=8000
```

#### 2. Iniciar servicios
```bash
docker-compose up -d
```

#### 3. Descargar modelo dentro del contenedor
```bash
docker exec -it fase_final_ollama ollama pull llama3
```

#### 4. Verificar estado
```bash
docker-compose ps
docker logs fase_final_backend
```

---

## 📋 Verificación de Configuración

### Script de Verificación
```bash
python check_ai_services.py
```

Este script verifica:
- ✅ Ollama está corriendo
- ✅ Modelo `llama3` está descargado
- ✅ ChromaDB está disponible

### Salida Esperada
```
🔍 Verificando configuración de IA para el proyecto...

✅ Ollama está corriendo en http://localhost:11434

📦 Modelos disponibles: ['llama3', 'llama2']
✅ Modelo 'llama3' está disponible

✅ ChromaDB está corriendo en http://localhost:8001

============================================================
📊 RESUMEN:
============================================================
Ollama:       ✅ OK
Modelo llama3: ✅ OK
ChromaDB:     ✅ OK

✅ Todo configurado correctamente. El sistema está listo.
```

---

## 🧪 Probar la Generación

### 1. Desde la UI (Frontend)
1. Ir a `/teacher/modules/{module_id}/create-activity`
2. Subir un PDF
3. Configurar parámetros (topic, dificultad, lenguaje)
4. Click en "Generar Ejercicios con IA"

### 2. Desde API directamente
```bash
# 1. Crear actividad
curl -X POST http://localhost:8000/api/v1/teacher/activities \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Activity",
    "course_id": "default_course",
    "teacher_id": "teacher123",
    "instructions": "Test"
  }'

# Respuesta: {"id": "activity_id_123", ...}

# 2. Subir PDF
curl -X POST http://localhost:8000/api/v1/learning/activities/activity_id_123/document \
  -F "file=@tu_archivo.pdf"

# 3. Generar ejercicios
curl -X POST http://localhost:8000/api/v1/learning/generate \
  -H "Content-Type: application/json" \
  -d '{
    "activity_id": "activity_id_123",
    "topic": "Variables en Python",
    "difficulty": "medium",
    "language": "python",
    "count": 3
  }'
```

---

## 🐛 Troubleshooting

### Error: "Could not connect to Ollama"

**Causa**: Ollama no está corriendo o URL incorrecta

**Solución**:
```bash
# Verificar si Ollama está corriendo
curl http://localhost:11434/api/tags

# Si no responde, iniciar Ollama
ollama serve

# Verificar nuevamente
python check_ai_services.py
```

### Error: "Model 'llama3' not found"

**Causa**: Modelo no descargado

**Solución**:
```bash
# Descargar modelo
ollama pull llama3

# Verificar modelos descargados
ollama list
```

### Error: "Failed to connect to ChromaDB"

**Causa**: ChromaDB no está corriendo

**Solución**:
```bash
# Iniciar ChromaDB
docker-compose up chroma -d

# Verificar que está corriendo
curl http://localhost:8001/api/v1/heartbeat
```

### Error: "PDF file appears to be empty"

**Causa**: PDF corrupto o protegido

**Solución**:
- Asegúrate de que el PDF no esté encriptado
- Verifica que el PDF contenga texto extraíble (no solo imágenes)
- Prueba con otro PDF

### No se generan ejercicios (sin error explícito)

**Verificar logs**:
```bash
# Docker
docker logs fase_final_backend -f

# Local
# Los logs aparecen en la terminal donde corriste uvicorn
```

**Buscar**:
- `[OllamaExerciseGenerator]` - Estado de generación
- `[RagService]` - Procesamiento de PDFs
- `ERROR` o `EXCEPTION`

---

## 📊 Monitoreo en Producción

### Variables de Entorno para Producción

Asegúrate de configurar en tu ambiente de producción:

```env
# Producción (Cloud)
OLLAMA_BASE_URL=http://ollama:11434  # o la IP/dominio de tu servidor Ollama
CHROMA_DB_HOST=chroma  # o la IP/dominio de tu servidor ChromaDB
CHROMA_DB_PORT=8000
DATABASE_URL=postgresql://user:pass@host:port/db
SECRET_KEY=tu-secret-key-seguro-y-largo
DB_ECHO=False
```

### Health Check Endpoint

Agregar verificación de servicios en el health check:

```python
# En main.py
@app.get("/health/ai")
def health_check_ai():
    """Verifica estado de servicios de IA"""
    ollama_ok = check_ollama()
    chroma_ok = check_chroma()
    return {
        "ollama": "ok" if ollama_ok else "error",
        "chromadb": "ok" if chroma_ok else "error"
    }
```

---

## 📝 Notas Adicionales

### Modelos Ollama Recomendados

- **llama3** (Recomendado): Balance entre calidad y velocidad
- **llama2**: Alternativa más ligera
- **codellama**: Especializado en código (opcional)

### Rendimiento

- Generación de 1 ejercicio: ~30-60 segundos
- Procesamiento de PDF (20 páginas): ~10-15 segundos
- Genera ejercicios de 1 en 1 para máxima estabilidad

### Límites

- Tamaño máximo de PDF: Ilimitado (pero considera tiempo de procesamiento)
- Ejercicios por generación: 1-10 recomendado
- Timeout de generación: 300 segundos (5 minutos)

---

## ✅ Checklist de Configuración

- [ ] Ollama instalado y corriendo
- [ ] Modelo `llama3` descargado
- [ ] ChromaDB corriendo
- [ ] PostgreSQL corriendo
- [ ] `.env` configurado correctamente
- [ ] `python check_ai_services.py` pasa todas las verificaciones
- [ ] Backend inicia sin errores
- [ ] Frontend conecta con backend

Si todos los items están marcados, ¡estás listo para generar ejercicios con IA! 🎉
