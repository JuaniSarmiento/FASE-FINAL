import { useEffect, useState } from 'react'
import { Bot, AlertTriangle, CheckCircle2, MessageSquare, TrendingUp, X, Clock, BrainCircuit } from 'lucide-react'
import teacherService, { type AIChat, type StudentRiskAnalysis, type StudentActivityResults } from '../../services/teacher.service'
import { toast } from '../../hooks/useToast'
import Spinner from '../../components/ui/Spinner'

interface StudentAIAnalyticsProps {
  studentId: string
  studentName: string
  activityId: string
  onClose: () => void
}

export default function StudentAIAnalytics({ studentId, studentName, activityId, onClose }: StudentAIAnalyticsProps) {
  const [activeTab, setActiveTab] = useState<'chats' | 'analysis'>('analysis')
  const [analysis, setAnalysis] = useState<StudentRiskAnalysis | null>(null)
  const [grading, setGrading] = useState<StudentActivityResults | null>(null)
  const [chats, setChats] = useState<AIChat[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    const loadDetails = async () => {
      setLoading(true)
      try {
        const details = await teacherService.getStudentActivityDetails(activityId, studentId)

        if (cancelled) return

        // Map to Grading Structure
        setGrading({
          total_exercises: details.exercises?.length || 0,
          passed_exercises: details.exercises?.filter((e: any) => e.passed).length || 0,
          attempt: {
            status: details.status,
            final_grade: details.final_grade,
            submitted_at: details.submitted_at,
            ai_feedback: null
          },
          exercises: details.exercises?.map((e: any) => ({
            exercise_id: e.exercise_id,
            exercise_title: `Ejercicio ${e.exercise_id}`, // Title not in DTO currently, using ID
            grade: e.grade,
            passed: e.passed,
            ai_feedback: e.feedback,
            submitted_at: null
          })) || []
        })

        // Map Chat History
        if (details.chat_history) {
          setChats(details.chat_history.map((c: any, i: number) => ({
            interaction_id: `msg-${i}`,
            student_message: c.role === 'user' ? c.content : '', // Simplified mapping
            ai_response: c.role !== 'user' ? c.content : '',
            created_at: c.timestamp,
            interaction_type: 'chat',
            question_quality: null,
            cognitive_phase: null,
            shows_effort: true,
            gave_direct_answer: false,
            exercise_title: null
          })))
        }

        // Map Risk Analysis
        if (details.risk_analysis) {
          setAnalysis({
            analysis_id: 'latest',
            student_id: studentId,
            student_name: studentName,
            risk_score: details.risk_analysis.risk_score / 100, // Normalize to 0-1 if needed, or keep 0-100
            risk_level: details.risk_analysis.risk_level,
            diagnosis: details.risk_analysis.diagnosis,
            evidence: details.risk_analysis.evidence,
            teacher_advice: details.risk_analysis.teacher_advice,
            intervention: details.risk_analysis.teacher_advice, // Using advice as intervention
            confidence_score: 1.0,
            ai_abuse_detected: details.risk_analysis.risk_level === 'HIGH' || details.risk_analysis.risk_level === 'CRITICAL',
            shows_learning_effort: true,
            copy_paste_pattern: false,
            total_ai_interactions: details.chat_history?.length || 0,
            copy_seeking_count: 0,
            conceptual_questions_count: 0,
            created_at: details.risk_analysis.analyzed_at
          } as unknown as StudentRiskAnalysis)
        }

      } catch (err) {
        toast({ title: 'Error cargando detalles', variant: 'error' })
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    loadDetails()
    return () => { cancelled = true }
  }, [studentId, activityId, studentName])


  const getRiskColor = (level: string) => {
    switch (level) {
      case 'CRITICAL': return 'text-red-600 bg-red-50 border-red-200'
      case 'HIGH': return 'text-orange-600 bg-orange-50 border-orange-200'
      case 'MEDIUM': return 'text-yellow-600 bg-yellow-50 border-yellow-200'
      case 'LOW': return 'text-emerald-600 bg-emerald-50 border-emerald-200'
      default: return 'text-gray-600 bg-gray-50 border-gray-200'
    }
  }

  const getRiskIcon = (level: string) => {
    switch (level) {
      case 'CRITICAL':
      case 'HIGH':
        return <AlertTriangle className="h-5 w-5" />
      case 'MEDIUM':
        return <TrendingUp className="h-5 w-5" />
      case 'LOW':
        return <CheckCircle2 className="h-5 w-5" />
      default:
        return <Bot className="h-5 w-5" />
    }
  }

  return (
    <div className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-5xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div>
            <h2 className="text-xl font-bold text-gray-900">Análisis de IA - {studentName}</h2>
            <p className="text-sm text-gray-500 mt-1">Patrones de uso del tutor IA y detección de mal uso</p>
          </div>
          <button
            onClick={onClose}
            className="rounded-lg p-2 hover:bg-gray-100 transition-colors"
          >
            <X className="h-5 w-5 text-gray-500" />
          </button>
        </div>

        {/* Tabs */}
        <div className="flex items-center gap-2 px-6 border-b border-gray-200">
          <button
            onClick={() => setActiveTab('analysis')}
            className={`flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors ${activeTab === 'analysis'
              ? 'border-gray-900 text-gray-900'
              : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
          >
            <BrainCircuit className="h-4 w-4" />
            Análisis de Riesgo
          </button>
          <button
            onClick={() => setActiveTab('chats')}
            className={`flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors ${activeTab === 'chats'
              ? 'border-gray-900 text-gray-900'
              : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
          >
            <MessageSquare className="h-4 w-4" />
            Chats con IA
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {activeTab === 'analysis' ? (
            <div className="space-y-6">
              {/* Grading Summary */}
              <div className="rounded-xl border border-gray-200 bg-white p-6">
                <h4 className="text-sm font-semibold text-gray-900 mb-3">Resultados de la Actividad</h4>
                {loading ? (
                  <div className="flex items-center gap-3 text-sm text-gray-500">
                    <Spinner size="sm" />
                    Cargando nota y resultados...
                  </div>
                ) : grading ? (
                  <div className="space-y-4">
                    <div className="flex flex-wrap items-center gap-3">
                      <div className="text-sm text-gray-700">
                        <span className="font-semibold">Nota final:</span>{' '}
                        {grading.attempt?.final_grade !== null
                          ? `${Number(grading.attempt.final_grade).toFixed(1)}/100`
                          : '—'}
                      </div>
                      <div className="text-sm text-gray-700">
                        <span className="font-semibold">Aprobados:</span>{' '}
                        {grading.passed_exercises}/{grading.total_exercises}
                      </div>
                      {grading.attempt?.submitted_at && (
                        <div className="text-xs text-gray-500">Enviado: {new Date(grading.attempt.submitted_at).toLocaleString()}</div>
                      )}
                    </div>
                  </div>
                ) : (
                  <p className="text-sm text-gray-500">Sin datos de calificación.</p>
                )}
              </div>

              {/* Analysis Section */}
              {!analysis ? (
                <div className="text-center py-6 relative z-10 bg-gray-900 rounded-xl">
                  <div className="flex justify-center mb-4">
                    <div className="relative">
                      <div className="absolute inset-0 bg-blue-500 blur-xl opacity-20 animate-pulse"></div>
                      <BrainCircuit className="h-12 w-12 text-blue-400 relative z-10 animate-pulse" />
                    </div>
                  </div>
                  <p className="text-sm font-medium text-white mb-2">
                    Analizando perfil del estudiante...
                  </p>
                  <p className="text-xs text-gray-400 max-w-[80%] mx-auto leading-relaxed">
                    El análisis se está generando en background. Por favor, recarga la página en unos segundos.
                  </p>
                </div>
              ) : (
                <div className="space-y-6">
                  {/* Risk Score Card */}
                  <div className={`rounded-xl border-2 p-6 ${getRiskColor(analysis.risk_level)}`}>
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center gap-3">
                        {getRiskIcon(analysis.risk_level)}
                        <div>
                          <h3 className="text-lg font-bold">Nivel de Riesgo: {analysis.risk_level}</h3>
                          <p className="text-sm opacity-75">Score: {(analysis.risk_score * 100).toFixed(0)}%</p>
                        </div>
                      </div>
                    </div>

                    {/* Diagnosis */}
                    <div className="p-4 bg-white/50 rounded-lg">
                      <p className="font-semibold mb-1">Diagnóstico:</p>
                      <p className="text-sm italic">"{analysis.diagnosis}"</p>
                    </div>
                  </div>

                  {/* Evidence */}
                  {analysis.evidence && analysis.evidence.length > 0 && (
                    <div className="rounded-lg border border-gray-200 bg-white p-6">
                      <h4 className="text-sm font-semibold text-gray-900 mb-3">Evidencia</h4>
                      <ul className="space-y-2">
                        {analysis.evidence.map((ev, idx) => (
                          <li key={idx} className="text-sm text-gray-700 flex items-start gap-2">
                            <span className="text-gray-400 mt-0.5">•</span>
                            <span>{ev}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Intervention */}
                  <div className="rounded-lg border-2 border-blue-200 bg-blue-50 p-6">
                    <h4 className="text-sm font-semibold text-blue-900 mb-3 flex items-center gap-2">
                      💡 Consejo para el Docente
                    </h4>
                    <p className="text-sm text-blue-900 leading-relaxed">{analysis.intervention}</p>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="space-y-4">
              {loading && (
                <div className="flex justify-center py-12">
                  <Spinner size="lg" />
                </div>
              )}

              {!loading && chats.length === 0 && (
                <div className="text-center py-12">
                  <MessageSquare className="h-16 w-16 text-gray-300 mx-auto mb-4" />
                  <p className="text-sm text-gray-500">No hay interacciones con el tutor IA o los mensajes están en formato crudo.</p>
                </div>
              )}

              {!loading && chats.length > 0 && (
                <div className="space-y-4">
                  {/* Raw chat display since structure is simplified */}
                  {chats.map((chat, idx) => (
                    <div key={idx} className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                      {chat.student_message && (
                        <div className="mb-2 text-right">
                          <span className="text-xs text-gray-500 block mb-1">Estudiante</span>
                          <span className="inline-block bg-blue-600 text-white px-3 py-2 rounded-lg rounded-br-none text-sm">{chat.student_message}</span>
                        </div>
                      )}
                      {chat.ai_response && (
                        <div className="text-left">
                          <span className="text-xs text-gray-500 block mb-1">Tutor IA</span>
                          <span className="inline-block bg-white border border-gray-200 text-gray-800 px-3 py-2 rounded-lg rounded-bl-none text-sm">{chat.ai_response}</span>
                        </div>
                      )}
                      <div className="text-xs text-gray-400 mt-2 text-center">
                        {new Date(chat.created_at).toLocaleString()}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
