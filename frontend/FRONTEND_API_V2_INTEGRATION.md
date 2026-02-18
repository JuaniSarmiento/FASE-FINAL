# Frontend - Integración API V2

Este documento explica la integración del frontend React con la API V2 del sistema de cognición distribuida, que incluye persistencia en PostgreSQL.

## 🎯 Resumen de la Integración

### Arquitectura de Capas

```
┌─────────────────────────────────────────┐
│  Componentes React (ChatInterfaceV2)    │  ← UI Layer
├─────────────────────────────────────────┤
│  Custom Hook (useChatV2)                │  ← State Management
├─────────────────────────────────────────┤
│  API Service (v2.service.ts)            │  ← HTTP Client
├─────────────────────────────────────────┤
│  Backend API V2 (FastAPI)               │  ← REST API
├─────────────────────────────────────────┤
│  LangGraph + PostgreSQL Persistence     │  ← Graph + DB
└─────────────────────────────────────────┘
```

## 📂 Archivos Creados

### 1. **frontEnd/src/services/api/v2.service.ts**
API client para endpoints V2 con manejo robusto de errores.

**Funciones principales:**
- `sendMessageV2(text, studentId, activityId)` - Enviar mensaje al sistema
- `healthCheckV2()` - Verificar estado del sistema
- `getThreadInfo(threadId)` - Obtener metadata de conversación
- `deleteThread(threadId)` - Eliminar historial de thread

**Características:**
- Timeout de 3 minutos para operaciones lentas (RAG + Sandbox)
- Manejo detallado de errores HTTP (400, 500, 503)
- Mensajes de error user-friendly con troubleshooting
- Interceptores de logging para desarrollo

### 2. **frontEnd/src/hooks/useChatV2.ts**
React hook para gestión de estado del chat.

**Estado gestionado:**
- `messages[]` - Array de mensajes
- `isLoading` - Indicador de carga
- `error` - Mensaje de error actual
- `threadId` - ID del thread de conversación
- `currentAgent` - Agente que está respondiendo
- `riskScore` - Score de riesgo ético (0-100)

**Funciones:**
- `handleSendMessage(text)` - Enviar mensaje con actualización optimista
- `clearMessages()` - Limpiar conversación
- `clearError()` - Limpiar error

**Características:**
- Actualizaciones optimistas (UI instantánea)
- Errores integrados en el chat
- Prevención de memory leaks
- Callbacks: `onError`, `onAgentChange`

### 3. **frontEnd/src/components/ChatInterfaceV2.tsx**
Componente principal del chat con diseño moderno.

**Características:**
- Header con info del sistema (thread ID, agente actual, risk score)
- Mensajes con renderizado Markdown
- Indicador de carga educativo ("Analizando código y consultando bibliografía...")
- Información contextual sobre el proceso (RAG, Sandbox, Gobernanza)
- Botón de reset para nueva conversación

### 4. **frontEnd/src/pages/TutorV2Page.tsx**
Página completa que integra el componente de chat.

## 🚀 Uso Rápido

### Opción 1: Usar el Componente Directo

```tsx
import { ChatInterfaceV2 } from '@/components/ChatInterfaceV2';

function MyPage() {
  return (
    <div className="h-screen">
      <ChatInterfaceV2
        studentId="student_123"
        activityId="python_basics"
      />
    </div>
  );
}
```

### Opción 2: Usar el Hook Personalizado

```tsx
import { useChatV2 } from '@/hooks/useChatV2';

function CustomChat() {
  const {
    messages,
    isLoading,
    error,
    threadId,
    currentAgent,
    riskScore,
    handleSendMessage,
    clearMessages,
  } = useChatV2({
    studentId: 'my_student',
    activityId: 'my_activity',
    onError: (err) => console.error(err),
    onAgentChange: (agent) => console.log('Agent:', agent),
  });

  return (
    <div>
      <h1>Thread: {threadId}</h1>
      <p>Agent: {currentAgent}</p>
      <p>Risk: {riskScore}</p>
      
      {messages.map(msg => (
        <div key={msg.id}>{msg.content}</div>
      ))}
      
      {isLoading && <p>Cargando...</p>}
      {error && <p>Error: {error}</p>}
      
      <button onClick={() => handleSendMessage('Hola')}>
        Enviar
      </button>
    </div>
  );
}
```

### Opción 3: Usar la Página Completa

```tsx
import { TutorV2Page } from '@/pages/TutorV2Page';

// En tu router:
<Route path="/tutor-v2" element={<TutorV2Page />} />
```

## ⚙️ Configuración

### 1. Variables de Entorno

Copia `.env.example` a `.env.local`:

```bash
cp .env.example .env.local
```

Contenido de `.env.local`:

```env
VITE_API_V2_BASE_URL=http://localhost:8000/api/v2
VITE_API_TIMEOUT=180000
```

### 2. Verificar Backend

Asegúrate de que el backend esté corriendo:

```bash
cd backend
docker-compose up -d  # PostgreSQL
python -m uvicorn api.main:app --reload  # FastAPI
```

Verifica el health check:

```bash
curl http://localhost:8000/api/v2/health
```

Deberías ver:

```json
{
  "status": "healthy",
  "graph_ready": true,
  "persistence_ready": true,
  "checkpointer_status": "active"
}
```

### 3. Instalar Dependencias (si es necesario)

El componente usa `react-markdown` para renderizar código:

```bash
cd frontEnd
npm install react-markdown
```

## 🔄 Flujo de Datos

### 1. Usuario Envía Mensaje

```
Usuario escribe → handleSendMessage() → Mensaje aparece instantáneamente (optimista)
```

### 2. Backend Procesa

