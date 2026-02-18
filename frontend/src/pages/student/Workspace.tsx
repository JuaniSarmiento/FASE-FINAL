import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import studentService, { type Exercise, type Workspace as WorkspaceData, type SubmissionResponse } from '../../services/student.service'
import { toast } from '../../hooks/useToast'
import Spinner from '../../components/ui/Spinner'
import Editor from '@monaco-editor/react'
import {
  ArrowLeft,
  ChevronLeft,
  ChevronRight,
  CheckCircle2,
  XCircle,
  Send,
  FileCode,
  FileText,
  Code2,
  Bot,
  Sparkles,
} from 'lucide-react'

type TabType = 'instructions' | 'editor' | 'tutor'

interface ExerciseCode {
  exercise_id: string
  code: string
}

interface ExerciseResult {
  exercise_id: string
  exercise_title: string
  grade: number
  ai_feedback: string
  passed: boolean
}

interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

export default function StudentWorkspace() {
  const { activityId } = useParams<{ activityId: string }>()
  const { user } = useAuth()
  const navigate = useNavigate()
  const [workspace, setWorkspace] = useState<WorkspaceData | null>(null)
  const [exercises, setExercises] = useState<Exercise[]>([])
  const [currentExIdx, setCurrentExIdx] = useState(0)
  const [exerciseCodes, setExerciseCodes] = useState<ExerciseCode[]>([])
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [submitted, setSubmitted] = useState(false)
  const [results, setResults] = useState<ExerciseResult[]>([])
  const [activeTab, setActiveTab] = useState<TabType>('instructions') // Default to instructions
  const [alreadyCompleted, setAlreadyCompleted] = useState(false)
  const [sessionId, setSessionId] = useState<string | null>(null)

  // Tutor state
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([])
  const [chatInput, setChatInput] = useState('')
  const [chatLoading, setChatLoading] = useState(false)

  useEffect(() => {
    if (!user || !activityId) return
    const load = async () => {
      try {
        // 1. Check if already completed
        const attempt = await studentService.getActivityAttempt(activityId, user.id).catch(() => null)

        if (attempt && attempt.final_grade !== null) {
          setAlreadyCompleted(true)
          // ... (Logic to load results - kept from previous version if needed, simplified here)
          try {
            const resultsData = await studentService.getActivityResults(activityId, user.id)
            if (resultsData.exercises && resultsData.exercises.length > 0) {
              const mapped = resultsData.exercises.map(ex => ({
                exercise_id: ex.exercise_id,
                exercise_title: ex.exercise_title,
                grade: ex.grade,
                ai_feedback: ex.ai_feedback,
                passed: ex.passed
              }))
              setResults(mapped)
              setSubmitted(true)
              // Fetch workspace just for title
              const ws = await studentService.getWorkspace(activityId, user.id).catch(() => null)
              setWorkspace(ws)
            }
          } catch (e) {
            console.error("Error loading results", e)
          }
          setLoading(false)
          return
        }

        // 2. Fetch Real Data
        const [ws, exs] = await Promise.all([
          studentService.getWorkspace(activityId, user.id),
          studentService.getExercises(activityId, user.id),
        ])
        setWorkspace(ws)
        setExercises(exs)

        // 3. Initialize Session
        try {
          const session = await studentService.startSession({
            student_id: user.id,
            activity_id: activityId,
            mode: 'practice'
          })
          setSessionId(session.session_id)
          console.log('✅ Session created:', session.session_id)

          // Initial Tutor Greeting
          setChatMessages([{
            role: 'assistant',
            content: `¡Hola! Soy tu tutor IA. Estoy listo para ayudarte con "${ws.activity_title}".`
          }])

        } catch (sessionErr) {
          console.error('❌ Error creating session:', sessionErr)
          toast({ title: 'Error de conexión', description: 'No se pudo iniciar la sesión de trabajo.', variant: 'error' })
        }

        // 4. Initialize Editors
        if (exs.length > 0) {
          const codes = exs.map(ex => ({
            exercise_id: ex.exercise_id || ex.id || 'temp',
            code: ex.starter_code || ''
          }))
          setExerciseCodes(codes)
        }

      } catch (err) {
        console.error(err)
        toast({ title: 'Error cargando actividad', variant: 'error' })
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [user, activityId])

  const currentExercise = exercises[currentExIdx]
  const currentCode = exerciseCodes.find((ec) => ec.exercise_id === currentExercise?.exercise_id)?.code || ''

  const updateCode = (code: string | undefined) => {
    if (code === undefined) return
    setExerciseCodes((prev) =>
      prev.map((ec) => (ec.exercise_id === currentExercise?.exercise_id ? { ...ec, code } : ec))
    )
  }

  const handleSendMessage = async () => {
    if (!chatInput.trim() || !sessionId) return

    const userMsg = chatInput
    setChatInput('')
    setChatMessages(prev => [...prev, { role: 'user', content: userMsg }])
    setChatLoading(true)

    try {
      const res = await studentService.sendSessionMessage(sessionId, {
        message: userMsg,
        current_code: currentCode
      })
      setChatMessages(prev => [...prev, { role: 'assistant', content: res.response }])
    } catch (e) {
      toast({ title: 'Error enviando mensaje', variant: 'error' })
      setChatMessages(prev => [...prev, { role: 'assistant', content: 'Lo siento, hubo un error de conexión.' }])
    } finally {
      setChatLoading(false)
    }
  }

  const handleSubmitAll = async () => {
    if (!sessionId || !currentExercise) return
    setSubmitting(true)
    try {
      // Prepare all codes
      const allCodes: Record<string, string> = {}
      exerciseCodes.forEach(ec => allCodes[ec.exercise_id] = ec.code)

      const res = await studentService.submitSessionCode(sessionId, {
        code: currentCode,
        exercise_id: currentExercise.exercise_id, // Specific exercise trigger
        is_final_submission: true,
        all_exercise_codes: allCodes
      })

      // Parse results from detailed audit
      const resultsData: ExerciseResult[] = []

      if (res.details?.exercises_audit && Array.isArray(res.details.exercises_audit)) {
        res.details.exercises_audit.forEach((audit: any) => {
          resultsData.push({
            exercise_id: audit.exercise_id || 'unknown',
            exercise_title: audit.title,
            grade: audit.grade,
            ai_feedback: audit.feedback,
            passed: audit.passed || audit.grade >= 60
          })
        })
      } else {
        // Fallback for when audit fails or old format
        exercises.forEach((ex) => {
          resultsData.push({
            exercise_id: ex.exercise_id || 'unknown',
            exercise_title: ex.title,
            grade: res.grade || 0,
            ai_feedback: res.feedback || 'Evaluado',
            passed: (res.grade || 0) >= 60
          })
        })
      }

      setResults(resultsData)
      setSubmitted(true)
      toast({ title: 'Actividad Entregada', variant: 'success' })

    } catch (e: any) {
      toast({ title: 'Error en la entrega', description: e.message, variant: 'error' })
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) return <div className="flex justify-center py-20"><Spinner size="lg" /></div>

  if (submitted) {
    // Determine overall grade from results or use the one from backend if available
    const totalGrade = results.reduce((sum, r) => sum + r.grade, 0)
    const avgGrade = results.length > 0 ? totalGrade / results.length : 0

    return (
      <div className="space-y-6 container mx-auto px-4 py-8">
        <div className="flex items-center gap-4 mb-6">
          <button onClick={() => navigate('/courses')} className="p-2 hover:bg-gray-100 rounded-full transition-colors">
            <ArrowLeft className="w-6 h-6 text-gray-700" />
          </button>
          <h1 className="text-2xl font-bold text-gray-900">Resultados: {workspace?.activity_title}</h1>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <div className="bg-gray-50 px-6 py-4 border-b border-gray-200 flex justify-between items-center">
            <div>
              <h2 className="text-lg font-semibold text-gray-800">Resumen de Evaluación</h2>
              <p className="text-sm text-gray-500">Corrección realizada por IA Tutor</p>
            </div>
            <div className="text-right">
              <span className="block text-3xl font-bold text-gray-900">{avgGrade.toFixed(1)}/100</span>
              <span className={`text-sm font-medium ${avgGrade >= 60 ? 'text-green-600' : 'text-red-500'}`}>
                {avgGrade >= 60 ? 'APROBADO' : 'NO APROBADO'}
              </span>
            </div>
          </div>

          <div className="divide-y divide-gray-100">
            {results.map((r, i) => (
              <div key={i} className="p-6 hover:bg-gray-50 transition-colors">
                <div className="flex justify-between items-start gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      {r.passed ? (
                        <CheckCircle2 className="w-5 h-5 text-green-500" />
                      ) : (
                        <XCircle className="w-5 h-5 text-red-500" />
                      )}
                      <h3 className="font-semibold text-gray-900">{r.exercise_title}</h3>
                    </div>
                    <div className="bg-blue-50 text-blue-800 p-3 rounded-lg text-sm leading-relaxed border border-blue-100">
                      <div className="flex items-start gap-2">
                        <Bot className="w-4 h-4 mt-0.5 shrink-0" />
                        <span>{r.ai_feedback}</span>
                      </div>
                    </div>
                  </div>
                  <div className="text-right shrink-0">
                    <span className={`inline-block px-3 py-1 rounded-full text-sm font-bold ${r.grade >= 90 ? 'bg-green-100 text-green-700' :
                        r.grade >= 60 ? 'bg-blue-100 text-blue-700' :
                          'bg-red-100 text-red-700'
                      }`}>
                      {r.grade}/100
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="bg-gray-50 px-6 py-4 border-t border-gray-200">
            <button
              onClick={() => navigate('/courses')}
              className="w-full bg-gray-900 text-white py-3 rounded-lg font-medium hover:bg-gray-800 transition-colors shadow-sm"
            >
              Volver a Mis Cursos
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-[calc(100vh-100px)]">
      {/* Header */}
      <div className="flex items-center justify-between mb-4 shrink-0">
        <div className="flex items-center gap-3">
          <button onClick={() => navigate('/courses')} className="p-2 hover:bg-gray-100 rounded-lg"><ArrowLeft className="w-5 h-5" /></button>
          <div>
            <h1 className="text-lg font-semibold">{workspace?.activity_title}</h1>
            <p className="text-xs text-gray-500">Ejercicio {currentExIdx + 1} de {exercises.length}</p>
          </div>
        </div>
      </div>

      <div className="flex flex-1 gap-4 min-h-0">
        {/* Left Panel: Instructions & Chat */}
        <div className="w-1/3 flex flex-col bg-white rounded-xl border border-gray-200 overflow-hidden">
          <div className="flex border-b">
            <button onClick={() => setActiveTab('instructions')} className={`flex-1 py-3 text-sm font-medium ${activeTab === 'instructions' ? 'border-b-2 border-green-500 text-green-700' : 'text-gray-500'}`}>Consigna</button>
            <button onClick={() => setActiveTab('tutor')} className={`flex-1 py-3 text-sm font-medium ${activeTab === 'tutor' ? 'border-b-2 border-blue-500 text-blue-700' : 'text-gray-500'}`}>Tutor IA</button>
          </div>

          <div className="flex-1 overflow-y-auto p-4">
            {activeTab === 'instructions' ? (
              <div className="prose prose-sm">
                <h3>{currentExercise?.title}</h3>
                <div className="whitespace-pre-wrap">{currentExercise?.problem_statement || workspace?.instructions}</div>
              </div>
            ) : (
              <div className="flex flex-col h-full">
                <div className="flex-1 space-y-4 overflow-y-auto mb-4">
                  {chatMessages.map((m, i) => (
                    <div key={i} className={`p-3 rounded-lg text-sm ${m.role === 'user' ? 'bg-gray-100 ml-auto max-w-[80%]' : 'bg-blue-50 max-w-[80%] text-blue-900'}`}>
                      {m.content}
                    </div>
                  ))}
                  {chatLoading && <Spinner size="sm" />}
                </div>
                <div className="flex gap-2">
                  <input
                    value={chatInput}
                    onChange={e => setChatInput(e.target.value)}
                    onKeyDown={e => e.key === 'Enter' && handleSendMessage()}
                    placeholder="Escribe tu duda..."
                    className="flex-1 border rounded-lg px-3 py-2 text-sm"
                  />
                  <button onClick={handleSendMessage} disabled={chatLoading} className="p-2 bg-gray-900 text-white rounded-lg"><Send className="w-4 h-4" /></button>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Right Panel: Editor */}
        <div className="flex-1 flex flex-col rounded-xl border border-gray-200 overflow-hidden bg-white">
          <div className="flex-1">
            <Editor
              height="100%"
              language="python"
              value={currentCode}
              onChange={updateCode}
              theme="vs-dark"
              options={{ minimap: { enabled: false }, fontSize: 14 }}
            />
          </div>
          <div className="p-4 border-t bg-gray-50 flex justify-between items-center">
            <button onClick={() => setCurrentExIdx(i => Math.max(0, i - 1))} disabled={currentExIdx === 0} className="text-sm font-medium text-gray-600 disabled:opacity-50">Anterior</button>

            {currentExIdx === exercises.length - 1 ? (
              <button onClick={handleSubmitAll} disabled={submitting} className="bg-gray-900 text-white px-6 py-2 rounded-lg text-sm font-medium hover:bg-gray-800 disabled:opacity-70 flex items-center gap-2">
                {submitting && <Spinner size="sm" className="border-white" />}
                Entregar Actividad
              </button>
            ) : (
              <button onClick={() => setCurrentExIdx(i => Math.min(exercises.length - 1, i + 1))} className="bg-gray-900 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-gray-800">Siguiente</button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
