# 🔍 Informe de Auditoría Técnica — AI-Native Learning Platform

**Proyecto**: Fase Final  
**Fecha**: 18 de febrero de 2026  
**Tipo**: Auditoría completa de arquitectura, seguridad, calidad de código y estado funcional  

---

## 1. Resumen Ejecutivo

El proyecto es una **plataforma educativa con IA integrada** que combina gestión académica, tutoría virtual con LLMs (Ollama/LLaMA), evaluación automatizada de código, análisis de riesgo de deserción y RAG (Retrieval-Augmented Generation) con ChromaDB. Arquitectónicamente sigue un patrón **Clean Architecture + Hexagonal** con separación en tres capas: `domain`, `application`, `infrastructure`.

### Veredicto General

| Aspecto | Calificación | Madurez |
|---|---|---|
| Arquitectura | ⭐⭐⭐⭐ | Bien diseñada conceptualmente |
| Seguridad | ⭐⭐ | **Crítica — múltiples vulnerabilidades** |
| Calidad de Código | ⭐⭐⭐ | Funcional con deuda técnica notable |
| Base de Datos | ⭐⭐ | Sin migraciones, tablas legacy, sin FK en varias relaciones |
| IA/ML | ⭐⭐⭐ | Funcional pero frágil y sin guardrails |
| Frontend | ⭐⭐⭐⭐ | Moderno, bien estructurado |
| DevOps | ⭐⭐ | Docker básico, sin CI/CD |
| Testing | ⭐ | Prácticamente inexistente en el código |

---

## 2. Arquitectura del Backend

### 2.1 Estructura de Capas

```
src/
├── domain/          # Entidades, Value Objects, Ports (interfaces)
│   ├── identity/    # Usuarios, autenticación
│   ├── academic/    # Materias, cursos, inscripciones
│   ├── learning/    # Actividades, ejercicios, sesiones
│   ├── grading/     # Submissions, intentos, evaluación
│   ├── analytics/   # Métricas y análisis de riesgo
│   ├── ai_tutor/    # Sesiones de tutoría, mensajes, trazas cognitivas
│   ├── ai/          # Port abstracto de RAG
│   ├── governance/  # Incidentes disciplinarios
│   └── shared/      # Value Objects compartidos
├── application/     # Use Cases (Commands/Queries), DTOs
│   ├── identity/    # RegisterUser, AuthenticateUser
│   ├── academic/    # CreateSubject, CreateCourse, EnrollStudent
│   ├── learning/    # CreateActivity, GenerateExercises, UploadDocument, ChatWithDocument
│   ├── grading/     # SubmitExercise
│   ├── analytics/   # GenerateRiskAnalysis
│   ├── student/     # ListActivities, StartSession, SendMessage, SubmitSolution, ListGrades
│   ├── teacher/     # Dashboard, ListStudents, AddStudentsToModule, StudentActivityDetails
│   ├── governance/  # ReportIncident
│   └── shared/      # UnitOfWork abstracto, DTOs comunes
└── infrastructure/  # Implementaciones concretas
    ├── http/        # FastAPI routers + dependency container
    ├── persistence/ # SQLAlchemy models + repository implementations
    ├── ai/          # Ollama (LLM), ChromaDB (RAG)
    ├── auth/        # Bcrypt hasher, JWT token provider
    ├── config/      # Settings (Pydantic)
    ├── grading/     # LocalCodeExecutor
    └── tasks/       # (vacío o mínimo)
```

#### ✅ Fortalezas