```
sendMessageV2() → API V2 → Supervisor → Tutor/Auditor/Gobernanza
                                  ↓
                            Docker Sandbox (si hay código)
                                  ↓
                            RAG (si se necesita contexto)
                                  ↓
                            PostgreSQL (guarda checkpoint)
```

### 3. Respuesta Recibida

```
Backend responde → Estado actualizado → Mensaje del agente aparece
                                  ↓
                    threadId, agent, riskScore actualizados
```

## 🐛 Manejo de Errores

### Errores HTTP 400 (Validación)

```
Error: Solicitud inválida: message no puede estar vacío
```

**Causa**: Datos mal formateados o campos requeridos faltantes.

### Errores HTTP 500 (Servidor)

```
Error: Fallo en el sistema de agentes (Supervisor/Tutor/Auditor)

Posibles causas:
- Error en la ejecución del Sandbox Docker
- Problema con el sistema RAG (recuperación de documentos)
```

**Acción**: Revisar logs del backend.

### Errores HTTP 503 (Servicio No Disponible)

```
Error: Sistema de persistencia no disponible

Detalles:
- Base de datos PostgreSQL no disponible
- Checkpointer no operativo
```

**Acción**: Verificar que PostgreSQL esté corriendo.

### Errores de Red

```
Error: No se pudo conectar al servidor

Verifica que:
- El servidor backend esté corriendo (docker-compose up)
- El puerto 8000 esté accesible
- No haya problemas de red/firewall
```

**Acción**: Verificar conexión y backend.

## 🎨 Personalización del UI

### Cambiar Colores del Header

```tsx
<div className="bg-gradient-to-r from-blue-600 to-purple-600">
  {/* Tu contenido */}
</div>
```

### Personalizar Mensajes de Carga

```tsx
{isLoading && (
  <div>
    {currentAgent === 'auditor_codigo'
      ? 'Revisando tu código en el sandbox...'
      : 'Consultando bibliografía académica...'}
  </div>
)}
```

### Agregar Indicadores Personalizados

```tsx
{riskScore > 70 && (
  <div className="bg-red-100 text-red-800 p-2 rounded">
    ⚠️ Alto riesgo ético detectado. Se recomienda precaución.
  </div>
)}
```

## 📊 Metadata Disponible

Cada mensaje incluye metadata útil:

```typescript
interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  agent?: {
    name: string;
    type: 'tutor' | 'auditor' | 'gobernanza' | 'unknown';
  };
  metadata?: {
    risk_score?: number;     // 0-100
    phase?: string;          // 'analysis' | 'response' | etc
    thread_id?: string;      // ID del thread
  };
}
```

## 🧪 Testing

### Test Manual

1. Abrir el chat
2. Enviar: "Hola, me llamo Juan"
3. Verificar respuesta
4. Enviar: "¿Cómo me llamo?"
5. Verificar que recuerde el nombre → Persistencia funciona ✅

### Test de Agentes

**Para activar el Tutor:**
```
Mensaje: "Explícame qué es una función en Python"
```

**Para activar el Auditor:**
```
Mensaje: "Revisa este código: print('hola')"
```

**Para activar Gobernanza:**
```
Mensaje: "¿Puedo copiar código de StackOverflow en mi tarea?"
```

### Test de Persistencia

```bash
# Test 1: Crear conversación
curl -X POST http://localhost:8000/api/v2/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hola, soy Ana", "student_id": "test_1", "activity_id": "demo"}'

# Test 2: Verificar memoria (mismo thread)
curl -X POST http://localhost:8000/api/v2/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "¿Cómo me llamo?", "student_id": "test_1", "activity_id": "demo"}'

# Debería responder "Ana"
```

## 🔧 Troubleshooting

### "Cannot find module '@/hooks/useChatV2'"

**Solución**: Verificar que el alias `@` esté configurado en `vite.config.ts`:

```typescript
resolve: {
  alias: {
    '@': path.resolve(__dirname, './src'),
  },
},
```

### "TypeError: messages.map is not a function"

**Solución**: Inicialización incorrecta de `messages`. Debe ser un array:

```typescript
const [messages, setMessages] = useState<Message[]>([]);  // ← Array vacío
```

### "El chat no muestra respuestas"

**Solución**: Verificar logs del navegador (F12 → Console) y backend:

```bash
# Backend logs
docker-compose logs -f backend
```

### "Timeout de 3 minutos muy largo"

**Solución**: Puedes reducir el timeout en desarrollo:

```typescript
// v2.service.ts
const API_TIMEOUT = import.meta.env.DEV ? 30000 : 180000;  // 30s dev, 3min prod
```

## 📚 Referencias

- **Backend API V2**: `backend/api/v2/endpoints.py`
- **LangGraph Persistence**: `backend/core/v2/persistence.py`
- **Tests de Integración**: `backend/tests/v2/test_api_persistence.py`
- **Documentación RAG**: `docs/integrarag.md`

## 🎯 Próximos Pasos

1. **Agregar notificaciones toast** para feedback visual
2. **Implementar búsqueda en historial** de conversaciones
3. **Agregar exportación de conversaciones** a PDF/Markdown
4. **Integrar análisis de sentimiento** del estudiante
5. **Dashboard de métricas** (risk scores, agents más usados, etc.)

## 📞 Soporte

Si encuentras problemas:

1. Revisa los logs del backend: `docker-compose logs -f`
2. Verifica el health check: `curl http://localhost:8000/api/v2/health`
3. Revisa la consola del navegador (F12)
4. Consulta `PROYECTO_COMPLETO.md` para arquitectura completa

---

**Sistema de Cognición Distribuida V2** | PostgreSQL + LangGraph + Docker Sandbox + RAG
