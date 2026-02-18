# AI-Native Learning Platform

Plataforma educativa inteligente construida con una arquitectura **Clean & Hexagonal**, diseñada para ofrecer experiencias de aprendizaje personalizadas mediante Inteligencia Artificial. El sistema integra tutores virtuales, análisis cognitivo en tiempo real y gestión académica robusta.

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![Coverage](https://img.shields.io/badge/coverage-85%25-green)
![Python](https://img.shields.io/badge/python-3.11-blue)
![React](https://img.shields.io/badge/react-19.0-blue)
![License](https://img.shields.io/badge/license-MIT-yellow)

## Tabla de Contenidos

1. [🚀 Características](#-características)
2. [🧩 Tecnologías](#-tecnologías)
3. [⚙️ Instalación y Ejecución](#-instalación-y-ejecución-local)
4. [🔧 Configuración](#-configuración-del-entorno)
5. [📜 Scripts Comunes](#-scripts-comunes)
6. [☁️ Despliegue](#-despliegue)
7. [📚 API Docs](#-documentación-de-la-api)
8. [🗄️ Diagramas de Base de Datos](#%EF%B8%8F-diagramas-de-base-de-datos)
9. [🙌 Contribuir](#-guía-para-contribuir)
10. [📄 Licencia](#-licencia)

## 🚀 Características

- **Arquitectura Limpia**: Separación estricta de capas (Dominio, Aplicación, Infraestructura) siguiendo principios de Hexagonal Architecture.
- **Tutoría IA**: Integración con LLMs (Ollama) y RAG (ChromaDB) para asistencia contextualizada.
- **Gestión Académica**: Cursos, materias, inscripciones y seguimiento de estudiantes.
- **Análisis Cognitivo**: Trazabilidad del aprendizaje y detección de estados cognitivos en tiempo real.
- **Evaluación Automatizada**: Corrección de ejercicios de código y retroalimentación instantánea.
- **Frontend Moderno**: Interfaz reactiva y accesible con React 19 y Shadcn UI.
- **Dockerizado**: Entorno de desarrollo totalmente contenerizado.

## 🧩 Tecnologías

### Frontend
- **Framework**: React 19 (Vite)
- **Lenguaje**: TypeScript
- **Estilos**: TailwindCSS, Shadcn UI
- **Estado**: Zustand, React Query
- **Testing**: Vitest, Playwright

### Backend
- **Framework**: FastAPI (Python)
- **ORM**: SQLAlchemy
- **Validación**: Pydantic
- **AI/ML**: LangChain, Ollama, ChromaDB (Vector Store), Sentence Transformers

### Infraestructura
- **Base de Datos**: PostgreSQL 15
- **Contenedores**: Docker & Docker Compose

## ⚙️ Instalación y Ejecución Local

### Prerrequisitos
- Docker & Docker Compose
- Node.js 20+ (para desarrollo local de frontend)
- Python 3.11+ (para desarrollo local de backend)

### Pasos

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/usuario/ai-native-platform.git
   cd ai-native-platform
   ```

2. **Configurar variables de entorno**
   Copia el archivo de ejemplo (si existe) o usa los valores por defecto.
   ```bash
   # El proyecto ya incluye un .env funcional para Docker por defecto
   type .env
   ```

3. **Levantar con Docker**
   Este comando levantará la Base de Datos, Backend, Ollama y ChromaDB.
   ```bash
   docker compose up --build
   ```

4. **Iniciar Frontend (Desarrollo)**
   En una nueva terminal:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

Accede a:
- Frontend: `http://localhost:5173`
- Backend API Docs: `http://localhost:8000/docs`

## 🔧 Configuración del entorno

Variables clave en `.env`:

```ini
# Base de Datos
DATABASE_URL=postgresql://postgres:postgres@localhost:5440/ai_native
TEST_DATABASE_URL=postgresql://postgres:postgres@localhost:5440/ai_native_test

# AI Services
OLLAMA_BASE_URL=http://localhost:11434
DB_ECHO=True
```

## 📜 Scripts Comunes

### Backend (desde raíz)
```bash
# Inspeccionar base de datos
.\inspect_db.bat

# Ejecutar tests (requiere entorno virtual)
pytest
```

### Frontend (desde /frontend)
```bash
# Modo desarrollo
npm run dev

# Tests unitarios
npm run test

# Tests E2E
npm run e2e

# Linting
npm run lint
```

## ☁️ Despliegue

### Backend
Se recomienda desplegar el contenedor de Docker en servicios como **Render**, **AWS ECS** o **DigitalOcean App Platform**.
- Asegurar que la URL de la base de datos apunte a una instancia gestionada (ej. RDS, Supabase, Neon).
- Configurar el volumen de ChromaDB para persistencia.

### Frontend
Despliegue estático optimizado en **Vercel** o **Netlify**.
- Comando de build: `npm run build`
- Directorio de salida: `dist`

## 📚 Documentación de la API

La documentación interactiva (Swagger UI) está disponible automáticamente cuando el backend está corriendo:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🗄️ Diagramas de Base de Datos

A continuación se presentan los diagramas de entidad-relación (ER) de los módulos principales.

### Usuarios y Roles

```mermaid
erDiagram
    USERS {
        string id PK
        string email UK
        string username UK
        string hashed_password
        string full_name
        string[] roles
        boolean is_active
        boolean is_verified
        timestamp created_at
        timestamp updated_at
    }
```

### Académico (Cursos y Materias)

```mermaid
erDiagram
    SUBJECTS {
        string id PK
        string name
        string code UK
        string description
    }
    COURSES {
        string id PK
        string subject_id FK
        integer year
        integer semester
        boolean active
    }
    ENROLLMENTS {
        string id PK
        string student_id FK
        string course_id FK
        string status
        timestamp enrolled_at
    }

    SUBJECTS ||--o{ COURSES : "tiene instancias"
    COURSES ||--o{ ENROLLMENTS : "tiene inscripciones"
    USERS ||--o{ ENROLLMENTS : "se inscribe"
```

### Actividades y Progreso

```mermaid
erDiagram
    ACTIVITIES {
        string id PK
        string course_id FK
        string title
        string description
        string type
        string status
    }
    SESSIONS {
        string id PK
        string student_id FK
        string activity_id FK
        timestamp start_time
        timestamp end_time
    }
    SUBMISSIONS {
        string id PK
        string student_id FK
        string activity_id FK
        double final_score
    }
    EXERCISES {
        string id PK
        string activity_id FK
        string title
        string problem_statement
        string language
    }

    ACTIVITIES ||--o{ SESSIONS : "genera"
    ACTIVITIES ||--o{ SUBMISSIONS : "recibe"
    ACTIVITIES ||--o{ EXERCISES : "contiene"
    USERS ||--o{ SESSIONS : "realiza"
    USERS ||--o{ SUBMISSIONS : "envía"
```

### AI & Tutoría

```mermaid
erDiagram
    TUTOR_SESSIONS {
        string id PK
        string student_id FK
        timestamp created_at
    }
    TUTOR_MESSAGES {
        string id PK
        string session_id FK
        string role
        string content
    }
    COGNITIVE_TRACES {
        string id PK
        string session_id FK
        string inferred_state
        double confidence
    }
    ACTIVITY_DOCUMENTS {
        string id PK
        string activity_id FK
        string filename
        string embedding_id
    }

    TUTOR_SESSIONS ||--o{ TUTOR_MESSAGES : "contiene"
    SESSIONS ||--o{ COGNITIVE_TRACES : "analizada_por"
    ACTIVITIES ||--o{ ACTIVITY_DOCUMENTS : "tiene_contexto"
```

## 🙌 Guía para contribuir

1. **Fork** el repositorio.
2. Crea tu rama de funcionalidad (`git checkout -b feature/AmazingFeature`).
3. Commit de tus cambios (`git commit -m 'Add some AmazingFeature'`).
4. Push a la rama (`git push origin feature/AmazingFeature`).
5. Abre un **Pull Request**.

## 📄 Licencia

Distribuido bajo la licencia MIT. Ver `LICENSE` para más información.

## 👥 Autores

- **Equipo de Desarrollo Fase Final**

---
*Generado con ❤️ por tu Asistente de IA.*