- **Separación de capas correcta**: Domain no importa de Infrastructure. Los puertos (interfaces) en `domain/ports/` son implementados por `infrastructure/`.
- **Dependency Injection via FastAPI Depends**: [container.py](file:///c:/Users/juani/Desktop/Fase%20Final/src/infrastructure/http/dependencies/container.py) actúa como composición root con ~41 factory functions.
- **CQRS ligero**: Separación entre Commands (escritura) y Queries (lectura) en application layer.
- **Unit of Work pattern**: [unit_of_work.py](file:///c:/Users/juani/Desktop/Fase%20Final/src/infrastructure/persistence/unit_of_work.py) implementa correctamente transacciones atómicas.

#### ⚠️ Problemas Encontrados

| Problema | Severidad | Ubicación |
|---|---|---|
| Imports mid-file (no PEP 8) | Baja | [student_router.py](file:///c:/Users/juani/Desktop/Fase%20Final/src/infrastructure/http/routers/student/student_router.py), [teacher_router.py](file:///c:/Users/juani/Desktop/Fase%20Final/src/infrastructure/http/routers/teacher/teacher_router.py) |
| Pydantic models definidos inline en routers | Media | `CodeSubmissionBody` en student_router, `ExerciseResponse`, `PublishActivityRequest`, `ActivityStatusUpdate` en teacher_router |
| Inyección directa de `Session` (SQLAlchemy) en routers | Media | [student_router.py:L137-143](file:///c:/Users/juani/Desktop/Fase%20Final/src/infrastructure/http/routers/student/student_router.py#L137-L143), [analytics_router.py](file:///c:/Users/juani/Desktop/Fase%20Final/src/infrastructure/http/routers/analytics/analytics_router.py) |
| Duplicación de get_unit_of_work y get_analytics_repository | Media | Definidos tanto en container.py como en analytics_router.py |
| Container.py monolítico (223 líneas) | Baja | Debería modularizarse por dominio |

---

## 3. Seguridad

> [!CAUTION]
> Se identificaron múltiples vulnerabilidades críticas que harían inaceptable un despliegue a producción sin remediación.

### 3.1 Vulnerabilidades Críticas

#### 🔴 SECRET_KEY Hardcodeada
```python
# settings.py:L10
SECRET_KEY: str = "supersecretkey"  # TODO: Move to .env for production
```
**Impacto**: Cualquier persona con acceso al repositorio puede forjar tokens JWT válidos y acceder como cualquier usuario.

#### 🔴 Autenticación Mock en Rutas de Estudiante
```python
# student_router.py:L30
student_id: str = "default_student"  # Mock auth for now or from token
```
**Impacto**: **Cualquier petición sin autenticación accede a datos como `default_student`**. No hay middleware de autenticación activo en las rutas de estudiante.

#### 🔴 Ejecución de Código Sin Sandboxing
```python
# local_code_executor.py:L26-31
result = subprocess.run(
    [sys.executable, tmp_path],
    capture_output=True, text=True, timeout=5
)
```
**Impacto**: El código del estudiante se ejecuta **directamente en el servidor** con permisos del proceso FastAPI. Un estudiante malicioso podría:
- Leer/escribir archivos del servidor
- Ejecutar comandos del sistema
- Acceder a variables de entorno (incluyendo `DATABASE_URL`)
- Realizar ataques de red internos

#### 🔴 CORS Abierto para Desarrollo
```python
# main.py:L25-31
allow_origins=["http://localhost:3000", "http://localhost:5173"],
allow_methods=["*"],
allow_headers=["*"],
```
**Nota**: Aceptable para desarrollo, pero **crítico si se despliega sin cambiar**.

### 3.2 Vulnerabilidades Medias

| Issue | Detalle |
|---|---|
| Sin RBAC (Role-Based Access Control) | Las rutas de teacher no validan el rol del usuario en la mayoría de endpoints |
| Sin rate limiting | Ni en auth ni en AI endpoints; vulnerable a brute-force y abuso de API de Ollama |
| `datetime.utcnow()` deprecated | Usado en todos los modelos; debería ser `datetime.now(timezone.utc)` |
| Sin validación de token refresh | El refresh token se genera pero no hay endpoint para refrescarlo |
| Sin blacklist de tokens | No hay mecanismo para invalidar tokens |

---

## 4. Base de Datos

### 4.1 Esquema

El schema SQL ([init_schema.sql](file:///c:/Users/juani/Desktop/Fase%20Final/init_schema.sql), 686 líneas) define **15 tablas** con sus PKs, FKs e índices.

| Tabla | Descripción | FK Correctas |
|---|---|---|
| `users` | Usuarios con roles en ARRAY | ✅ |
| `subjects` | Materias académicas | ✅ |
| `courses` | Instancias de materias (año/semestre) | ✅ → subjects |
| `enrollments` | Inscripciones | ✅ → users, courses |
| `activities` | Actividades de aprendizaje | ✅ (parcial: teacher_id sin FK) |
| `exercises` | Ejercicios de código | ✅ → activities |
| `sessions` | Sesiones de aprendizaje | ✅ → activities |
| `tutor_messages` | Mensajes del chat con IA | ✅ → sessions |
| `cognitive_traces` | Trazas cognitivas | ✅ → sessions |
| `submissions` | Entregas de código | ✅ → activities |
| `exercise_attempts` | Intentos por ejercicio | ✅ → submissions, exercises |
| `risk_analyses` | Análisis de riesgo de IA | ✅ → submissions |
| `activity_documents` | Documentos subidos (RAG) | ✅ → activities |
| `incidents` | Incidentes disciplinarios | ⚠️ student_id sin FK |
| `activity_assignments` | Asignaciones estudiante-actividad | ✅ → activities, users |

### 4.2 Problemas Encontrados

> [!WARNING]
> No existe sistema de migraciones (Alembic). Los cambios de esquema se gestionan manualmente con un dump SQL monolítico.

| Problema | Severidad | Detalle |
|---|---|---|
| **Sin Alembic/migraciones** | 🔴 Crítico | Cambios al esquema requieren recrear la BD completa |
| **Tablas legacy fantasma** | Media | `sessions_v2`, `tutor_sessions` existen pero no son usadas por el ORM |
| **teacher_id sin FK** | Media | `activities.teacher_id` no referencia `users.id` |
| **incidents.student_id sin FK** | Media | No tiene constraint referencial |
| **String como PK (UUID)** | Baja | Performance sub-óptima vs `UUID` nativo de PostgreSQL |
| **ARRAY(String) para roles** | Media | No normalizado; impide queries eficientes por rol |
| **Imports duplicados** en [models/__init__.py](file:///c:/Users/juani/Desktop/Fase%20Final/src/infrastructure/persistence/models/__init__.py) | Baja | Learning y grading models importados dos veces |
| **`\restrict` en SQL** | Baja | Línea 5 y 684 de init_schema.sql contienen directivas no estándar |

---

## 5. Integración de IA

### 5.1 Componentes IA

| Componente | Archivo | Función |
|---|---|---|
| **Generador de Ejercicios** | [ollama_service.py](file:///c:/Users/juani/Desktop/Fase%20Final/src/infrastructure/ai/llm/ollama_service.py) | Genera ejercicios de código con LLM |
| **Tutor Virtual (RAG)** | [rag_service.py](file:///c:/Users/juani/Desktop/Fase%20Final/src/infrastructure/ai/rag/rag_service.py) | Chat basado en documentos del curso |
| **Analizador de Riesgo** | [risk_analyzer.py](file:///c:/Users/juani/Desktop/Fase%20Final/src/infrastructure/ai/llm/risk_analyzer.py) | Evalúa riesgo de deserción/frustración |
| **Auditor de Código** | `ollama_auditor.py` | Evalúa calidad de código entregado |

### 5.2 Evaluación Técnica

#### Generador de Ejercicios
- ✅ Prompt engineering sofisticado con rol educativo y constraints narrativos
- ✅ Fallback a resultados parciales si falla mid-generation
- ✅ JSON cleaning robusto (busca primer `{` y último `}`)
- ✅ Descubrimiento automático de URL de Ollama (múltiples fallbacks)
- ⚠️ **URL discovery** con IPs Docker hardcodeadas
- ⚠️ Timeout de 300s por batch — podría bloquear el servidor
- ⚠️ Modelo `llama3` hardcodeado sin configuración por entorno

#### Tutor Virtual (RAG)
- ✅ Pipeline completo: PDF → Chunks → Embeddings → ChromaDB → Retrieval → LLM
- ✅ Prompt Socrático bien diseñado (prohibición de dar código directo)
- ✅ Modelo de embeddings estándar (`all-MiniLM-L6-v2`)
- ⚠️ `print("DEBUG: ...")` statements en producción
- ⚠️ Historia limitada a últimos 5 mensajes (ventana de contexto estrecha)
- ⚠️ No hay caché de embeddings — recalcula en cada query
- ❌ **Sin timeout** en `_call_ollama()` — puede bloquearse indefinidamente

#### Analizador de Riesgo
- ✅ Prompt psicoeducativo bien diseñado
- ✅ Fallback graceful cuando Ollama falla
- ⚠️ Trunca código a 1000 chars — puede perder contexto crucial
- ⚠️ `os.getenv()` directo en vez de usar `settings`

---

## 6. Frontend

### 6.1 Stack Tecnológico

| Tecnología | Versión | Rol |
|---|---|---|
| React | 19.0.0 | Framework UI |
| TypeScript | 5.7.2 | Tipado estático |
| Vite | 6.0.6 | Bundler/Dev Server |
| TailwindCSS | 3.4.17 | Estilos |
| Zustand | 5.0.2 | Estado global |
| React Query (TanStack) | 5.62.0 | Estado servidor |
| React Router | 7.1.1 | Enrutamiento |
| Monaco Editor | 4.7.0 | Editor de código |
| Radix UI | Multiple | Componentes primitivos accesibles |
| Recharts | 2.15.0 | Gráficos |
| Axios | 1.13.5 | HTTP Client |

### 6.2 Estructura

```
frontend/src/
├── pages/
│   ├── auth/      (2 pages: Login, Register)
│   ├── student/   (7 pages: Dashboard, Activities, Session, etc.)
│   └── teacher/   (10 pages: Dashboard, Students, Analytics, etc.)
├── services/
│   ├── api.ts            (Axios instance configurada)
│   ├── auth.service.ts   (Autenticación)
│   ├── student.service.ts (9.4 KB — completo)
│   └── teacher.service.ts (18.8 KB — extenso)
├── components/    (6 componentes compartidos)
├── contexts/      (1: AuthContext)
├── hooks/         (1 custom hook)
├── layouts/       (2: Student, Teacher layouts)
├── stores/        (1: Zustand store)
└── types/         (1: Type definitions)
```

#### ✅ Fortalezas
- Stack moderno y actualizado (React 19, Vite 6, latest TanStack)
- Buena separación en services layer
- Radix UI para accesibilidad
- Monaco Editor para IDE embebido
- Setup de testing configurado (Vitest + Playwright)

#### ⚠️ Problemas
- Carpeta `src_old/` con código legacy sin limpiar
- Archivos de debug en raíz (`debug_auth.js`, `debug_login.js`, `test-backend.js`)
- Documentación de integración excesiva en archivos `.md` del frontend
- 3 archivos `.env*` (posible confusión de configuración)

---

## 7. DevOps e Infraestructura

### 7.1 Docker

El [docker-compose.yml](file:///c:/Users/juani/Desktop/Fase%20Final/docker-compose.yml) define 4 servicios:

| Servicio | Imagen | Puerto |
|---|---|---|
| `db` | postgres:15-alpine | 5440:5432 |
| `ollama` | ollama/ollama:latest | 11434:11434 |
| `chroma` | chromadb/chroma:0.4.24 | 8001:8000 |
| `backend` | Build local (Dockerfile) | 8000:8000 |

#### ⚠️ Problemas

| Problema | Severidad | Detalle |
|---|---|---|
| Frontend no dockerizado | Media | Se ejecuta aparte con `npm run dev` |
| `--reload` en producción | Media | CMD del Dockerfile usa `--reload`, inaceptable para prod |
| Volume mount `.:/app` | Media | Monta todo el código fuente incluyendo `.env` y scripts de debug |
| Sin multi-stage build | Baja | Imagen final incluye gcc y herramientas de compilación |
| GPU hardcodeada para Ollama | Baja | `driver: nvidia` — falla en máquinas sin GPU NVIDIA |
| `docker-compose version: '3.8'` | Baja | Obsoleto; versiones modernas no necesitan este campo |
| Sin healthcheck para backend | Media | Solo db y ollama tienen healthcheck |
| ChromaDB healthcheck incorrecto | Media | Usa `/validation/healthcheck.py` que puede no existir |

### 7.2 CI/CD

> [!IMPORTANT]
> **No existe pipeline de CI/CD**. No hay GitHub Actions, GitLab CI, ni ningún sistema de integración continua.

---

## 8. Testing

> [!WARNING]
> El proyecto tiene **configuración** de testing pero **prácticamente cero tests automatizados** para el código de producción.

| Tipo | Configurado | Implementado |
|---|---|---|
| Unit Tests Backend (pytest) | ✅ (en requirements.txt falta pytest) | ❌ |
| Unit Tests Frontend (Vitest) | ✅ | Desconocido |
| E2E Tests (Playwright) | ✅ | Desconocido |
| Integration Tests | ❌ | ❌ |

Los archivos `test_*.py` y `debug_*.py` en la raíz (13+ archivos) son **scripts ad-hoc de debugging**, no tests automatizados. Ejemplo: `test_grading.py`, `test_chat_persistence.py`, `verify_student_courses.py` son scripts que se ejecutan manualmente y hacen llamadas HTTP directas.

---

## 9. Deuda Técnica Consolidada

### Archivos de Debug/Scripts Ad-Hoc en Raíz

El directorio raíz contiene **14 archivos de debugging** que no deberían estar en producción:

- `debug_activities.py`, `debug_activities_network.py`, `debug_activity_exercises.py`
- `debug_chat_insert.py`, `debug_module_enrollment.py`, `debug_ollama.py`
- `debug_output.txt`, `debug_schema_inspect.py`
- `fix_db_schema.py`, `update_db_schema.py`, `check_tables.py`, `check_architecture_imports.py`
- `test_chat_persistence.py`, `test_grades_query.py`, `test_grading.py`, `test_publish_command.py`
- `publish_activity.py`, `verify_module_creation.py`, `verify_student_courses.py`

### Resumen de Deuda

| Categoría | Items |
|---|---|
| Seguridad | 5 vulnerabilidades críticas |
| Base de Datos | Sin migraciones, tablas legacy, FKs faltantes |
| Código | Imports desordenados, models inline, debug prints |
| Testing | ~0% cobertura automatizada |
| DevOps | Sin CI/CD, sin multi-stage Docker, sin monitoring |
| Documentación | Mezclada entre raíz y frontend, inconsistente |

---

## 10. Conclusión

El proyecto demuestra una **visión arquitectónica sólida** y un conocimiento profundo de patrones de diseño (Clean Architecture, CQRS, Unit of Work, Ports & Adapters). La integración de IA es **ambiciosa y funcional** con features avanzadas como análisis de riesgo psicoedagógico y tutor socrático.

Sin embargo, el estado actual es **firmemente MVP**: la seguridad es insuficiente para producción, no hay sistema de migraciones, la ejecución de código es peligrosa, y la cobertura de tests es prácticamente nula. Se necesita un trabajo significativo para llevarlo a un estado production-ready.
